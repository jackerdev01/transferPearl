#!/usr/bin/env python3
"""Auto-transfer PEARL (PRL) from an Oyster wallet to a fixed address.

PEARL is the native coin of the Pearl L1 (a btcd/btcwallet fork); there is no token
contract. This talks to the Oyster wallet over JSON-RPC (default https://127.0.0.1:44207)
and sends with `sendtoaddress`.

    python pearl_transfer.py                 # loop according to config.json
    python pearl_transfer.py --once          # check / send once
    python pearl_transfer.py --dry-run       # simulate, never broadcast
    python pearl_transfer.py --balance       # show balance only
    python pearl_transfer.py -c other.json --lang vi
"""

import argparse
import base64
import json
import logging
import os
import random
import ssl
import sys
import time
import urllib.error
import urllib.request
from decimal import ROUND_DOWN, Decimal

from i18n import LANGUAGES, set_language, t

HERE = os.path.dirname(os.path.abspath(__file__))
GRAIN = Decimal("0.00000001")  # 1 PRL = 1e8 grain
MIN_RELAY_FEE_RATE = Decimal("0.00001")  # PRL/kB, network minimum relay fee


# ---------- platform paths (match node/btcutil.AppDataDir used by Pearl) ----------

def app_data_dir(app):
    """Data dir of a Pearl app ("oyster", "pearld") on this OS."""
    name = app[:1].upper() + app[1:]
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, name)
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", name)
    return os.path.join(os.path.expanduser("~"), "." + app.lower())


def pearl_bin_dir():
    """Install dir used by Pearl's official install.ps1 / install.sh."""
    if os.name == "nt":
        return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Pearl", "bin")
    return os.environ.get("XDG_BIN_HOME") or os.path.join(os.path.expanduser("~"), ".local", "bin")


OYSTER_DIR = app_data_dir("oyster")
OYSTER_CONF = os.path.join(OYSTER_DIR, "oyster.conf")

DEFAULT_CONFIG = {
    "language": "",
    "rpc_url": "https://127.0.0.1:44207",
    "rpc_user": "",
    "rpc_pass": "",
    "rpc_cert": os.path.join(OYSTER_DIR, "rpc.cert"),
    "tls_verify": True,
    "wallet_passphrase": "",
    "to_address": "",
    "min_transfer": "1",
    "max_transfer": "100",
    "amount_mode": "max",
    "keep_balance": "0",
    "fee_reserve": "0.001",
    "fee_rate": "0.00001",
    "min_conf": 1,
    "interval_seconds": 60,
    "log_file": "pearl_transfer.log",
}

log = logging.getLogger("pearl_transfer")


class RPCError(Exception):
    def __init__(self, code, message):
        super().__init__(f"RPC error {code}: {message}")
        self.code = code
        self.message = message


class OysterRPC:
    """Minimal JSON-RPC client for the Oyster wallet."""

    def __init__(self, url, user, password, cert_path=None, tls_verify=True, timeout=60):
        self.url = url
        self.timeout = timeout
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        self.headers = {"Content-Type": "application/json", "Authorization": f"Basic {token}"}
        self.ssl_ctx = None
        if url.startswith("https://"):
            if not tls_verify:
                self.ssl_ctx = ssl._create_unverified_context()
            elif cert_path and os.path.isfile(cert_path):
                self.ssl_ctx = ssl.create_default_context(cafile=cert_path)
            else:
                self.ssl_ctx = ssl.create_default_context()
        self._id = 0

    def call(self, method, *params):
        self._id += 1
        body = json.dumps({"jsonrpc": "1.0", "id": self._id, "method": method, "params": list(params)})
        req = urllib.request.Request(self.url, data=body.encode(), headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_ctx) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            raw = e.read()
            if e.code == 401:
                raise RPCError(401, t("err_rpc_auth")) from None
            if not raw:
                raise RPCError(e.code, e.reason) from None
        data = json.loads(raw, parse_float=Decimal)
        if data.get("error"):
            err = data["error"]
            raise RPCError(err.get("code"), err.get("message"))
        return data.get("result")


def make_rpc(cfg):
    return OysterRPC(cfg["rpc_url"], cfg["rpc_user"], cfg["rpc_pass"], cfg["rpc_cert"], cfg["tls_verify"])


def read_oyster_conf(path=OYSTER_CONF):
    """Read the RPC username/password from oyster.conf; ("", "") if missing."""
    values = {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                key, sep, value = line.partition("=")
                if sep and not key.strip().startswith(";"):
                    values.setdefault(key.strip(), value.strip())
    except OSError:
        pass
    return values.get("username", ""), values.get("password", "")


def read_raw_config(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def load_config(path):
    cfg = dict(DEFAULT_CONFIG)
    if not os.path.isfile(path):
        sys.exit(t("err_config_missing", path=path))
    cfg.update({k: v for k, v in read_raw_config(path).items() if v != ""})

    if cfg["language"]:
        if cfg["language"] not in LANGUAGES:
            sys.exit(t("err_language", langs=", ".join(LANGUAGES)))
        set_language(cfg["language"])

    # Secrets may come from environment variables instead of the file.
    cfg["rpc_pass"] = os.environ.get("PEARL_RPC_PASS", cfg["rpc_pass"])
    cfg["wallet_passphrase"] = os.environ.get("PEARL_WALLET_PASSPHRASE", cfg["wallet_passphrase"])
    # Empty rpc_user/rpc_pass => use the username/password the Pearl installer wrote to oyster.conf.
    if not cfg["rpc_user"] or not cfg["rpc_pass"]:
        user, password = read_oyster_conf()
        cfg["rpc_user"] = cfg["rpc_user"] or user
        cfg["rpc_pass"] = cfg["rpc_pass"] or password

    if cfg["log_file"] and not os.path.isabs(cfg["log_file"]):
        cfg["log_file"] = os.path.join(os.path.dirname(os.path.abspath(path)), cfg["log_file"])

    for key in ("min_transfer", "max_transfer", "keep_balance", "fee_reserve", "fee_rate"):
        cfg[key] = Decimal(str(cfg[key]))

    if not cfg["to_address"]:
        sys.exit(t("err_to_address"))
    if cfg["min_transfer"] <= 0 or cfg["max_transfer"] < cfg["min_transfer"]:
        sys.exit(t("err_min_max"))
    if cfg["fee_rate"] < MIN_RELAY_FEE_RATE:
        sys.exit(t("err_fee_rate", min=MIN_RELAY_FEE_RATE))
    if cfg["amount_mode"] not in ("max", "random"):
        sys.exit(t("err_amount_mode"))
    return cfg


def looks_like_seed(passphrase):
    return len(passphrase.split()) >= 12


def setup_logging(log_file):
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    log.setLevel(logging.INFO)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(sh)
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        log.addHandler(fh)


def to_grain(amount):
    return amount.quantize(GRAIN, rounding=ROUND_DOWN)


def pick_amount(cfg, available):
    """PRL to send this round, or None if below min_transfer."""
    lo, hi = cfg["min_transfer"], cfg["max_transfer"]
    if available < lo:
        return None
    if cfg["amount_mode"] == "random":
        target = lo + (hi - lo) * Decimal(str(random.random()))
    else:
        target = hi
    amount = to_grain(min(target, available))
    return amount if amount >= lo else None


def ensure_unlocked(rpc, cfg):
    if not rpc.call("walletislocked"):
        return
    if not cfg["wallet_passphrase"]:
        raise RuntimeError(t("err_locked"))
    rpc.call("walletpassphrase", cfg["wallet_passphrase"], 60)


def print_rows(rows):
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        print(f"{label.ljust(width)} : {value}")


def show_balance(rpc, cfg):
    """Print the balance and what the next round would send (sends nothing)."""
    synced = rpc.call("chainsynced")
    confirmed = Decimal(rpc.call("getbalance", "*", cfg["min_conf"]))
    total = Decimal(rpc.call("getbalance", "*", 0))
    unconfirmed = to_grain(total - confirmed) if total != confirmed else Decimal(0)
    available = max(confirmed - cfg["keep_balance"] - cfg["fee_reserve"], Decimal(0))
    lo, hi = cfg["min_transfer"], cfg["max_transfer"]

    print_rows([
        (t("bal_sync"), t("bal_sync_done") if synced else t("bal_sync_not")),
        (t("bal_locked"), t("yes") if rpc.call("walletislocked") else t("no")),
        (t("bal_total"), f"{total} PRL"),
        (t("bal_confirmed", n=cfg["min_conf"]), f"{confirmed} PRL"),
        (t("bal_unconfirmed"), f"{unconfirmed} PRL"),
        (t("bal_reserve"), f"{cfg['keep_balance']} + {cfg['fee_reserve']} PRL"),
        (t("bal_available"), f"{available} PRL"),
        (t("bal_minmax"), f"{lo} / {hi} PRL (mode={cfg['amount_mode']})"),
    ])
    if available < lo:
        print(t("bal_cannot", missing=lo - available))
    elif cfg["amount_mode"] == "random":
        print(t("bal_can_random", lo=lo, hi=to_grain(min(hi, available)), addr=cfg["to_address"]))
    else:
        print(t("bal_can", amount=to_grain(min(hi, available)), addr=cfg["to_address"]))


def available_balance(rpc, cfg):
    """Confirmed PRL that can be sent after keep_balance and fee_reserve."""
    confirmed = Decimal(rpc.call("getbalance", "*", cfg["min_conf"]))
    return max(confirmed - cfg["keep_balance"] - cfg["fee_reserve"], Decimal(0))


def run_once(rpc, cfg, dry_run):
    if not rpc.call("chainsynced"):
        log.info(t("log_not_synced"))
        return None

    balance = Decimal(rpc.call("getbalance", "*", cfg["min_conf"]))
    available = balance - cfg["keep_balance"] - cfg["fee_reserve"]
    amount = pick_amount(cfg, available)
    if amount is None:
        log.info(t("log_below_min", balance=balance, available=max(available, Decimal(0)),
                   min=cfg["min_transfer"]))
        return None

    log.info(t("log_will_send", balance=balance, amount=amount, addr=cfg["to_address"]))
    return send_amount(rpc, cfg, amount, dry_run)


def send_amount(rpc, cfg, amount, dry_run=False):
    """Send exactly `amount` PRL to cfg["to_address"]; returns the txid (None on dry-run)."""
    amount = to_grain(amount)
    if dry_run:
        log.info(t("log_dry_run", amount=amount, addr=cfg["to_address"]))
        return None

    ensure_unlocked(rpc, cfg)
    try:
        txid = rpc.call("sendtoaddress", cfg["to_address"], float(amount), float(cfg["fee_rate"]))
    finally:
        if cfg["wallet_passphrase"]:
            try:
                rpc.call("walletlock")
            except RPCError as e:
                log.warning(t("log_relock_fail", err=e))
    log.info(t("log_sent", amount=amount, txid=txid))
    return txid


def check_destination(rpc, cfg):
    """Validate to_address against the wallet's network; prints and returns False if invalid."""
    info = rpc.call("validateaddress", cfg["to_address"])
    if not info.get("isvalid"):
        print(t("addr_invalid", addr=cfg["to_address"]))
        return False
    if info.get("ismine"):
        print(t("addr_mine"))
    return True


def main():
    parser = argparse.ArgumentParser(description="Auto-transfer PEARL from an Oyster wallet")
    parser.add_argument("-c", "--config", default=os.path.join(HERE, "config.json"))
    parser.add_argument("--once", action="store_true", help="run a single round and exit")
    parser.add_argument("--dry-run", action="store_true", help="never broadcast transactions")
    parser.add_argument("--balance", action="store_true", help="only show the balance")
    parser.add_argument("--lang", choices=sorted(LANGUAGES), help="UI language (overrides config)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    set_language(args.lang)
    if looks_like_seed(cfg["wallet_passphrase"]):
        print(t("warn_seed"))
    rpc = make_rpc(cfg)

    if args.balance:
        try:
            show_balance(rpc, cfg)
        except (RPCError, OSError) as e:
            sys.exit(t("err_connect", url=cfg["rpc_url"], err=e))
        return

    setup_logging(cfg["log_file"])
    try:
        if not check_destination(rpc, cfg):
            sys.exit(1)
    except (RPCError, OSError) as e:
        sys.exit(t("err_connect", url=cfg["rpc_url"], err=e))

    log.info(t("log_start", min=cfg["min_transfer"], max=cfg["max_transfer"], mode=cfg["amount_mode"],
               keep=cfg["keep_balance"], interval=cfg["interval_seconds"],
               dry=" [DRY-RUN]" if args.dry_run else ""))
    while True:
        try:
            run_once(rpc, cfg, args.dry_run)
        except (RPCError, OSError, RuntimeError) as e:
            log.error(t("log_error", err=e))
        if args.once:
            break
        try:
            time.sleep(cfg["interval_seconds"])
        except KeyboardInterrupt:
            break
    log.info(t("log_stopped"))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        pass

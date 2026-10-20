#!/usr/bin/env python3
"""Interactive menu for the PEARL transfer tool (Windows / macOS / Linux).

    python main.py               # open the menu
    python main.py 1             # run option 1 directly (show balance)
    python main.py --lang zh 4   # Chinese UI, start auto transfer
    python main.py -c other.json
"""

import argparse
import datetime
import getpass
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from decimal import Decimal, InvalidOperation

import pearl_transfer as pt
from i18n import LANGUAGES, get_language, set_language, t

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_CONFIG = os.path.join(HERE, "config.example.json")
INSTALLER_URL = {
    "nt": "https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.ps1",
    "posix": "https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.sh",
}
DEFAULT_BIRTHDAY = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)  # before Pearl genesis
YES = ("y", "yes", "c", "co", "có", "s", "shi", "是")
_logging_ready = False


# ---------- helpers ----------

def read(prompt):
    try:
        return input(prompt).replace("﻿", "").strip()
    except EOFError:
        return ""


def ask(prompt, default=None):
    suffix = f" [{default}]" if default not in (None, "") else ""
    value = read(f"{prompt}{suffix}: ")
    return value if value else default


def confirm(prompt):
    return ask(f"{prompt} {t('yn_suffix')}", "n").lower() in YES


def pause():
    read(t("press_enter"))


def ensure_config_file(path):
    if os.path.isfile(path):
        return True
    if not os.path.isfile(EXAMPLE_CONFIG):
        print(t("cfg_no_example", path=path))
        return False
    if confirm(t("cfg_create_q", path=path)):
        raw = pt.read_raw_config(EXAMPLE_CONFIG)
        raw["language"] = get_language()
        write_config(path, raw)
        print(t("cfg_created", path=path))
        return True
    return False


def write_config(path, raw):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load(path):
    """Load config + build the RPC client; returns (cfg, rpc) or (None, None)."""
    if not ensure_config_file(path):
        return None, None
    try:
        cfg = pt.load_config(path)
    except SystemExit as e:
        print(t("cfg_error", err=e))
        return None, None
    if pt.looks_like_seed(cfg["wallet_passphrase"]):
        print(t("warn_seed"))
    return cfg, pt.make_rpc(cfg)


def init_logging(cfg):
    global _logging_ready
    if not _logging_ready:
        pt.setup_logging(cfg["log_file"])
        _logging_ready = True


def find_bin(name):
    found = shutil.which(name)
    if found:
        return found
    exe = name + (".exe" if os.name == "nt" else "")
    candidate = os.path.join(pt.pearl_bin_dir(), exe)
    return candidate if os.path.isfile(candidate) else None


def is_running(name):
    try:
        if os.name == "nt":
            out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}.exe", "/NH"],
                                 capture_output=True, text=True).stdout
            return f"{name}.exe".lower() in out.lower()
        return subprocess.run(["pgrep", "-x", name], capture_output=True).returncode == 0
    except OSError:
        return False


# ---------- menu options ----------

def opt_balance(path):
    cfg, rpc = load(path)
    if cfg:
        pt.show_balance(rpc, cfg)


def opt_transfer_once(path, dry_run):
    cfg, rpc = load(path)
    if not cfg or not pt.check_destination(rpc, cfg):
        return
    pt.show_balance(rpc, cfg)
    available = pt.available_balance(rpc, cfg)

    print(t("amount_help"))
    raw = (ask(t("amount_label"), "") or "").lower()
    if raw == "":
        amount = pt.pick_amount(cfg, available)
        if amount is None:
            print(t("below_min"))
            return
    elif raw in ("all", "het", "hết", "全部"):
        amount = pt.to_grain(available)
    else:
        try:
            amount = pt.to_grain(Decimal(raw.replace(",", ".")))
        except InvalidOperation:
            print(t("invalid_number", raw=raw))
            return
    if amount <= 0:
        print(t("amount_positive"))
        return
    if amount > available:
        print(t("amount_exceeds", available=available))
        return

    print(t("will_send", amount=amount, addr=cfg["to_address"], fee=cfg["fee_rate"]))
    if not dry_run and not confirm(t("confirm_real")):
        print(t("cancelled"))
        return
    init_logging(cfg)
    pt.send_amount(rpc, cfg, amount, dry_run)


def opt_auto(path):
    cfg, rpc = load(path)
    if not cfg or not pt.check_destination(rpc, cfg):
        return
    print(t("auto_summary", min=cfg["min_transfer"], max=cfg["max_transfer"], mode=cfg["amount_mode"],
            interval=cfg["interval_seconds"], addr=cfg["to_address"]))
    dry_run = not confirm(t("auto_confirm"))
    init_logging(cfg)
    print(t("auto_running"))
    try:
        while True:
            try:
                pt.run_once(rpc, cfg, dry_run)
            except (pt.RPCError, OSError, RuntimeError) as e:
                pt.log.error(t("log_error", err=e))
            time.sleep(cfg["interval_seconds"])
    except KeyboardInterrupt:
        print(t("auto_stopped"))


def opt_show_config(path):
    if not ensure_config_file(path):
        return
    for key, value in pt.read_raw_config(path).items():
        if key in SECRET_KEYS and value:
            value = "***"
        print(f"  {key:18}: {value}")


EDITABLE = [
    ("to_address", str), ("min_transfer", Decimal), ("max_transfer", Decimal), ("amount_mode", str),
    ("keep_balance", Decimal), ("fee_reserve", Decimal), ("fee_rate", Decimal),
    ("interval_seconds", int), ("min_conf", int), ("rpc_url", str), ("rpc_user", str),
    ("rpc_pass", str), ("wallet_passphrase", str),
]
SECRET_KEYS = {"rpc_pass", "wallet_passphrase"}


def opt_edit_config(path):
    if not ensure_config_file(path):
        return
    raw = pt.read_raw_config(path)
    print(t("edit_hint"))
    for key, typ in EDITABLE:
        current = raw.get(key, pt.DEFAULT_CONFIG.get(key, ""))
        shown = "***" if key in SECRET_KEYS and current else current
        value = ask(f"{t('f_' + key)} ({key})", shown)
        if value in (None, shown):
            continue
        try:
            typ(value)
        except (ValueError, InvalidOperation):
            print(t("edit_skip", value=value, key=key))
            continue
        raw[key] = int(value) if typ is int else value
    write_config(path, raw)
    print(t("edit_saved", path=path))
    try:
        pt.load_config(path)
        print(t("cfg_valid"))
    except SystemExit as e:
        print(t("cfg_invalid", err=e))


def opt_check_connection(path):
    cfg, rpc = load(path)
    if not cfg:
        return
    print(f"RPC: {cfg['rpc_url']}")
    info = rpc.call("getinfo")
    print(t("conn_ok", blocks=info.get("blocks"), peers=info.get("connections")))
    yn = lambda v: t("yes") if v else t("no")  # noqa: E731
    print(t("conn_synced", yn=yn(rpc.call("chainsynced"))))
    locked = rpc.call("walletislocked")
    print(t("conn_locked", yn=yn(locked)))
    if pt.check_destination(rpc, cfg):
        print(t("conn_addr_ok", addr=cfg["to_address"]))
    if cfg["wallet_passphrase"] and locked:
        try:
            rpc.call("walletpassphrase", cfg["wallet_passphrase"], 1)
            rpc.call("walletlock")
            print(t("pass_ok"))
        except pt.RPCError as e:
            print(t("pass_bad", err=e.message))


def opt_new_address(path):
    cfg, rpc = load(path)
    if cfg:
        print(t("new_address", addr=rpc.call("getnewaddress")))


def opt_install(_path):
    url = INSTALLER_URL["nt" if os.name == "nt" else "posix"]
    print(t("install_will", url=url))
    if not confirm(t("continue_q")):
        return
    tmpdir = tempfile.mkdtemp(prefix="pearl-install-")
    try:
        script = os.path.join(tmpdir, os.path.basename(url))
        urllib.request.urlretrieve(url, script)
        if os.name == "nt":
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script]
        else:
            cmd = ["sh", script]
        code = subprocess.run(cmd).returncode
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    print(t("install_done") if code == 0 else t("install_failed", code=code))


def opt_import_wallet(_path):
    exe = find_bin("oyster")
    if not exe:
        print(t("oyster_missing"))
        return
    if is_running("oyster"):
        print(t("import_stop_first"))
        return
    db_path = os.path.join(pt.OYSTER_DIR, "mainnet", "wallet.db")
    if os.path.exists(db_path):
        print(t("import_exists", path=db_path))
        return

    seed = " ".join(getpass.getpass(t("import_seed")).lower().split())
    words = len(seed.split())
    if words not in (12, 15, 18, 21, 24):
        print(t("import_seed_words", n=words))
        return
    password = getpass.getpass(t("import_pass1"))
    if not password:
        print(t("import_pass_empty"))
        return
    if password != getpass.getpass(t("import_pass2")):
        print(t("import_pass_mismatch"))
        return
    birthday = DEFAULT_BIRTHDAY
    raw_bday = ask(t("import_bday"), "")
    if raw_bday:
        try:
            birthday = datetime.datetime.strptime(raw_bday, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            print(t("import_bday_bad"))
            return

    # oyster --createfromfile only accepts a file: keep it private (0600) and delete it right away.
    fd, setup = tempfile.mkstemp(prefix="oyster-import-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"PrivatePassphrase": password, "Seed": seed,
                       "Bday": str(int(birthday.timestamp()))}, f)
        print(t("import_running"))
        # oyster prints the seed on success, so its output is captured and never shown.
        result = subprocess.run([exe, f"--createfromfile={setup}"], capture_output=True, text=True)
    finally:
        os.remove(setup)
    if result.returncode != 0:
        detail = "\n".join(line for line in (result.stderr or "").splitlines() if seed not in line)
        print(t("import_failed", code=result.returncode, detail=detail.strip()))
        return
    print(t("import_ok", path=db_path))


def opt_start_oyster(path):
    # The Pearl installer sets usespv=1, so oyster syncs on its own (pearld is not needed).
    if is_running("oyster"):
        print(t("oyster_running"))
    else:
        exe = find_bin("oyster")
        if not exe:
            print(t("oyster_missing"))
            return
        if os.name == "nt":
            subprocess.Popen([exe], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        print(t("oyster_started", exe=exe))
    wait_synced(path)


def wait_synced(path):
    cfg, rpc = load(path)
    if not cfg:
        return
    print(t("wait_sync"))
    try:
        while True:
            try:
                p = rpc.call("getsyncprogress")
                if p.get("synced"):
                    print(t("sync_done", height=p["block_height"]))
                    return
                print("\r" + t("sync_progress", block=p["block_height"], best=p["best_peer_height"],
                               hdr=p["header_height"], peers=p["connections"]), end="", flush=True)
            except (pt.RPCError, OSError):
                print("\r" + t("oyster_starting"), end="", flush=True)
            time.sleep(5)
    except KeyboardInterrupt:
        print(t("wait_skipped"))


def opt_stop_oyster(path):
    if not is_running("oyster"):
        print(t("stop_not_running"))
        return
    cfg, rpc = load(path)
    if cfg:
        rpc.call("stop")
        print(t("stop_ok"))


def opt_language(path):
    codes = list(LANGUAGES)
    for i, code in enumerate(codes, 1):
        print(f"  {i}. {LANGUAGES[code]}")
    choice = ask(t("lang_prompt"), str(codes.index(get_language()) + 1))
    if not (choice or "").isdigit() or not 1 <= int(choice) <= len(codes):
        print(t("menu_invalid"))
        return
    set_language(codes[int(choice) - 1])
    if os.path.isfile(path):
        raw = pt.read_raw_config(path)
        raw["language"] = get_language()
        write_config(path, raw)
    print(t("lang_set", lang=LANGUAGES[get_language()]))


MENU = [
    ("1", opt_balance),
    ("2", lambda p: opt_transfer_once(p, False)),
    ("3", lambda p: opt_transfer_once(p, True)),
    ("4", opt_auto),
    ("5", opt_show_config),
    ("6", opt_edit_config),
    ("7", opt_check_connection),
    ("8", opt_new_address),
    ("9", opt_install),
    ("10", opt_import_wallet),
    ("11", opt_start_oyster),
    ("12", opt_stop_oyster),
    ("13", opt_language),
    ("0", None),
]


def run_option(choice, path):
    for key, func in MENU:
        if key == choice:
            if func is None:
                sys.exit(0)
            try:
                func(path)
            except pt.RPCError as e:
                print(t("wallet_error", err=e))
            except OSError as e:
                print(t("conn_error_hint", err=e))
            return True
    print(t("menu_invalid"))
    return False


def main():
    parser = argparse.ArgumentParser(description="PEARL transfer tool menu")
    parser.add_argument("-c", "--config", default=os.path.join(HERE, "config.json"))
    parser.add_argument("--lang", choices=sorted(LANGUAGES), help="UI language (en/vi/zh)")
    parser.add_argument("choice", nargs="?", help="menu option to run directly")
    args = parser.parse_args()

    configured = ""
    if os.path.isfile(args.config):
        try:
            configured = pt.read_raw_config(args.config).get("language", "")
        except (OSError, ValueError):
            pass
    set_language(args.lang or configured)

    if args.choice:
        run_option(args.choice, args.config)
        return

    if not (args.lang or configured or os.environ.get("PEARL_LANG")):
        opt_language(args.config)  # first run: let the user pick a language

    while True:
        print(f"\n========== {t('menu_title')} ==========")
        print(t("menu_config", path=args.config))
        for key, _ in MENU:
            print(f" {key:>2}. {t('m' + key)}")
        choice = read(t("menu_choose"))
        if run_option(choice, args.config) and choice != "0":
            pause()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        print()

# PEARL Auto Transfer

**English** · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md)

A small, dependency-free tool that automatically sends **PEARL (PRL)** from your own
[Oyster](https://github.com/pearl-research-labs/pearl) wallet to a fixed address, with a
minimum / maximum amount per transfer. It runs on **Windows, macOS and Linux** and has an
interactive menu in **English, Tiếng Việt and 简体中文**.

> **Non-custodial.** Your seed and coins stay on your own computer. The tool only talks to the
> Oyster wallet running locally (`127.0.0.1`). It never sends your seed, password or keys anywhere.

---

## Contents

1. [How it works](#how-it-works)
2. [Requirements](#requirements)
3. [Quick start](#quick-start)
4. [Full setup, step by step](#full-setup-step-by-step)
5. [Daily use](#daily-use)
6. [Menu reference](#menu-reference)
7. [Configuration reference](#configuration-reference)
8. [Command-line mode](#command-line-mode)
9. [Start automatically at login](#start-automatically-at-login)
10. [Fees](#fees)
11. [Security notes — read this](#security-notes--read-this)
12. [Troubleshooting](#troubleshooting)
13. [Where files live](#where-files-live)
14. [FAQ](#faq)
15. [Disclaimer and license](#disclaimer-and-license)

---

## How it works

```
 this tool ──JSON-RPC (localhost:44207)──▶ oyster (your wallet) ──SPV──▶ Pearl network
```

- PEARL is the **native coin** of the Pearl Layer-1 blockchain. There is no token contract, so
  sending PRL means asking your own wallet, **Oyster**, to build and broadcast a transaction.
- Oyster runs in **SPV (light) mode**: it syncs block headers and filters from the network on its
  own. You do **not** need to run a full node (`pearld`).
- Every `interval_seconds` the tool checks your confirmed balance. When the amount you can send
  (balance − `keep_balance` − `fee_reserve`) reaches `min_transfer`, it sends up to
  `max_transfer` PRL to `to_address`.

**Features**

- Automatic transfers with min / max limits, a fixed or random amount, and a balance to keep.
- Manual one-off transfer where you type the amount (`all` = send everything available).
- Dry-run mode to see what would be sent without broadcasting anything.
- Balance view, connection + password check, receiving address.
- Installs Pearl, imports a wallet from its seed, starts / stops Oyster, and shows sync progress.
- English / Vietnamese / Chinese interface. Only the Python standard library is used.

## Requirements

| | |
|---|---|
| OS | Windows 10/11, macOS (Intel or Apple Silicon), Linux x86_64 / arm64 |
| Python | **3.8 or newer** ([python.org](https://www.python.org/downloads/)) |
| Pearl wallet | `oyster` from the official [Pearl releases](https://github.com/pearl-research-labs/pearl/releases), installed by menu option 9 |
| Network | Internet connection; the first wallet sync downloads all block headers |
| Disk | A few hundred MB for the wallet's header and filter data |

## Quick start

```bash
git clone https://github.com/jackerdev01/transferPearl.git
cd transferPearl
python main.py          # macOS / Linux: python3 main.py
```

Then, in the menu: **9** install Pearl → **10** import wallet → **11** start Oyster and wait for
sync → **6** edit config → **7** check → **3** dry-run → **2** small real transfer → **4** auto
transfer.

The rest of this page explains each step.

## Full setup, step by step

### 1. Install Python 3

- **Windows:** install from [python.org](https://www.python.org/downloads/windows/) and tick
  **"Add python.exe to PATH"**. Check with `py -3 --version` or `python --version`.
- **macOS:** install from [python.org](https://www.python.org/downloads/macos/) or with
  Homebrew (`brew install python`). Check with `python3 --version`.
- **Linux:** usually already installed. Otherwise use your package manager, for example
  `sudo apt install python3` (Debian/Ubuntu) or `sudo dnf install python3` (Fedora).

### 2. Download the tool

Either `git clone https://github.com/jackerdev01/transferPearl.git`, or on GitHub click
**Code → Download ZIP** and extract it. Open a terminal in that folder:

- **Windows:** open the folder in Explorer, click the address bar, type `cmd` and press Enter.
  You can also use PowerShell or Windows Terminal.
- **macOS:** Terminal, then `cd ~/Downloads/transferPearl` (adjust the path).
- **Linux:** your terminal, then `cd` into the folder.

In the commands below, Windows users type `python` (or `py -3`) and macOS / Linux users type
`python3`.

### 3. Install Pearl (Oyster wallet)

Run `python main.py`, pick your language, then choose **9**. The tool downloads the **official**
installer from the `pearl-research-labs/pearl` GitHub repository and runs it:

| OS | Installer used | Binaries go to |
|---|---|---|
| Windows | `install.ps1` | `%LOCALAPPDATA%\Pearl\bin` |
| macOS / Linux | `install.sh` | `~/.local/bin` (or `$XDG_BIN_HOME`) |

The installer also writes `oyster.conf` with a random RPC username and password, and turns on SPV
mode (`usespv=1`). The tool reads these credentials automatically.

**Open a new terminal afterwards** so that `oyster` is on your `PATH`.

If you prefer to install by hand, these are the official commands:

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.ps1 | iex
```
```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.sh | sh
```

> Linux: if `oyster` is "not found" after installing, add `~/.local/bin` to your `PATH`
> (`echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`, then open a new terminal).

### 4. Import your wallet

Choose **10 – Import wallet from seed**:

1. Type your 12- or 24-word **seed**. It is not shown while you type.
2. Choose a **wallet password** (the "private passphrase"). It encrypts the keys on disk and is
   required for every transfer. **Write it down; it cannot be recovered.**
3. Optionally enter the **date of the wallet's first transaction** (`YYYY-MM-DD`). You can find
   it on an explorer such as [prlscan.com](https://prlscan.com). Leave it empty to scan the whole
   chain, which is safe but slower.

The seed is passed to `oyster --createfromfile` through a private temporary file that is deleted
right away. It is never written to `config.json`.

Notes:
- Oyster must be **stopped** while importing (menu 12).
- Oyster keeps **one wallet per network**. If `wallet.db` already exists, the import refuses to
  overwrite it. See [Where files live](#where-files-live).
- No wallet yet? Run `oystercli` and choose *"Generate a new recovery seed"*, then continue with
  step 5.

### 5. Start Oyster and wait for the first sync

Choose **11**. Oyster starts (on Windows in its own window; on macOS / Linux in the background)
and the tool shows progress until the wallet is synced:

```
  block 0/130552 (headers 58300, peers 8)
```

- The **first sync** downloads all headers and filters, then rescans the chain for your
  transactions. In one test on a home PC (about 130,000 blocks, October 2026) this took roughly
  30–60 minutes. Later starts only catch up on new blocks: seconds to a few minutes.
- Your balance is only correct after the sync has finished.
- You can press Ctrl+C to stop waiting; Oyster keeps running.

### 6. Configure

Choose **6** and answer the questions (press Enter to keep a value). At minimum, set:

- `to_address`: where PRL should be sent. **Double-check it.** Transactions cannot be reversed.
- `min_transfer` / `max_transfer`
- `wallet_passphrase`: the wallet password from step 4. **Not the seed.**

The menu creates `config.json` from `config.example.json` the first time.
`config.json` is personal and listed in `.gitignore`. See the
[Configuration reference](#configuration-reference) for every field.

### 7. Check, test, then go

1. **7 – Check wallet connection + password**: RPC connection, sync state, destination address
   and wallet password.
2. **3 – Dry-run**: enter a small amount such as `0.1`; nothing is broadcast.
3. **2 – Send once**: send a small real amount, confirm with `y`, then look up the `txid` on
   [prlscan.com](https://prlscan.com).
4. **4 – Auto transfer**: answer `y` to run for real. Leave the window open; press Ctrl+C to stop.

## Daily use

After a reboot, everything you set up is still there. Just start the tool:

| OS | Do this |
|---|---|
| Windows | double-click **`start.bat`** |
| macOS | double-click **`start.command`** (first time: right-click → Open) |
| Linux | `./start.sh` |

The start script starts Oyster if needed, waits for the sync, and then opens the menu. Choose
**4** for automatic transfers.

Before shutting down, press Ctrl+C in the tool, then choose **12 – Stop Oyster** (or press
Ctrl+C in Oyster's window on Windows).

## Menu reference

| # | Option | What it does |
|---|---|---|
| 1 | Show balance | Sync state, balances, what the next round would send. Sends nothing. |
| 2 | Send once | Type an amount (`12.5`, `all`, or Enter for auto); asks `y/N` before sending. |
| 3 | Dry-run once | Same as 2 but never broadcasts. |
| 4 | Auto transfer | Loops every `interval_seconds`; asks real vs dry-run first. Ctrl+C stops. |
| 5 | Show config | Prints `config.json` with passwords hidden. |
| 6 | Edit config | Asks for each field and validates the result. |
| 7 | Check connection | RPC, block height, peers, sync, address and password check. |
| 8 | Receiving address | Shows a new address of your wallet (to receive PRL into it). |
| 9 | Install Pearl | Downloads and runs the official Pearl installer for your OS. |
| 10 | Import wallet | Restores the wallet from its seed (see step 4). |
| 11 | Start Oyster | Starts the wallet if needed and waits for the sync. |
| 12 | Stop Oyster | Shuts the wallet down cleanly. |
| 13 | Language | English / Tiếng Việt / 简体中文 (saved in `config.json`). |
| 0 | Exit | |

Run an option directly with `python main.py <number>`, for example `python main.py 1`.

## Configuration reference

`config.json` (copied from `config.example.json`):

| Key | Default | Meaning |
|---|---|---|
| `language` | `en` | `en`, `vi` or `zh`. Can also be set with `--lang` or `PEARL_LANG`. |
| `rpc_url` | `https://127.0.0.1:44207` | Oyster RPC. Mainnet wallet port is 44207 (testnet 44209). |
| `rpc_user` / `rpc_pass` | empty | Empty = read `username` / `password` from `oyster.conf`. |
| `rpc_cert` | empty | Oyster TLS certificate. Empty = `rpc.cert` in Oyster's data folder. |
| `tls_verify` | `true` | Set `false` only if the certificate cannot be verified (localhost only). |
| `wallet_passphrase` | empty | **Wallet password, not the seed.** Can come from `PEARL_WALLET_PASSPHRASE`. |
| `to_address` | — | Destination address (`prl1…`). |
| `min_transfer` | `1` | Only send when at least this much PRL is available. |
| `max_transfer` | `100` | Never send more than this per transfer. |
| `amount_mode` | `max` | `max`: send min(available, max). `random`: a random amount in [min, max], capped by what is available. |
| `keep_balance` | `0` | PRL that always stays in the wallet. |
| `fee_reserve` | `0.001` | PRL kept aside for network fees. |
| `fee_rate` | `0.00001` | Fee in PRL per kB. `0.00001` is the network minimum. |
| `min_conf` | `1` | Only count coins with at least this many confirmations. |
| `interval_seconds` | `60` | How often the auto transfer checks the balance. |
| `log_file` | `pearl_transfer.log` | Log file next to the config. Empty disables file logging. |

**Available to send** = confirmed balance − `keep_balance` − `fee_reserve`.

Environment variables override the file: `PEARL_WALLET_PASSPHRASE`, `PEARL_RPC_PASS`, `PEARL_LANG`.

## Command-line mode

`pearl_transfer.py` runs without menus. This is useful for servers and services:

```bash
python pearl_transfer.py --balance          # show balance and exit
python pearl_transfer.py --dry-run --once   # one simulated round
python pearl_transfer.py                    # auto transfer loop (real)
python pearl_transfer.py -c other.json --lang zh
```

## Start automatically at login

Oyster must be running before transfers can happen. The start scripts handle that for you.

- **Windows:** press Win+R, type `shell:startup` and press Enter. Put a **shortcut** to
  `start.bat` in that folder.
- **macOS:** System Settings → General → **Login Items** → add `start.command`.
- **Linux (systemd, user services):** create the two files below, then run
  `systemctl --user enable --now oyster pearl-transfer`. Use a non-interactive setup:
  `config.json` with `wallet_passphrase` (or the environment variable) and a tested `to_address`.

```ini
# ~/.config/systemd/user/oyster.service
[Unit]
Description=Pearl Oyster wallet
[Service]
ExecStart=%h/.local/bin/oyster
Restart=on-failure
[Install]
WantedBy=default.target
```
```ini
# ~/.config/systemd/user/pearl-transfer.service
[Unit]
Description=PEARL auto transfer
After=oyster.service
Requires=oyster.service
[Service]
WorkingDirectory=%h/transferPearl
ExecStart=/usr/bin/python3 pearl_transfer.py
Restart=on-failure
RestartSec=30
[Install]
WantedBy=default.target
```

## Fees

- The tool pays the network fee set by `fee_rate`. The default `0.00001` PRL/kB is the network
  minimum (about 1 grain per virtual byte). A typical transfer costs around **0.000003 PRL**.
- A transaction that spends many small inputs (for example many mining payouts) is larger, so
  its fee is a little higher. The fee does **not** depend on the amount sent.
- The fee is paid **on top of** the amount. `fee_reserve` keeps enough PRL aside for it.
- The tool charges no fee of its own. Some web wallets add a service fee to every transfer;
  this tool does not.

## Security notes — read this

1. **Never put your seed in `config.json`** or anywhere else in this folder. The seed is only
   typed once, into menu option 10. `wallet_passphrase` is the wallet **password**. The tool
   warns you if it looks like a seed.
2. **Anyone with your seed owns your coins.** Keep it offline. If you think it has leaked
   (pasted into a chat, a file, a screenshot, a cloud drive), create a new wallet and move your
   funds there, and point your mining payouts to the new address.
3. `config.json` holds your wallet password. It is git-ignored; **never commit or share it**. On
   macOS / Linux, restrict it with `chmod 600 config.json`. Alternatively, leave
   `wallet_passphrase` empty and set the `PEARL_WALLET_PASSPHRASE` environment variable.
4. Oyster's RPC only listens on `127.0.0.1`. **Do not expose port 44207** to the internet or your
   LAN.
5. **Check `to_address` carefully.** Blockchain transfers are final. Always do a dry-run and a
   small real transfer first.
6. The tool unlocks the wallet only for the moment it sends, and then locks it again.
7. Keep `wallet.db` and your seed backed up. Losing `wallet.db` alone is fine: you can import the
   seed again.
8. Only download this tool and Pearl from their official GitHub repositories.

## Troubleshooting

| Problem | Fix |
|---|---|
| `RPC error 401: wrong rpc_user/rpc_pass` | Leave `rpc_user` / `rpc_pass` empty so they are read from `oyster.conf`, or copy `username=` / `password=` from it. |
| `Cannot connect to the Oyster wallet` / connection refused | Oyster is not running: use menu 11. Check `rpc_url` (port 44207 on mainnet). |
| `oyster was not found` | Install with menu 9, then open a **new** terminal. On Linux, add `~/.local/bin` to `PATH`. |
| Sync seems stuck on an old date | The chain started on 2026-04-27, so early dates are normal at the start. Check menu 11 / 1. The first sync can take up to an hour. |
| Balance is 0 after import | Wait until the sync shows *done*, then compare with the balance of your address on [prlscan.com](https://prlscan.com). If it still differs, the seed was probably mistyped: stop Oyster, rename `wallet.db` and import again. |
| `The wallet is locked and wallet_passphrase … is not set` | Set `wallet_passphrase` (menu 6) or `PEARL_WALLET_PASSPHRASE`. |
| `Wallet password is WRONG` | Use the password chosen during import, not the seed. |
| `A wallet already exists at …` | Oyster holds one wallet per network. Stop Oyster, back up / rename `wallet.db`, then import again. |
| `Destination address is not valid` | The address is mistyped or for another network (mainnet addresses start with `prl1`). |
| Import says to stop Oyster first | Use menu 12, then menu 10. |
| Seed input does not work on Windows | Run the tool from `cmd`, PowerShell or Windows Terminal, not Git Bash / mintty. |
| macOS: "start.command cannot be opened" | Right-click → Open once, or run `chmod +x start.command start.sh`. |
| Garbled characters on Windows | Use `start.bat` (sets UTF-8), or run `chcp 65001` first. |
| `fee_rate must be >= 0.00001` | Transactions below the network minimum are rejected; keep the default. |

## Where files live

| | Windows | macOS | Linux |
|---|---|---|---|
| Oyster data (`oyster.conf`, `rpc.cert`, `mainnet/wallet.db`) | `%LOCALAPPDATA%\Oyster` | `~/Library/Application Support/Oyster` | `~/.oyster` |
| Oyster logs | `…\Oyster\logs\mainnet\oyster.log` | `…/Oyster/logs/mainnet/oyster.log` | `~/.oyster/logs/mainnet/oyster.log` |
| Pearl binaries | `%LOCALAPPDATA%\Pearl\bin` | `~/.local/bin` | `~/.local/bin` |
| This tool's config and log | the tool's folder (`config.json`, `pearl_transfer.log`) | same | same |

## FAQ

**Do I need `pearld` (the full node)?** No. Oyster syncs by itself in SPV mode. `pearld` uses a
lot of CPU and is not needed for this tool.

**If I turn the computer off, does it sync from scratch again?** No. Headers, filters and wallet
state are stored on disk. Oyster continues from where it stopped.

**Can I use several wallets?** Oyster keeps one wallet per network and data folder. Run one copy
of the tool per wallet, each with its own Oyster `--appdata` folder, port and `config.json`.

**Can I run it on a server for other people?** Then the server would hold other people's seeds,
which is a large security and legal risk. This tool is meant for each person to run on their own
machine.

## Disclaimer and license

This is an unofficial community tool. It is not affiliated with Pearl Research Labs. It is
provided **as is, without warranty of any kind**. You are responsible for your wallet, your seed
and every transaction you send. Test with small amounts first.

Released under the [MIT License](LICENSE).

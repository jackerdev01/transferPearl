# PEARL Auto Transfer

[English](README.md) · [Tiếng Việt](README.vi.md) · **简体中文**

一个无需安装第三方依赖的小工具：自动把您自己的 [Oyster](https://github.com/pearl-research-labs/pearl)
钱包中的 **PEARL (PRL)** 转到固定地址，并可设置每次转账的最小 / 最大金额。支持
**Windows、macOS 和 Linux**，交互菜单提供 **English、Tiếng Việt 和 简体中文**。

> **非托管。** 助记词和资金始终留在您自己的电脑上。本工具只与本机运行的 Oyster 钱包
> （`127.0.0.1`）通信，绝不会把助记词、密码或私钥发送到任何地方。

---

## 目录

1. [工作原理](#工作原理)
2. [环境要求](#环境要求)
3. [快速开始](#快速开始)
4. [详细安装步骤](#详细安装步骤)
5. [日常使用](#日常使用)
6. [菜单说明](#菜单说明)
7. [配置说明](#配置说明)
8. [命令行模式](#命令行模式)
9. [开机自动运行](#开机自动运行)
10. [手续费](#手续费)
11. [安全须知（务必阅读）](#安全须知务必阅读)
12. [常见问题排查](#常见问题排查)
13. [文件位置](#文件位置)
14. [FAQ](#faq)
15. [免责声明与许可证](#免责声明与许可证)

---

## 工作原理

```
 本工具 ──JSON-RPC (localhost:44207)──▶ oyster（您的钱包）──SPV──▶ Pearl 网络
```

- PEARL 是 Pearl 一层区块链的**原生币**，没有代币合约。转账 PRL 需要由您自己的钱包
  **Oyster** 构建并广播交易。
- Oyster 以 **SPV（轻节点）模式**运行：它自己从网络同步区块头和过滤器。您**不需要**运行全节点
  （`pearld`）。
- 每隔 `interval_seconds` 秒，工具检查一次已确认余额。当可转金额（余额 − `keep_balance` −
  `fee_reserve`）达到 `min_transfer` 时，向 `to_address` 转出最多 `max_transfer` PRL。

**功能**

- 按 min / max 自动转账，可选固定或随机金额，并可保留部分余额。
- 手动单次转账，自行输入数量（`all` = 转出全部可用余额）。
- 模拟运行（dry-run）：查看将转多少，但不广播任何交易。
- 查看余额、检查连接和密码、获取收款地址。
- 安装 Pearl、通过助记词导入钱包、启动 / 停止 Oyster、显示同步进度。
- 英文 / 越南文 / 中文界面。只使用 Python 标准库。

## 环境要求

| | |
|---|---|
| 操作系统 | Windows 10/11、macOS（Intel 或 Apple Silicon）、Linux x86_64 / arm64 |
| Python | **3.8 或更高版本**（[python.org](https://www.python.org/downloads/)） |
| Pearl 钱包 | 来自 [Pearl 官方发布](https://github.com/pearl-research-labs/pearl/releases) 的 `oyster`，可用菜单 9 安装 |
| 网络 | 需要联网；首次同步会下载全部区块头 |
| 磁盘 | 钱包的区块头和过滤器数据约占几百 MB |

## 快速开始

```bash
git clone https://github.com/jackerdev01/transferPearl.git
cd transferPearl
python main.py          # macOS / Linux：python3 main.py
```

然后在菜单中依次选择：**9** 安装 Pearl → **10** 导入钱包 → **11** 启动 Oyster 并等待同步 →
**6** 编辑配置 → **7** 检查 → **3** 模拟运行 → **2** 小额真实转账 → **4** 自动转账。

下面逐步说明。

## 详细安装步骤

### 1. 安装 Python 3

- **Windows：** 从 [python.org](https://www.python.org/downloads/windows/) 安装，并勾选
  **“Add python.exe to PATH”**。用 `py -3 --version` 或 `python --version` 检查。
- **macOS：** 从 [python.org](https://www.python.org/downloads/macos/) 安装，或用 Homebrew
  （`brew install python`）。用 `python3 --version` 检查。
- **Linux：** 通常已自带。否则用包管理器安装，例如 `sudo apt install python3`（Debian/Ubuntu）
  或 `sudo dnf install python3`（Fedora）。

### 2. 下载本工具

执行 `git clone https://github.com/jackerdev01/transferPearl.git`，或在 GitHub 页面点击
**Code → Download ZIP** 并解压。然后在该文件夹中打开终端：

- **Windows：** 在资源管理器中打开该文件夹，点击地址栏，输入 `cmd` 后回车。也可以使用
  PowerShell 或 Windows Terminal。
- **macOS：** 打开“终端”，执行 `cd ~/Downloads/transferPearl`（按实际路径修改）。
- **Linux：** 打开终端并 `cd` 到该文件夹。

以下命令中，Windows 用户输入 `python`（或 `py -3`），macOS / Linux 用户输入 `python3`。

### 3. 安装 Pearl（Oyster 钱包）

运行 `python main.py`，选择语言，然后选 **9**。工具会从 GitHub 仓库
`pearl-research-labs/pearl` 下载**官方**安装脚本并运行：

| 操作系统 | 安装脚本 | 安装位置 |
|---|---|---|
| Windows | `install.ps1` | `%LOCALAPPDATA%\Pearl\bin` |
| macOS / Linux | `install.sh` | `~/.local/bin`（或 `$XDG_BIN_HOME`） |

安装脚本还会生成 `oyster.conf`（包含随机的 RPC 用户名和密码），并开启 SPV 模式
（`usespv=1`）。本工具会自动读取这些凭据。

**安装完成后请打开一个新的终端窗口**，使 `oyster` 出现在 `PATH` 中。

如果想手动安装，官方命令如下：

```powershell
# Windows（PowerShell）
irm https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.ps1 | iex
```
```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.sh | sh
```

> Linux：如果安装后提示找不到 `oyster`，请把 `~/.local/bin` 加入 `PATH`
> （`echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`，然后打开新终端）。

### 4. 导入钱包

选择 **10 – 通过助记词导入钱包**：

1. 输入 12 或 24 个单词的**助记词**。输入时不会显示。
2. 设置**钱包密码**（private passphrase）。它用于加密磁盘上的私钥，每次转账都需要。
   **请务必记下，丢失后无法找回。**
3. 可选：输入钱包**首笔交易的日期**（`YYYY-MM-DD`），可在 [prlscan.com](https://prlscan.com)
   等浏览器上查到。留空则扫描整条链：安全，但更慢。

助记词通过一个私有临时文件传给 `oyster --createfromfile`，该文件随后立即删除。助记词绝不会
写入 `config.json`。

注意：
- 导入时 Oyster 必须**处于停止状态**（菜单 12）。
- Oyster 每个网络只保存**一个钱包**。如果 `wallet.db` 已存在，工具会拒绝覆盖。参见
  [文件位置](#文件位置)。
- 还没有钱包？运行 `oystercli`，选择 *“Generate a new recovery seed”*，然后继续第 5 步。

### 5. 启动 Oyster 并等待首次同步

选择 **11**。Oyster 会启动（Windows 上在独立窗口中运行；macOS / Linux 上在后台运行），
工具会显示进度直到钱包同步完成：

```
  区块 0/130552（区块头 58300，节点 8）
```

- **首次同步**会下载全部区块头和过滤器，然后重新扫描链以查找您的交易。在一次家用电脑测试中
  （约 130,000 个区块，2026 年 10 月），大约用了 30–60 分钟。之后每次启动只需追赶新区块：
  几秒到几分钟。
- 只有同步完成后，余额才准确。
- 可以按 Ctrl+C 停止等待；Oyster 会继续运行。

### 6. 配置

选择 **6** 并回答各项问题（直接回车保留原值）。至少需要设置：

- `to_address`：PRL 的收款地址。**务必仔细核对**，区块链交易无法撤销。
- `min_transfer` / `max_transfer`
- `wallet_passphrase`：第 4 步设置的钱包密码。**不是助记词。**

第一次使用时，菜单会从 `config.example.json` 创建 `config.json`。`config.json` 是个人文件，已
列入 `.gitignore`。各字段含义见[配置说明](#配置说明)。

### 7. 检查、测试，然后正式运行

1. **7 – 检查钱包连接和密码**：RPC 连接、同步状态、收款地址和钱包密码。
2. **3 – 模拟运行**：输入一个小数量，例如 `0.1`；不会广播任何交易。
3. **2 – 单次转账**：真实转出一个小额，输入 `y` 确认，然后在 [prlscan.com](https://prlscan.com)
   上查询 `txid`。
4. **4 – 自动转账**：回答 `y` 以真实运行。保持窗口打开；按 Ctrl+C 停止。

## 日常使用

重启电脑后，所有设置都会保留。只需启动工具：

| 操作系统 | 操作 |
|---|---|
| Windows | 双击 **`start.bat`** |
| macOS | 双击 **`start.command`**（第一次：右键 → 打开） |
| Linux | `./start.sh` |

启动脚本会在需要时启动 Oyster，等待同步完成，然后打开菜单。选择 **4** 开始自动转账。

关机前，在工具中按 Ctrl+C，然后选择 **12 – 停止 Oyster**（或在 Windows 的 Oyster 窗口中按 Ctrl+C）。

## 菜单说明

| # | 选项 | 作用 |
|---|---|---|
| 1 | 查看余额 | 同步状态、余额、下一轮将转出的金额。不发送任何交易。 |
| 2 | 单次转账 | 输入数量（`12.5`、`all`，或回车自动计算）；发送前询问 `y/N`。 |
| 3 | 模拟单次转账 | 与 2 相同，但从不广播。 |
| 4 | 自动转账 | 每隔 `interval_seconds` 循环一次；开始前询问真实运行还是模拟。按 Ctrl+C 停止。 |
| 5 | 查看配置 | 显示 `config.json`，密码会被隐藏。 |
| 6 | 编辑配置 | 逐项询问并校验结果。 |
| 7 | 检查连接 | RPC、区块高度、节点数、同步状态、收款地址和钱包密码。 |
| 8 | 收款地址 | 显示钱包的一个新地址（用于向本钱包收款）。 |
| 9 | 安装 Pearl | 下载并运行适合您系统的 Pearl 官方安装脚本。 |
| 10 | 导入钱包 | 通过助记词恢复钱包（见第 4 步）。 |
| 11 | 启动 Oyster | 必要时启动钱包并等待同步。 |
| 12 | 停止 Oyster | 正常关闭钱包。 |
| 13 | 语言 | English / Tiếng Việt / 简体中文（保存到 `config.json`）。 |
| 0 | 退出 | |

可以用 `python main.py <编号>` 直接运行某个选项，例如 `python main.py 1`。

## 配置说明

`config.json`（从 `config.example.json` 复制而来）：

| 键 | 默认值 | 含义 |
|---|---|---|
| `language` | `en` | `en`、`vi` 或 `zh`。也可用 `--lang` 或环境变量 `PEARL_LANG` 设置。 |
| `rpc_url` | `https://127.0.0.1:44207` | Oyster RPC。主网钱包端口为 44207（测试网 44209）。 |
| `rpc_user` / `rpc_pass` | 空 | 留空则从 `oyster.conf` 读取 `username` / `password`。 |
| `rpc_cert` | 空 | Oyster 的 TLS 证书。留空则使用 Oyster 数据目录中的 `rpc.cert`。 |
| `tls_verify` | `true` | 仅在证书无法校验时设为 `false`（仅限本机）。 |
| `wallet_passphrase` | 空 | **钱包密码，不是助记词。** 也可来自环境变量 `PEARL_WALLET_PASSPHRASE`。 |
| `to_address` | — | 收款地址（`prl1…`）。 |
| `min_transfer` | `1` | 可转金额至少达到该值才转账。 |
| `max_transfer` | `100` | 每次转账不超过该值。 |
| `amount_mode` | `max` | `max`：转出 min(可转金额, max)。`random`：在 [min, max] 内随机，且不超过可转金额。 |
| `keep_balance` | `0` | 钱包中始终保留的 PRL。 |
| `fee_reserve` | `0.001` | 为网络手续费预留的 PRL。 |
| `fee_rate` | `0.00001` | 手续费率，单位 PRL/kB。`0.00001` 为网络最低值。 |
| `min_conf` | `1` | 只统计至少有这么多确认的资金。 |
| `interval_seconds` | `60` | 自动转账检查余额的间隔。 |
| `log_file` | `pearl_transfer.log` | 日志文件，位于配置文件旁。留空则不写日志文件。 |

**可转金额** = 已确认余额 − `keep_balance` − `fee_reserve`。

环境变量优先于文件中的值：`PEARL_WALLET_PASSPHRASE`、`PEARL_RPC_PASS`、`PEARL_LANG`。

## 命令行模式

`pearl_transfer.py` 可以不经菜单直接运行，适合服务器或系统服务：

```bash
python pearl_transfer.py --balance          # 查看余额后退出
python pearl_transfer.py --dry-run --once   # 模拟运行一轮
python pearl_transfer.py                    # 自动转账循环（真实）
python pearl_transfer.py -c other.json --lang zh
```

## 开机自动运行

只有 Oyster 正在运行时才能转账。启动脚本会自动处理这一点。

- **Windows：** 按 Win+R，输入 `shell:startup` 后回车。在该文件夹中放一个 `start.bat` 的**快捷方式**。
- **macOS：** 系统设置 → 通用 → **登录项** → 添加 `start.command`。
- **Linux（systemd 用户服务）：** 创建下面两个文件，然后运行
  `systemctl --user enable --now oyster pearl-transfer`。这种方式无人值守，需要事先准备好
  `config.json`：包含 `wallet_passphrase`（或环境变量）和已测试过的 `to_address`。

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

## 手续费

- 工具按 `fee_rate` 支付网络手续费。默认的 `0.00001` PRL/kB 是网络最低值（约每虚拟字节
  1 grain）。一笔普通转账约 **0.000003 PRL**。
- 如果一笔交易花费了很多零散输入（例如很多次挖矿收益），交易体积更大，手续费会略高。手续费
  **与转账金额无关**。
- 手续费在转账金额**之外另行支付**，`fee_reserve` 会为此预留 PRL。
- 本工具不收取任何额外费用。有些网页钱包每笔转账会额外收取服务费，本工具不会。

## 安全须知（务必阅读）

1. **切勿把助记词写进 `config.json`** 或本文件夹中的任何文件。助记词只在菜单 10 中输入一次。
   `wallet_passphrase` 是钱包**密码**。如果它看起来像助记词，工具会发出警告。
2. **谁拿到助记词，谁就拥有您的资金。** 请离线保管。如果怀疑助记词已泄露（曾粘贴到聊天、文件、
   截图或云盘中），请创建新钱包并转移资金，同时把挖矿收益地址改为新地址。
3. `config.json` 中保存着钱包密码。它已被 git 忽略；**切勿提交或分享**。在 macOS / Linux 上，
   请用 `chmod 600 config.json` 限制权限。也可以把 `wallet_passphrase` 留空，改用环境变量
   `PEARL_WALLET_PASSPHRASE`。
4. Oyster 的 RPC 只监听 `127.0.0.1`。**不要把 44207 端口**暴露到互联网或局域网。
5. **仔细核对 `to_address`。** 区块链转账不可撤销。请务必先模拟运行，再小额真实转账。
6. 工具只在发送的那一刻解锁钱包，发送后立即重新锁定。
7. 请备份 `wallet.db` 和助记词。只丢失 `wallet.db` 没关系：可以用助记词重新导入。
8. 只从官方 GitHub 仓库下载本工具和 Pearl。

## 常见问题排查

| 问题 | 解决方法 |
|---|---|
| `RPC error 401: rpc_user/rpc_pass 错误` | 将 `rpc_user` / `rpc_pass` 留空以便从 `oyster.conf` 读取，或手动复制其中的 `username=` / `password=`。 |
| `无法连接 Oyster 钱包` / connection refused | Oyster 未运行：使用菜单 11。检查 `rpc_url`（主网端口 44207）。 |
| `未找到 oyster` | 用菜单 9 安装，然后打开**新**终端。Linux 上请把 `~/.local/bin` 加入 `PATH`。 |
| 同步似乎停在旧日期 | 链从 2026-04-27 开始，所以刚开始看到早期日期是正常的。查看菜单 11 / 1。首次同步最长可能需要约 1 小时。 |
| 导入后余额为 0 | 等到同步显示*已完成*，再与 [prlscan.com](https://prlscan.com) 上您地址的余额对比。如果仍不一致，可能是助记词输错了：停止 Oyster，重命名 `wallet.db` 后重新导入。 |
| `钱包已锁定，且未设置 wallet_passphrase…` | 设置 `wallet_passphrase`（菜单 6）或 `PEARL_WALLET_PASSPHRASE`。 |
| `钱包密码错误` | 请使用导入时设置的密码，而不是助记词。 |
| `… 已存在钱包` | Oyster 每个网络只保存一个钱包。停止 Oyster，备份 / 重命名 `wallet.db` 后重新导入。 |
| `收款地址对当前网络无效` | 地址输错，或属于其他网络（主网地址以 `prl1` 开头）。 |
| 导入提示需要先停止 Oyster | 先用菜单 12，再用菜单 10。 |
| Windows 上无法输入助记词 | 请在 `cmd`、PowerShell 或 Windows Terminal 中运行，不要使用 Git Bash / mintty。 |
| macOS：“start.command 无法打开” | 右键 → 打开一次，或执行 `chmod +x start.command start.sh`。 |
| Windows 上出现乱码 | 使用 `start.bat`（已设置 UTF-8），或先执行 `chcp 65001`。 |
| `fee_rate 必须 >= 0.00001` | 低于网络最低费率的交易会被拒绝；请保留默认值。 |

## 文件位置

| | Windows | macOS | Linux |
|---|---|---|---|
| Oyster 数据（`oyster.conf`、`rpc.cert`、`mainnet/wallet.db`） | `%LOCALAPPDATA%\Oyster` | `~/Library/Application Support/Oyster` | `~/.oyster` |
| Oyster 日志 | `…\Oyster\logs\mainnet\oyster.log` | `…/Oyster/logs/mainnet/oyster.log` | `~/.oyster/logs/mainnet/oyster.log` |
| Pearl 程序 | `%LOCALAPPDATA%\Pearl\bin` | `~/.local/bin` | `~/.local/bin` |
| 本工具的配置和日志 | 工具所在文件夹（`config.json`、`pearl_transfer.log`） | 同左 | 同左 |

## FAQ

**需要 `pearld`（全节点）吗？** 不需要。Oyster 以 SPV 模式自行同步。`pearld` 占用大量 CPU，
本工具用不到它。

**关机后再开机，需要从头同步吗？** 不需要。区块头、过滤器和钱包状态都保存在磁盘上。Oyster 会从
上次停止的地方继续。

**可以使用多个钱包吗？** Oyster 每个网络、每个数据目录只保存一个钱包。如需多个钱包，请为每个钱包
运行一份工具，并分别使用独立的 Oyster `--appdata` 目录、端口和 `config.json`。

**可以部署在服务器上给其他人共用吗？** 那样服务器会保存其他人的助记词，安全和法律风险都很大。
本工具的设计是每个人在自己的电脑上运行。

## 免责声明与许可证

这是非官方的社区工具，与 Pearl Research Labs 无关。本工具按**“原样”提供，不附带任何形式的担保**。
您需要对自己的钱包、助记词以及发出的每一笔交易负责。请先用小额测试。

基于 [MIT 许可证](LICENSE) 发布。

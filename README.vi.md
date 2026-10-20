# PEARL Auto Transfer

[English](README.md) · **Tiếng Việt** · [简体中文](README.zh-CN.md)

Công cụ nhỏ, không cần cài thêm thư viện. Nó tự động chuyển **PEARL (PRL)** từ ví
[Oyster](https://github.com/pearl-research-labs/pearl) của chính bạn sang một địa chỉ cố định, có
giới hạn số tiền tối thiểu / tối đa mỗi lần chuyển. Tool chạy trên **Windows, macOS và Linux**,
với menu bằng **English, Tiếng Việt và 简体中文**.

> **Bạn tự giữ tiền.** Seed và coin nằm trên máy của bạn. Tool chỉ nói chuyện với ví Oyster chạy
> trên chính máy đó (`127.0.0.1`). Tool không bao giờ gửi seed, mật khẩu hay khóa đi đâu cả.

---

## Mục lục

1. [Cách hoạt động](#cách-hoạt-động)
2. [Yêu cầu](#yêu-cầu)
3. [Bắt đầu nhanh](#bắt-đầu-nhanh)
4. [Cài đặt chi tiết từng bước](#cài-đặt-chi-tiết-từng-bước)
5. [Sử dụng hằng ngày](#sử-dụng-hằng-ngày)
6. [Danh sách menu](#danh-sách-menu)
7. [Giải thích cấu hình](#giải-thích-cấu-hình)
8. [Chạy bằng dòng lệnh](#chạy-bằng-dòng-lệnh)
9. [Tự chạy khi bật máy](#tự-chạy-khi-bật-máy)
10. [Phí giao dịch](#phí-giao-dịch)
11. [Lưu ý bảo mật — hãy đọc](#lưu-ý-bảo-mật--hãy-đọc)
12. [Xử lý lỗi thường gặp](#xử-lý-lỗi-thường-gặp)
13. [Vị trí các file](#vị-trí-các-file)
14. [Câu hỏi thường gặp](#câu-hỏi-thường-gặp)
15. [Miễn trừ trách nhiệm và giấy phép](#miễn-trừ-trách-nhiệm-và-giấy-phép)

---

## Cách hoạt động

```
 tool này ──JSON-RPC (localhost:44207)──▶ oyster (ví của bạn) ──SPV──▶ mạng Pearl
```

- PEARL là **coin gốc** của blockchain Layer-1 Pearl. Nó không có contract token, nên muốn chuyển
  PRL thì phải nhờ chính ví **Oyster** của bạn tạo và phát giao dịch.
- Oyster chạy ở **chế độ SPV (nhẹ)**: nó tự tải block header và filter từ mạng. Bạn **không** cần
  chạy full node (`pearld`).
- Cứ mỗi `interval_seconds` giây, tool kiểm tra số dư đã xác nhận. Khi số có thể chuyển
  (số dư − `keep_balance` − `fee_reserve`) đạt `min_transfer`, tool chuyển tối đa `max_transfer`
  PRL đến `to_address`.

**Tính năng**

- Tự động chuyển theo min / max, số tiền cố định hoặc ngẫu nhiên, có giữ lại một phần số dư.
- Chuyển tay một lần và tự nhập số lượng (`all` = chuyển hết phần khả dụng).
- Chạy thử (dry-run) để xem sẽ chuyển bao nhiêu mà không gửi giao dịch nào.
- Xem số dư, kiểm tra kết nối và mật khẩu, lấy địa chỉ nhận.
- Cài Pearl, import ví từ seed, bật / tắt Oyster, xem tiến độ đồng bộ.
- Giao diện tiếng Anh / Việt / Trung. Chỉ dùng thư viện chuẩn của Python.

## Yêu cầu

| | |
|---|---|
| Hệ điều hành | Windows 10/11, macOS (Intel hoặc Apple Silicon), Linux x86_64 / arm64 |
| Python | **3.8 trở lên** ([python.org](https://www.python.org/downloads/)) |
| Ví Pearl | `oyster` từ [bản phát hành chính thức của Pearl](https://github.com/pearl-research-labs/pearl/releases), cài bằng menu 9 |
| Mạng | Có Internet; lần đồng bộ đầu tiên tải toàn bộ block header |
| Ổ đĩa | Vài trăm MB cho dữ liệu header và filter của ví |

## Bắt đầu nhanh

```bash
git clone https://github.com/jackerdev01/transferPearl.git
cd transferPearl
python main.py          # macOS / Linux: python3 main.py
```

Sau đó trong menu: **9** cài Pearl → **10** import ví → **11** bật Oyster và chờ đồng bộ →
**6** sửa cấu hình → **7** kiểm tra → **3** chạy thử → **2** chuyển thật một số nhỏ → **4** tự động
chuyển.

Phần dưới giải thích chi tiết từng bước.

## Cài đặt chi tiết từng bước

### 1. Cài Python 3

- **Windows:** tải từ [python.org](https://www.python.org/downloads/windows/), nhớ tích
  **"Add python.exe to PATH"**. Kiểm tra bằng `py -3 --version` hoặc `python --version`.
- **macOS:** tải từ [python.org](https://www.python.org/downloads/macos/) hoặc dùng Homebrew
  (`brew install python`). Kiểm tra bằng `python3 --version`.
- **Linux:** thường đã có sẵn. Nếu chưa, dùng trình quản lý gói, ví dụ `sudo apt install python3`
  (Debian/Ubuntu) hoặc `sudo dnf install python3` (Fedora).

### 2. Tải tool về

Chạy `git clone https://github.com/jackerdev01/transferPearl.git`, hoặc trên GitHub bấm
**Code → Download ZIP** rồi giải nén. Sau đó mở terminal trong thư mục đó:

- **Windows:** mở thư mục bằng Explorer, bấm vào thanh địa chỉ, gõ `cmd` rồi Enter. Cũng có thể
  dùng PowerShell hoặc Windows Terminal.
- **macOS:** mở Terminal, gõ `cd ~/Downloads/transferPearl` (sửa đường dẫn cho đúng).
- **Linux:** mở terminal và `cd` vào thư mục.

Trong các lệnh bên dưới, Windows gõ `python` (hoặc `py -3`), còn macOS / Linux gõ `python3`.

### 3. Cài Pearl (ví Oyster)

Chạy `python main.py`, chọn ngôn ngữ, rồi chọn **9**. Tool tải bộ cài **chính thức** từ repo GitHub
`pearl-research-labs/pearl` và chạy nó:

| Hệ điều hành | Bộ cài | Vị trí cài |
|---|---|---|
| Windows | `install.ps1` | `%LOCALAPPDATA%\Pearl\bin` |
| macOS / Linux | `install.sh` | `~/.local/bin` (hoặc `$XDG_BIN_HOME`) |

Bộ cài cũng tạo file `oyster.conf` với username / password RPC ngẫu nhiên và bật chế độ SPV
(`usespv=1`). Tool tự đọc thông tin đăng nhập này.

**Sau khi cài, hãy mở một cửa sổ terminal mới** để `oyster` có trong `PATH`.

Nếu muốn tự cài bằng tay, đây là lệnh chính thức:

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.ps1 | iex
```
```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/pearl-research-labs/pearl/master/install.sh | sh
```

> Linux: nếu sau khi cài vẫn báo không tìm thấy `oyster`, hãy thêm `~/.local/bin` vào `PATH`
> (`echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`, rồi mở terminal mới).

### 4. Import ví

Chọn **10 – Import ví từ seed**:

1. Nhập **seed** 12 hoặc 24 từ. Seed không hiện ra khi gõ.
2. Đặt **mật khẩu ví** (private passphrase). Mật khẩu này mã hóa khóa trên ổ đĩa và cần cho mọi lần
   chuyển. **Hãy ghi lại; mất là không lấy lại được.**
3. Có thể nhập **ngày giao dịch đầu tiên của ví** (`YYYY-MM-DD`). Bạn tra ngày này trên explorer
   như [prlscan.com](https://prlscan.com). Để trống thì ví quét toàn bộ chain: an toàn nhưng chậm hơn.

Seed được chuyển cho `oyster --createfromfile` qua một file tạm riêng tư, và file này bị xóa ngay
sau đó. Seed không bao giờ được ghi vào `config.json`.

Lưu ý:
- Oyster phải **đang tắt** khi import (menu 12).
- Oyster chỉ giữ **một ví cho mỗi mạng**. Nếu `wallet.db` đã tồn tại, tool từ chối ghi đè. Xem
  [Vị trí các file](#vị-trí-các-file).
- Chưa có ví? Chạy `oystercli`, chọn *"Generate a new recovery seed"*, rồi tiếp tục bước 5.

### 5. Bật Oyster và chờ đồng bộ lần đầu

Chọn **11**. Oyster được bật (trên Windows nó mở cửa sổ riêng; trên macOS / Linux nó chạy nền) và
tool hiện tiến độ cho đến khi ví đồng bộ xong:

```
  block 0/130552 (header 58300, peer 8)
```

- **Lần đồng bộ đầu tiên** tải toàn bộ header và filter, rồi quét lại chain để tìm giao dịch của
  bạn. Trong một lần thử trên máy tính ở nhà (khoảng 130.000 block, tháng 10/2026), việc này mất
  khoảng 30–60 phút. Các lần sau chỉ tải phần block mới: vài giây đến vài phút.
- Số dư chỉ đúng khi đồng bộ xong.
- Có thể nhấn Ctrl+C để thôi chờ; Oyster vẫn tiếp tục chạy.

### 6. Cấu hình

Chọn **6** và trả lời từng câu (nhấn Enter để giữ giá trị cũ). Tối thiểu cần điền:

- `to_address`: địa chỉ nhận PRL. **Kiểm tra thật kỹ**, vì giao dịch không thể hoàn tác.
- `min_transfer` / `max_transfer`
- `wallet_passphrase`: mật khẩu ví đã đặt ở bước 4. **Không phải seed.**

Lần đầu, menu tạo `config.json` từ `config.example.json`. File `config.json` là file cá nhân và đã
nằm trong `.gitignore`. Xem [Giải thích cấu hình](#giải-thích-cấu-hình) để biết từng trường.

### 7. Kiểm tra, chạy thử, rồi chạy thật

1. **7 – Kiểm tra kết nối ví + mật khẩu**: kết nối RPC, trạng thái đồng bộ, địa chỉ nhận và mật khẩu ví.
2. **3 – Chạy thử**: nhập một số nhỏ như `0.1`; không có giao dịch nào được gửi.
3. **2 – Chuyển 1 lần**: chuyển thật một số nhỏ, xác nhận bằng `y`, rồi tra `txid` trên
   [prlscan.com](https://prlscan.com).
4. **4 – Tự động chuyển**: trả lời `y` để chạy thật. Để cửa sổ mở; nhấn Ctrl+C để dừng.

## Sử dụng hằng ngày

Sau khi khởi động lại máy, mọi thứ đã cài đặt vẫn còn nguyên. Chỉ cần mở tool:

| Hệ điều hành | Làm như sau |
|---|---|
| Windows | bấm đúp **`start.bat`** |
| macOS | bấm đúp **`start.command`** (lần đầu: chuột phải → Open) |
| Linux | `./start.sh` |

Script khởi động sẽ bật Oyster nếu cần, chờ đồng bộ, rồi mở menu. Chọn **4** để tự động chuyển.

Trước khi tắt máy, nhấn Ctrl+C trong tool, rồi chọn **12 – Dừng Oyster** (hoặc nhấn Ctrl+C trong
cửa sổ Oyster trên Windows).

## Danh sách menu

| # | Mục | Chức năng |
|---|---|---|
| 1 | Xem số dư | Trạng thái đồng bộ, số dư, số tiền lượt tới sẽ chuyển. Không gửi gì. |
| 2 | Chuyển 1 lần | Nhập số lượng (`12.5`, `all`, hoặc Enter để tự tính); hỏi `y/N` trước khi gửi. |
| 3 | Chạy thử 1 lần | Như mục 2 nhưng không bao giờ gửi giao dịch. |
| 4 | Tự động chuyển | Lặp lại mỗi `interval_seconds`; hỏi chạy thật hay chạy thử trước. Ctrl+C để dừng. |
| 5 | Xem cấu hình | In `config.json`, mật khẩu được ẩn. |
| 6 | Sửa cấu hình | Hỏi từng trường rồi kiểm tra kết quả. |
| 7 | Kiểm tra kết nối | RPC, số block, số peer, đồng bộ, địa chỉ nhận và mật khẩu ví. |
| 8 | Địa chỉ nhận | Hiện một địa chỉ mới của ví (để nhận PRL vào ví này). |
| 9 | Cài Pearl | Tải và chạy bộ cài Pearl chính thức cho hệ điều hành của bạn. |
| 10 | Import ví | Khôi phục ví từ seed (xem bước 4). |
| 11 | Bật Oyster | Bật ví nếu chưa chạy và chờ đồng bộ. |
| 12 | Dừng Oyster | Tắt ví đúng cách. |
| 13 | Ngôn ngữ | English / Tiếng Việt / 简体中文 (lưu vào `config.json`). |
| 0 | Thoát | |

Chạy thẳng một mục bằng `python main.py <số>`, ví dụ `python main.py 1`.

## Giải thích cấu hình

`config.json` (được copy từ `config.example.json`):

| Khóa | Mặc định | Ý nghĩa |
|---|---|---|
| `language` | `en` | `en`, `vi` hoặc `zh`. Cũng có thể đặt bằng `--lang` hoặc biến môi trường `PEARL_LANG`. |
| `rpc_url` | `https://127.0.0.1:44207` | RPC của Oyster. Mainnet dùng cổng 44207 (testnet 44209). |
| `rpc_user` / `rpc_pass` | trống | Để trống thì tool đọc `username` / `password` trong `oyster.conf`. |
| `rpc_cert` | trống | Chứng chỉ TLS của Oyster. Để trống thì dùng `rpc.cert` trong thư mục dữ liệu Oyster. |
| `tls_verify` | `true` | Chỉ đặt `false` khi không xác thực được chứng chỉ (chỉ dùng với localhost). |
| `wallet_passphrase` | trống | **Mật khẩu ví, không phải seed.** Có thể lấy từ biến `PEARL_WALLET_PASSPHRASE`. |
| `to_address` | — | Địa chỉ nhận (`prl1…`). |
| `min_transfer` | `1` | Chỉ chuyển khi số khả dụng đạt ít nhất mức này. |
| `max_transfer` | `100` | Mỗi lần chuyển không quá mức này. |
| `amount_mode` | `max` | `max`: chuyển min(khả dụng, max). `random`: số ngẫu nhiên trong [min, max], không vượt số khả dụng. |
| `keep_balance` | `0` | Số PRL luôn giữ lại trong ví. |
| `fee_reserve` | `0.001` | Số PRL chừa lại để trả phí mạng. |
| `fee_rate` | `0.00001` | Phí tính theo PRL/kB. `0.00001` là mức tối thiểu của mạng. |
| `min_conf` | `1` | Chỉ tính các khoản có ít nhất bấy nhiêu xác nhận. |
| `interval_seconds` | `60` | Chu kỳ kiểm tra số dư khi tự động chuyển. |
| `log_file` | `pearl_transfer.log` | File log nằm cạnh file config. Để trống thì không ghi file log. |

**Khả dụng để chuyển** = số dư đã xác nhận − `keep_balance` − `fee_reserve`.

Biến môi trường được ưu tiên hơn giá trị trong file: `PEARL_WALLET_PASSPHRASE`, `PEARL_RPC_PASS`,
`PEARL_LANG`.

## Chạy bằng dòng lệnh

`pearl_transfer.py` chạy không cần menu. Cách này hợp với server hoặc service:

```bash
python pearl_transfer.py --balance          # xem số dư rồi thoát
python pearl_transfer.py --dry-run --once   # chạy thử 1 lượt
python pearl_transfer.py                    # vòng lặp tự động chuyển (thật)
python pearl_transfer.py -c other.json --lang zh
```

## Tự chạy khi bật máy

Oyster phải đang chạy thì mới chuyển được. Các script khởi động đã lo việc này.

- **Windows:** nhấn Win+R, gõ `shell:startup` rồi Enter. Đặt một **shortcut** của `start.bat` vào
  thư mục đó.
- **macOS:** System Settings → General → **Login Items** → thêm `start.command`.
- **Linux (systemd, service của user):** tạo hai file bên dưới, rồi chạy
  `systemctl --user enable --now oyster pearl-transfer`. Cách này chạy không có ai tương tác, nên
  cần có `config.json` với `wallet_passphrase` (hoặc biến môi trường) và một `to_address` đã thử.

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

## Phí giao dịch

- Tool trả phí mạng theo `fee_rate`. Mặc định `0.00001` PRL/kB là mức tối thiểu của mạng (khoảng
  1 grain mỗi virtual byte). Một lần chuyển thông thường tốn khoảng **0,000003 PRL**.
- Giao dịch gom nhiều khoản nhỏ làm đầu vào (ví dụ nhiều lần nhận thưởng đào) có kích thước lớn hơn,
  nên phí cao hơn một chút. Phí **không** phụ thuộc vào số tiền chuyển.
- Phí được trả **thêm vào** số tiền chuyển. `fee_reserve` chừa sẵn PRL cho khoản này.
- Tool không thu phí riêng nào. Một số ví web thu thêm phí dịch vụ cho mỗi lần chuyển; tool này
  thì không.

## Lưu ý bảo mật — hãy đọc

1. **Không bao giờ để seed trong `config.json`** hay bất kỳ file nào trong thư mục này. Seed chỉ
   nhập một lần, ở menu 10. `wallet_passphrase` là **mật khẩu** ví. Tool sẽ cảnh báo nếu giá trị
   này trông giống seed.
2. **Ai có seed là người đó sở hữu tiền của bạn.** Hãy giữ seed ngoại tuyến. Nếu nghi seed đã lộ
   (đã dán vào chat, file, ảnh chụp màn hình, ổ đĩa đám mây), hãy tạo ví mới, chuyển tiền sang, và
   đổi địa chỉ nhận thưởng đào sang ví mới.
3. `config.json` chứa mật khẩu ví. File này đã được git bỏ qua; **đừng commit hay chia sẻ nó**. Trên
   macOS / Linux, hãy giới hạn quyền bằng `chmod 600 config.json`. Hoặc để trống
   `wallet_passphrase` và đặt biến môi trường `PEARL_WALLET_PASSPHRASE`.
4. RPC của Oyster chỉ nghe trên `127.0.0.1`. **Đừng mở cổng 44207** ra Internet hay mạng LAN.
5. **Kiểm tra kỹ `to_address`.** Giao dịch blockchain là vĩnh viễn. Luôn chạy thử và chuyển thật
   một số nhỏ trước.
6. Tool chỉ mở khóa ví đúng lúc gửi, rồi khóa lại ngay.
7. Hãy sao lưu `wallet.db` và seed. Mất riêng `wallet.db` thì không sao: bạn có thể import lại từ seed.
8. Chỉ tải tool này và Pearl từ repo GitHub chính thức.

## Xử lý lỗi thường gặp

| Vấn đề | Cách xử lý |
|---|---|
| `RPC error 401: sai rpc_user/rpc_pass` | Để trống `rpc_user` / `rpc_pass` để tool tự đọc từ `oyster.conf`, hoặc chép dòng `username=` / `password=` trong file đó. |
| `Không kết nối được ví Oyster` / connection refused | Oyster chưa chạy: dùng menu 11. Kiểm tra `rpc_url` (cổng 44207 cho mainnet). |
| `Không tìm thấy oyster` | Cài bằng menu 9 rồi mở terminal **mới**. Trên Linux, thêm `~/.local/bin` vào `PATH`. |
| Đồng bộ có vẻ đứng ở ngày cũ | Chain bắt đầu từ 27/04/2026, nên lúc đầu thấy ngày cũ là bình thường. Xem menu 11 / 1. Lần đồng bộ đầu có thể mất đến khoảng 1 giờ. |
| Số dư bằng 0 sau khi import | Chờ đồng bộ báo *xong*, rồi so với số dư địa chỉ của bạn trên [prlscan.com](https://prlscan.com). Nếu vẫn khác thì có thể đã gõ sai seed: dừng Oyster, đổi tên `wallet.db` và import lại. |
| `Ví đang khóa và chưa cấu hình wallet_passphrase…` | Điền `wallet_passphrase` (menu 6) hoặc đặt `PEARL_WALLET_PASSPHRASE`. |
| `Mật khẩu ví SAI` | Dùng mật khẩu đã đặt lúc import, không phải seed. |
| `Đã có ví tại …` | Oyster chỉ giữ một ví mỗi mạng. Dừng Oyster, sao lưu / đổi tên `wallet.db`, rồi import lại. |
| `Địa chỉ nhận không hợp lệ` | Gõ sai địa chỉ, hoặc địa chỉ thuộc mạng khác (địa chỉ mainnet bắt đầu bằng `prl1`). |
| Import báo phải dừng Oyster trước | Dùng menu 12, rồi menu 10. |
| Không nhập được seed trên Windows | Chạy tool trong `cmd`, PowerShell hoặc Windows Terminal, không dùng Git Bash / mintty. |
| macOS: "start.command cannot be opened" | Chuột phải → Open một lần, hoặc chạy `chmod +x start.command start.sh`. |
| Lỗi hiển thị ký tự trên Windows | Dùng `start.bat` (đã bật UTF-8), hoặc chạy `chcp 65001` trước. |
| `fee_rate phải >= 0.00001` | Giao dịch dưới mức tối thiểu của mạng sẽ bị từ chối; hãy giữ giá trị mặc định. |

## Vị trí các file

| | Windows | macOS | Linux |
|---|---|---|---|
| Dữ liệu Oyster (`oyster.conf`, `rpc.cert`, `mainnet/wallet.db`) | `%LOCALAPPDATA%\Oyster` | `~/Library/Application Support/Oyster` | `~/.oyster` |
| Log Oyster | `…\Oyster\logs\mainnet\oyster.log` | `…/Oyster/logs/mainnet/oyster.log` | `~/.oyster/logs/mainnet/oyster.log` |
| File chạy của Pearl | `%LOCALAPPDATA%\Pearl\bin` | `~/.local/bin` | `~/.local/bin` |
| Config và log của tool | thư mục tool (`config.json`, `pearl_transfer.log`) | như trên | như trên |

## Câu hỏi thường gặp

**Có cần `pearld` (full node) không?** Không. Oyster tự đồng bộ ở chế độ SPV. `pearld` tốn nhiều CPU
và tool này không cần đến nó.

**Tắt máy rồi mở lại thì có phải đồng bộ lại từ đầu không?** Không. Header, filter và trạng thái ví
được lưu trên ổ đĩa. Oyster tiếp tục từ chỗ đã dừng.

**Dùng được nhiều ví không?** Oyster giữ một ví cho mỗi mạng và mỗi thư mục dữ liệu. Muốn dùng nhiều
ví thì chạy mỗi ví một bản tool, mỗi bản có thư mục `--appdata` của Oyster, cổng và `config.json` riêng.

**Có thể chạy trên server cho người khác dùng chung không?** Khi đó server sẽ giữ seed của người
khác, rủi ro rất lớn về bảo mật và pháp lý. Tool này được thiết kế để mỗi người tự chạy trên máy
của mình.

## Miễn trừ trách nhiệm và giấy phép

Đây là công cụ cộng đồng, không chính thức, không liên kết với Pearl Research Labs. Tool được cung
cấp **nguyên trạng, không có bất kỳ bảo đảm nào**. Bạn tự chịu trách nhiệm với ví, seed và mọi giao
dịch mình gửi. Hãy thử với số tiền nhỏ trước.

Phát hành theo [giấy phép MIT](LICENSE).

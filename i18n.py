"""Translations (English / Tiếng Việt / 简体中文).

Language is chosen, in order, from: set_language() (CLI --lang or config "language"),
the PEARL_LANG environment variable, the system locale, then English.
"""

import locale
import os

LANGUAGES = {"en": "English", "vi": "Tiếng Việt", "zh": "简体中文"}
_current = None

M = {
    # ---- generic ----
    "yes": {"en": "yes", "vi": "có", "zh": "是"},
    "no": {"en": "no", "vi": "không", "zh": "否"},
    "yn_suffix": {"en": "(y/N)", "vi": "(y/N)", "zh": "(y/N)"},
    "press_enter": {"en": "\nPress Enter to return to the menu...",
                    "vi": "\nNhấn Enter để quay lại menu...",
                    "zh": "\n按回车键返回菜单..."},
    "cancelled": {"en": "Cancelled.", "vi": "Đã hủy.", "zh": "已取消。"},
    "continue_q": {"en": "Continue?", "vi": "Tiếp tục?", "zh": "是否继续？"},

    # ---- config ----
    "err_config_missing": {
        "en": "Config file not found: {path} (copy config.example.json to config.json)",
        "vi": "Không tìm thấy file config: {path} (copy config.example.json thành config.json)",
        "zh": "找不到配置文件：{path}（请将 config.example.json 复制为 config.json）"},
    "err_to_address": {"en": "to_address is missing in the config",
                       "vi": "Thiếu to_address trong config",
                       "zh": "配置中缺少 to_address（收款地址）"},
    "err_min_max": {"en": "Requires 0 < min_transfer <= max_transfer",
                    "vi": "Cần 0 < min_transfer <= max_transfer",
                    "zh": "需要满足 0 < min_transfer <= max_transfer"},
    "err_fee_rate": {"en": "fee_rate must be >= {min} PRL/kB (network minimum)",
                     "vi": "fee_rate phải >= {min} PRL/kB (mức tối thiểu của mạng)",
                     "zh": "fee_rate 必须 >= {min} PRL/kB（网络最低费率）"},
    "err_amount_mode": {"en": 'amount_mode must be "max" or "random"',
                        "vi": 'amount_mode phải là "max" hoặc "random"',
                        "zh": 'amount_mode 必须是 "max" 或 "random"'},
    "err_language": {"en": "language must be one of: {langs}",
                     "vi": "language phải là một trong: {langs}",
                     "zh": "language 必须是以下之一：{langs}"},
    "warn_seed": {
        "en": "WARNING: wallet_passphrase looks like a 12/24-word seed. It must be the wallet unlock "
              "password (private passphrase set when creating the Oyster wallet), NOT the seed. "
              "Remove the seed from the config file.",
        "vi": "CẢNH BÁO: wallet_passphrase trông giống seed 12/24 từ. Đây phải là mật khẩu mở khóa ví "
              "(private passphrase đặt khi tạo ví Oyster), KHÔNG phải seed. Hãy xóa seed khỏi file config.",
        "zh": "警告：wallet_passphrase 看起来像 12/24 个单词的助记词。这里应填写钱包解锁密码"
              "（创建 Oyster 钱包时设置的私钥密码），而不是助记词。请从配置文件中删除助记词。"},
    "cfg_create_q": {"en": "{path} does not exist. Create it from config.example.json?",
                     "vi": "Chưa có {path}. Tạo từ config.example.json?",
                     "zh": "{path} 不存在。是否从 config.example.json 创建？"},
    "cfg_created": {"en": "Created {path}. Use option 6 to edit it.",
                    "vi": "Đã tạo {path}. Dùng mục 6 để sửa cấu hình.",
                    "zh": "已创建 {path}。请使用选项 6 编辑配置。"},
    "cfg_no_example": {"en": "Neither {path} nor config.example.json exists.",
                       "vi": "Không có {path} và cũng không có config.example.json.",
                       "zh": "{path} 和 config.example.json 都不存在。"},
    "cfg_error": {"en": "Config error: {err}", "vi": "Lỗi config: {err}", "zh": "配置错误：{err}"},
    "cfg_valid": {"en": "Config is valid.", "vi": "Config hợp lệ.", "zh": "配置有效。"},
    "cfg_invalid": {"en": "Config is not valid yet: {err}", "vi": "Config chưa hợp lệ: {err}",
                    "zh": "配置尚未有效：{err}"},
    "edit_hint": {"en": "Press Enter to keep the current value.\n",
                  "vi": "Nhấn Enter để giữ nguyên giá trị hiện tại.\n",
                  "zh": "直接按回车保留当前值。\n"},
    "edit_skip": {"en": "  Skipped: '{value}' is not valid for {key}",
                  "vi": "  Bỏ qua: '{value}' không hợp lệ cho {key}",
                  "zh": "  已跳过：'{value}' 不是 {key} 的有效值"},
    "edit_saved": {"en": "\nSaved {path}. Validating...", "vi": "\nĐã lưu {path}. Đang kiểm tra lại...",
                   "zh": "\n已保存 {path}。正在校验..."},

    # ---- config field labels ----
    "f_to_address": {"en": "Destination address", "vi": "Địa chỉ ví nhận", "zh": "收款地址"},
    "f_min_transfer": {"en": "Minimum PRL per transfer", "vi": "Số PRL tối thiểu mỗi lần chuyển",
                       "zh": "每次转账最少 PRL"},
    "f_max_transfer": {"en": "Maximum PRL per transfer", "vi": "Số PRL tối đa mỗi lần chuyển",
                       "zh": "每次转账最多 PRL"},
    "f_amount_mode": {"en": "Amount mode (max/random)", "vi": "Chế độ số tiền (max/random)",
                      "zh": "金额模式 (max/random)"},
    "f_keep_balance": {"en": "PRL to always keep in the wallet", "vi": "Số PRL luôn giữ lại trong ví",
                       "zh": "钱包中始终保留的 PRL"},
    "f_fee_reserve": {"en": "PRL reserved for fees", "vi": "Số PRL chừa để trả phí", "zh": "预留手续费 PRL"},
    "f_fee_rate": {"en": "Fee rate PRL/kB (>= 0.00001)", "vi": "Phí PRL/kB (>= 0.00001)",
                   "zh": "手续费率 PRL/kB (>= 0.00001)"},
    "f_interval_seconds": {"en": "Check interval (seconds)", "vi": "Chu kỳ kiểm tra (giây)",
                           "zh": "检查间隔（秒）"},
    "f_min_conf": {"en": "Minimum confirmations", "vi": "Số xác nhận tối thiểu", "zh": "最少确认数"},
    "f_rpc_url": {"en": "Oyster RPC URL", "vi": "RPC URL của Oyster", "zh": "Oyster RPC 地址"},
    "f_rpc_user": {"en": "RPC user (empty = read oyster.conf)", "vi": "RPC user (trống = đọc oyster.conf)",
                   "zh": "RPC 用户名（留空 = 读取 oyster.conf）"},
    "f_rpc_pass": {"en": "RPC password (empty = read oyster.conf)",
                   "vi": "RPC password (trống = đọc oyster.conf)",
                   "zh": "RPC 密码（留空 = 读取 oyster.conf）"},
    "f_wallet_passphrase": {"en": "Wallet password (NOT the seed)", "vi": "Mật khẩu ví (KHÔNG phải seed)",
                            "zh": "钱包密码（不是助记词）"},

    # ---- RPC / wallet ----
    "err_rpc_auth": {"en": "wrong rpc_user/rpc_pass", "vi": "sai rpc_user/rpc_pass",
                     "zh": "rpc_user/rpc_pass 错误"},
    "err_locked": {
        "en": "The wallet is locked and wallet_passphrase / PEARL_WALLET_PASSPHRASE is not set",
        "vi": "Ví đang khóa và chưa cấu hình wallet_passphrase / PEARL_WALLET_PASSPHRASE",
        "zh": "钱包已锁定，且未设置 wallet_passphrase / PEARL_WALLET_PASSPHRASE"},
    "err_connect": {"en": "Cannot connect to the Oyster wallet at {url}: {err}",
                    "vi": "Không kết nối được ví Oyster tại {url}: {err}",
                    "zh": "无法连接 {url} 上的 Oyster 钱包：{err}"},
    "conn_error_hint": {"en": "Cannot connect to the Oyster wallet: {err}\n(Is it running? Try option 11, then 7.)",
                        "vi": "Không kết nối được ví Oyster: {err}\n(Ví đã chạy chưa? Thử mục 11 rồi mục 7.)",
                        "zh": "无法连接 Oyster 钱包：{err}\n（钱包是否在运行？请先用选项 11，再用选项 7。）"},
    "wallet_error": {"en": "Wallet error: {err}", "vi": "Lỗi từ ví: {err}", "zh": "钱包错误：{err}"},
    "addr_invalid": {"en": "Destination address is not valid for this network: {addr}",
                     "vi": "Địa chỉ nhận không hợp lệ cho mạng hiện tại: {addr}",
                     "zh": "收款地址对当前网络无效：{addr}"},
    "addr_mine": {"en": "Note: the destination address belongs to this wallet (internal transfer).",
                  "vi": "Lưu ý: địa chỉ nhận thuộc chính ví này (chuyển nội bộ).",
                  "zh": "注意：收款地址属于本钱包（内部转账）。"},

    # ---- balance ----
    "bal_sync": {"en": "Chain synced", "vi": "Đồng bộ chain", "zh": "链同步"},
    "bal_sync_done": {"en": "done", "vi": "xong", "zh": "已完成"},
    "bal_sync_not": {"en": "NOT YET (balance may be incomplete)", "vi": "CHƯA XONG (số dư có thể chưa đủ)",
                     "zh": "未完成（余额可能不完整）"},
    "bal_locked": {"en": "Wallet locked", "vi": "Ví đang khóa", "zh": "钱包已锁定"},
    "bal_total": {"en": "Total balance", "vi": "Tổng số dư", "zh": "总余额"},
    "bal_confirmed": {"en": "Confirmed (>={n})", "vi": "Đã xác nhận (>={n})", "zh": "已确认 (>={n})"},
    "bal_unconfirmed": {"en": "Unconfirmed", "vi": "Chưa xác nhận", "zh": "未确认"},
    "bal_reserve": {"en": "Keep + fee reserve", "vi": "Giữ lại + phí", "zh": "保留 + 手续费预留"},
    "bal_available": {"en": "Available to send", "vi": "Khả dụng để chuyển", "zh": "可转账金额"},
    "bal_minmax": {"en": "Min / Max", "vi": "Min / Max", "zh": "最小 / 最大"},
    "bal_cannot": {"en": "=> CANNOT send yet: {missing} PRL short of min_transfer",
                   "vi": "=> CHƯA chuyển được: còn thiếu {missing} PRL để đạt min_transfer",
                   "zh": "=> 暂不能转账：距 min_transfer 还差 {missing} PRL"},
    "bal_can_random": {"en": "=> CAN send: random {lo} - {hi} PRL to {addr}",
                       "vi": "=> CÓ THỂ chuyển: ngẫu nhiên {lo} - {hi} PRL đến {addr}",
                       "zh": "=> 可以转账：随机 {lo} - {hi} PRL 至 {addr}"},
    "bal_can": {"en": "=> CAN send: {amount} PRL to {addr}",
                "vi": "=> CÓ THỂ chuyển: {amount} PRL đến {addr}",
                "zh": "=> 可以转账：{amount} PRL 至 {addr}"},

    # ---- transfer log ----
    "log_not_synced": {"en": "Wallet is not synced yet, skipping this round",
                       "vi": "Ví chưa đồng bộ xong chain, bỏ qua lượt này",
                       "zh": "钱包尚未同步完成，跳过本轮"},
    "log_below_min": {"en": "Balance {balance} PRL (available {available}) < min_transfer {min}, waiting...",
                      "vi": "Số dư {balance} PRL (khả dụng {available}) < min_transfer {min}, chờ...",
                      "zh": "余额 {balance} PRL（可用 {available}）< min_transfer {min}，等待中..."},
    "log_will_send": {"en": "Balance {balance} PRL -> sending {amount} PRL to {addr}",
                      "vi": "Số dư {balance} PRL -> chuyển {amount} PRL đến {addr}",
                      "zh": "余额 {balance} PRL -> 转账 {amount} PRL 至 {addr}"},
    "log_dry_run": {"en": "[dry-run] Would send {amount} PRL to {addr}; nothing broadcast",
                    "vi": "[dry-run] Sẽ chuyển {amount} PRL đến {addr}, không gửi giao dịch",
                    "zh": "[模拟] 将转账 {amount} PRL 至 {addr}，未实际广播"},
    "log_sent": {"en": "Sent {amount} PRL, txid={txid}", "vi": "Đã gửi {amount} PRL, txid={txid}",
                 "zh": "已发送 {amount} PRL，txid={txid}"},
    "log_relock_fail": {"en": "Could not re-lock the wallet: {err}", "vi": "Không khóa lại được ví: {err}",
                        "zh": "无法重新锁定钱包：{err}"},
    "log_start": {"en": "Start: min={min} max={max} mode={mode} keep={keep} interval={interval}s{dry}",
                  "vi": "Bắt đầu: min={min} max={max} mode={mode} giữ lại={keep} interval={interval}s{dry}",
                  "zh": "开始：min={min} max={max} 模式={mode} 保留={keep} 间隔={interval}秒{dry}"},
    "log_stopped": {"en": "Stopped", "vi": "Dừng", "zh": "已停止"},
    "log_error": {"en": "Error: {err}", "vi": "Lỗi: {err}", "zh": "错误：{err}"},

    # ---- manual transfer ----
    "amount_help": {
        "en": "\nEnter the PRL amount to send, 'all' = everything available, Enter = auto (min/max).",
        "vi": "\nNhập số PRL muốn chuyển, 'all' = chuyển hết phần khả dụng, Enter = tự tính theo min/max.",
        "zh": "\n输入要转账的 PRL 数量，'all' = 全部可用余额，直接回车 = 按 min/max 自动计算。"},
    "amount_label": {"en": "Amount", "vi": "Số lượng", "zh": "数量"},
    "below_min": {"en": "Available balance is below min_transfer; nothing sent.",
                  "vi": "Số dư khả dụng chưa đạt min_transfer, không chuyển.",
                  "zh": "可用余额低于 min_transfer，不转账。"},
    "invalid_number": {"en": "'{raw}' is not a valid number.", "vi": "'{raw}' không phải số hợp lệ.",
                       "zh": "'{raw}' 不是有效数字。"},
    "amount_positive": {"en": "Amount must be greater than 0 (or the available balance is 0).",
                        "vi": "Số lượng phải lớn hơn 0 (hoặc số dư khả dụng đang là 0).",
                        "zh": "数量必须大于 0（或可用余额为 0）。"},
    "amount_exceeds": {"en": "Exceeds the available balance ({available} PRL).",
                       "vi": "Vượt quá số dư khả dụng ({available} PRL).",
                       "zh": "超过可用余额（{available} PRL）。"},
    "will_send": {"en": "\nWill send {amount} PRL -> {addr} (fee {fee} PRL/kB)",
                  "vi": "\nSẽ chuyển {amount} PRL -> {addr} (phí {fee} PRL/kB)",
                  "zh": "\n将转账 {amount} PRL -> {addr}（手续费 {fee} PRL/kB）"},
    "confirm_real": {"en": "Broadcast a REAL transaction now?", "vi": "Gửi giao dịch THẬT ngay bây giờ?",
                     "zh": "现在广播真实交易吗？"},

    # ---- auto ----
    "auto_summary": {"en": "Auto transfer: min={min} max={max} mode={mode} every {interval}s -> {addr}",
                     "vi": "Tự động chuyển: min={min} max={max} mode={mode} mỗi {interval}s -> {addr}",
                     "zh": "自动转账：min={min} max={max} 模式={mode} 每 {interval} 秒 -> {addr}"},
    "auto_confirm": {"en": "Run for REAL (broadcast transactions)? Choose N for dry-run",
                     "vi": "Chạy THẬT (gửi giao dịch)? Chọn N để chạy dry-run",
                     "zh": "真实运行（广播交易）吗？选择 N 为模拟运行"},
    "auto_running": {"en": "Running... press Ctrl+C to stop and return to the menu.",
                     "vi": "Đang chạy... nhấn Ctrl+C để dừng và quay lại menu.",
                     "zh": "运行中... 按 Ctrl+C 停止并返回菜单。"},
    "auto_stopped": {"en": "\nAuto transfer stopped.", "vi": "\nĐã dừng tự động chuyển.", "zh": "\n自动转账已停止。"},

    # ---- connection check ----
    "conn_ok": {"en": "Connected. Current block: {blocks}  |  Peers: {peers}",
                "vi": "Kết nối OK. Block hiện tại: {blocks}  |  Số kết nối peer: {peers}",
                "zh": "连接成功。当前区块：{blocks}  |  节点连接数：{peers}"},
    "conn_synced": {"en": "Chain synced: {yn}", "vi": "Chain đã đồng bộ: {yn}", "zh": "链已同步：{yn}"},
    "conn_locked": {"en": "Wallet locked: {yn}", "vi": "Ví đang khóa: {yn}", "zh": "钱包已锁定：{yn}"},
    "conn_addr_ok": {"en": "Destination address is valid: {addr}", "vi": "Địa chỉ nhận hợp lệ: {addr}",
                     "zh": "收款地址有效：{addr}"},
    "pass_ok": {"en": "Wallet password is correct.", "vi": "Mật khẩu ví đúng.", "zh": "钱包密码正确。"},
    "pass_bad": {"en": "Wallet password is WRONG or the wallet cannot be unlocked: {err}",
                 "vi": "Mật khẩu ví SAI hoặc không mở khóa được: {err}",
                 "zh": "钱包密码错误或无法解锁：{err}"},
    "new_address": {"en": "Receiving address of this wallet: {addr}",
                    "vi": "Địa chỉ nhận của ví này: {addr}",
                    "zh": "本钱包的收款地址：{addr}"},

    # ---- install / import / daemon ----
    "install_will": {"en": "This will download and run the official Pearl installer:\n  {url}",
                     "vi": "Sẽ tải và chạy script cài đặt chính thức của Pearl:\n  {url}",
                     "zh": "将下载并运行 Pearl 官方安装脚本：\n  {url}"},
    "install_done": {"en": "Done. Open a NEW terminal so PATH picks up oyster.",
                     "vi": "Xong. Mở cửa sổ terminal MỚI để PATH nhận oyster.",
                     "zh": "完成。请打开新的终端窗口，使 PATH 生效。"},
    "install_failed": {"en": "Installer failed (exit code {code}).", "vi": "Cài đặt lỗi (exit code {code}).",
                       "zh": "安装失败（退出码 {code}）。"},
    "oyster_missing": {"en": "oyster was not found. Use option 9 to install Pearl.",
                       "vi": "Không tìm thấy oyster. Chọn mục 9 để cài Pearl.",
                       "zh": "未找到 oyster。请使用选项 9 安装 Pearl。"},
    "import_stop_first": {"en": "oyster is running. Stop it first (option 12), then import.",
                          "vi": "oyster đang chạy. Dừng nó trước (mục 12) rồi mới import.",
                          "zh": "oyster 正在运行。请先停止它（选项 12）再导入。"},
    "import_exists": {
        "en": "A wallet already exists at {path}. Oyster keeps one wallet per network: back up/rename this "
              "file first if you really want to import another one.",
        "vi": "Đã có ví tại {path}. Oyster chỉ giữ 1 ví/mạng: sao lưu/đổi tên file này trước nếu thật sự "
              "muốn import ví khác.",
        "zh": "{path} 已存在钱包。Oyster 每个网络只保存一个钱包：如确需导入其他钱包，请先备份/重命名该文件。"},
    "import_seed": {"en": "Seed phrase (12/24 words, hidden while typing): ",
                    "vi": "Nhập seed (12/24 từ, không hiển thị khi gõ): ",
                    "zh": "输入助记词（12/24 个单词，输入时不显示）："},
    "import_seed_words": {"en": "The seed has {n} words; 12/15/18/21/24 are required.",
                          "vi": "Seed có {n} từ, cần 12/15/18/21/24 từ.",
                          "zh": "助记词有 {n} 个单词，需要 12/15/18/21/24 个。"},
    "import_pass1": {"en": "Set a wallet password (private passphrase): ",
                     "vi": "Đặt mật khẩu ví (private passphrase): ",
                     "zh": "设置钱包密码（私钥密码）："},
    "import_pass2": {"en": "Repeat the wallet password: ", "vi": "Nhập lại mật khẩu ví: ",
                     "zh": "再次输入钱包密码："},
    "import_pass_empty": {"en": "The password must not be empty.", "vi": "Mật khẩu không được để trống.",
                          "zh": "密码不能为空。"},
    "import_pass_mismatch": {"en": "The passwords do not match.", "vi": "Hai lần nhập mật khẩu không khớp.",
                             "zh": "两次输入的密码不一致。"},
    "import_bday": {"en": "Date of the wallet's first transaction YYYY-MM-DD (Enter = scan the whole chain)",
                    "vi": "Ngày giao dịch đầu tiên của ví YYYY-MM-DD (Enter = quét toàn bộ chain)",
                    "zh": "钱包首笔交易日期 YYYY-MM-DD（回车 = 扫描整条链）"},
    "import_bday_bad": {"en": "Invalid date, expected YYYY-MM-DD.", "vi": "Ngày không hợp lệ, cần dạng YYYY-MM-DD.",
                        "zh": "日期无效，格式应为 YYYY-MM-DD。"},
    "import_running": {"en": "Creating the wallet...", "vi": "Đang tạo ví...", "zh": "正在创建钱包..."},
    "import_failed": {"en": "Import failed (exit {code}). Check the seed spelling.\n{detail}",
                      "vi": "Import lỗi (exit {code}). Kiểm tra lại chính tả seed.\n{detail}",
                      "zh": "导入失败（退出码 {code}）。请检查助记词拼写。\n{detail}"},
    "import_ok": {"en": "Wallet imported: {path}\nNext: option 11 to start oyster and wait for the sync, "
                        "then option 6 to set wallet_passphrase.",
                  "vi": "Import thành công: {path}\nTiếp theo: mục 11 để chạy oyster và chờ đồng bộ, "
                        "rồi mục 6 để điền wallet_passphrase.",
                  "zh": "钱包导入成功：{path}\n下一步：选项 11 启动 oyster 并等待同步，然后用选项 6 设置 wallet_passphrase。"},
    "oyster_running": {"en": "oyster is already running.", "vi": "oyster đang chạy rồi.", "zh": "oyster 已在运行。"},
    "oyster_started": {"en": "Started oyster: {exe}", "vi": "Đã khởi động oyster: {exe}", "zh": "已启动 oyster：{exe}"},
    "wait_sync": {"en": "Waiting for the wallet to sync (Ctrl+C to skip)...",
                  "vi": "Đang chờ ví đồng bộ (Ctrl+C để bỏ qua)...",
                  "zh": "正在等待钱包同步（按 Ctrl+C 跳过）..."},
    "sync_done": {"en": "\nSynced at block {height}.", "vi": "\nĐồng bộ xong ở block {height}.",
                  "zh": "\n已同步至区块 {height}。"},
    "sync_progress": {"en": "  block {block}/{best} (headers {hdr}, peers {peers})   ",
                      "vi": "  block {block}/{best} (header {hdr}, peer {peers})   ",
                      "zh": "  区块 {block}/{best}（区块头 {hdr}，节点 {peers}）   "},
    "oyster_starting": {"en": "  oyster is starting...", "vi": "  oyster đang khởi động...",
                        "zh": "  oyster 正在启动..."},
    "wait_skipped": {"en": "\nSkipped waiting for sync.", "vi": "\nBỏ qua chờ đồng bộ.", "zh": "\n已跳过等待同步。"},
    "stop_ok": {"en": "oyster is shutting down.", "vi": "oyster đang tắt.", "zh": "oyster 正在关闭。"},
    "stop_not_running": {"en": "oyster is not running.", "vi": "oyster không chạy.", "zh": "oyster 未在运行。"},

    # ---- language ----
    "lang_prompt": {"en": "Choose language", "vi": "Chọn ngôn ngữ", "zh": "选择语言"},
    "lang_set": {"en": "Language set to {lang}.", "vi": "Đã chọn ngôn ngữ {lang}.", "zh": "语言已设置为 {lang}。"},

    # ---- menu ----
    "menu_title": {"en": "PEARL TRANSFER", "vi": "PEARL TRANSFER", "zh": "PEARL 转账工具"},
    "menu_config": {"en": "Config: {path}", "vi": "Config: {path}", "zh": "配置文件：{path}"},
    "menu_choose": {"en": "Choose: ", "vi": "Chọn: ", "zh": "请选择："},
    "menu_invalid": {"en": "Invalid choice.", "vi": "Lựa chọn không hợp lệ.", "zh": "无效的选项。"},
    "m1": {"en": "Show balance / amount that can be sent", "vi": "Xem số dư / số PRL có thể chuyển",
           "zh": "查看余额 / 可转账金额"},
    "m2": {"en": "Send once - enter amount (real, asks to confirm)",
           "vi": "Chuyển 1 lần - nhập số lượng (thật, có xác nhận)",
           "zh": "单次转账 - 输入数量（真实，需确认）"},
    "m3": {"en": "Test a single transfer - enter amount (dry-run)",
           "vi": "Chạy thử chuyển 1 lần - nhập số lượng (dry-run)",
           "zh": "模拟单次转账 - 输入数量（dry-run）"},
    "m4": {"en": "Auto transfer continuously (min/max)", "vi": "Tự động chuyển liên tục theo min/max",
           "zh": "按 min/max 持续自动转账"},
    "m5": {"en": "Show config", "vi": "Xem cấu hình", "zh": "查看配置"},
    "m6": {"en": "Edit config (destination, min/max, ...)", "vi": "Sửa cấu hình (địa chỉ nhận, min/max, ...)",
           "zh": "编辑配置（收款地址、min/max 等）"},
    "m7": {"en": "Check wallet connection + password", "vi": "Kiểm tra kết nối ví + mật khẩu",
           "zh": "检查钱包连接和密码"},
    "m8": {"en": "Get a receiving address of this wallet", "vi": "Lấy địa chỉ nhận của ví này",
           "zh": "获取本钱包收款地址"},
    "m9": {"en": "Install Pearl (oyster wallet)", "vi": "Cài Pearl (ví oyster)", "zh": "安装 Pearl（oyster 钱包）"},
    "m10": {"en": "Import wallet from seed", "vi": "Import ví từ seed", "zh": "通过助记词导入钱包"},
    "m11": {"en": "Start oyster + wait for sync", "vi": "Khởi động ví oyster + chờ đồng bộ",
            "zh": "启动 oyster 并等待同步"},
    "m12": {"en": "Stop oyster", "vi": "Dừng ví oyster", "zh": "停止 oyster"},
    "m13": {"en": "Language / Ngôn ngữ / 语言", "vi": "Language / Ngôn ngữ / 语言", "zh": "Language / Ngôn ngữ / 语言"},
    "m0": {"en": "Exit", "vi": "Thoát", "zh": "退出"},
}


def _detect():
    env = os.environ.get("PEARL_LANG", "").lower()[:2]
    if env in LANGUAGES:
        return env
    try:
        loc = (locale.getlocale()[0] or "").lower()
    except ValueError:
        loc = ""
    for code, names in (("vi", ("vi", "vietnam")), ("zh", ("zh", "chinese"))):
        if loc.startswith(names):
            return code
    return "en"


def set_language(code):
    global _current
    if code and code[:2].lower() in LANGUAGES:
        _current = code[:2].lower()


def get_language():
    global _current
    if _current is None:
        _current = _detect()
    return _current


def t(key, **kwargs):
    entry = M.get(key)
    if entry is None:
        return key
    text = entry.get(get_language()) or entry["en"]
    return text.format(**kwargs) if kwargs else text

# 🤖 Agent của Tiến - Telegram Bot AI

Bot Telegram trợ lý AI cá nhân, sử dụng Google Gemini API miễn phí.

Bot có phong cách trả lời cute, thân thiện, nhiệt tình. Xưng "em" gọi "anh", dùng emoji dễ thương. Bot nhớ được ngữ cảnh hội thoại để trò chuyện tự nhiên hơn.

---

## 📋 Anh cần chuẩn bị gì?

1. Một tài khoản Google (Gmail) - để lấy Gemini API key miễn phí
2. Một tài khoản GitHub - để lưu code (đăng ký miễn phí tại github.com)
3. Bot Token Telegram: `8787881290:AAGBgMl-rEXEO6frOXMdD9bmMfVsVk3vXNs`

---

## 🔑 Bước 1: Lấy Google Gemini API Key (MIỄN PHÍ)

1. Mở trình duyệt, vào trang: https://aistudio.google.com/apikey
2. Đăng nhập bằng tài khoản Gmail của anh
3. Nhấn nút **"Create API key"** (nút màu xanh)
4. Chọn **"Create API key in new project"**
5. Google sẽ tạo ra một chuỗi ký tự dài (bắt đầu bằng "AIza...") - đó là API key của anh
6. **Sao chép và lưu lại** chuỗi này (giữ bí mật, không chia sẻ cho ai)

> ⚠️ LƯU Ý: API key này hoàn toàn MIỄN PHÍ, không cần nhập thẻ visa hay thanh toán gì cả!

---

## 📦 Bước 2: Đưa code lên GitHub

### 2.1. Tạo tài khoản GitHub (nếu chưa có)
1. Vào https://github.com
2. Nhấn **"Sign up"** và đăng ký (có thể dùng Gmail)

### 2.2. Tạo Repository mới
1. Sau khi đăng nhập GitHub, nhấn dấu **"+"** ở góc trên bên phải
2. Chọn **"New repository"**
3. Đặt tên: `telegram-bot` (hoặc tên gì anh thích)
4. Chọn **"Public"**
5. Nhấn **"Create repository"**

### 2.3. Upload code
1. Trong trang repository vừa tạo, nhấn **"uploading an existing file"** (hoặc nút "Add file" > "Upload files")
2. Kéo thả TẤT CẢ các file trong thư mục `telegram_gemini_bot` vào:
   - `main.py`
   - `config.py`
   - `telegram_handler.py`
   - `gemini_service.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
3. Nhấn **"Commit changes"** (nút màu xanh bên dưới)

---

## 🚀 Bước 3: Deploy bot lên Koyeb (MIỄN PHÍ, chạy 24/7)

Em chọn **Koyeb** vì:
- Miễn phí hoàn toàn (không cần thẻ visa)
- Bot chạy 24/7 không bị ngủ
- Dễ sử dụng, kết nối trực tiếp với GitHub

### 3.1. Tạo tài khoản Koyeb
1. Vào https://www.koyeb.com
2. Nhấn **"Get started for free"**
3. Đăng ký bằng tài khoản GitHub (nhanh nhất) hoặc Gmail

### 3.2. Tạo dịch vụ mới
1. Sau khi đăng nhập, nhấn **"Create Service"** hoặc **"Create App"**
2. Chọn **"GitHub"** làm nguồn deploy
3. Kết nối tài khoản GitHub của anh (nhấn "Connect GitHub" nếu được yêu cầu)
4. Chọn repository `telegram-bot` mà anh vừa tạo ở Bước 2

### 3.3. Cấu hình dịch vụ
1. **Builder**: Chọn **"Buildpack"** (tự động nhận diện Python)
2. **Run command**: Nhập `python main.py`
3. **Instance type**: Chọn **"Free"** (eco)

### 3.4. Thêm biến môi trường (QUAN TRỌNG!)
Tìm phần **"Environment variables"** và thêm 2 biến:

| Tên biến | Giá trị |
|----------|---------|
| `TELEGRAM_BOT_TOKEN` | `8787881290:AAGBgMl-rEXEO6frOXMdD9bmMfVsVk3vXNs` |
| `GEMINI_API_KEY` | Chuỗi API key anh lấy ở Bước 1 (bắt đầu bằng AIza...) |

### 3.5. Deploy!
1. Nhấn nút **"Deploy"**
2. Đợi khoảng 2-3 phút để hệ thống cài đặt
3. Khi thấy trạng thái **"Healthy"** hoặc **"Running"** là thành công!

### 3.6. Kiểm tra bot
1. Mở Telegram
2. Tìm bot `@spVNP_bot`
3. Nhấn **Start** hoặc gõ `/start`
4. Gửi tin nhắn bất kỳ để test!

---

## ⚡ Giới hạn gói miễn phí

### Google Gemini API Free Tier:
| Giới hạn | Mức cho phép |
|----------|-------------|
| Số request/phút | 15 lần |
| Số request/ngày | ~1,500 lần |
| Token/phút | 1,000,000 |
| Thời hạn | Không giới hạn (dùng mãi) |

**Nghĩa là:** Anh có thể nhắn khoảng 15 tin/phút, ~1,500 tin/ngày. Với chat cá nhân thì DƯ SỨC dùng!

### Koyeb Free Tier:
| Giới hạn | Mức cho phép |
|----------|-------------|
| Dịch vụ | 1 dịch vụ miễn phí |
| RAM | 512 MB |
| CPU | Shared |
| Thời hạn | Không giới hạn |

**Nghĩa là:** Bot chạy 24/7 miễn phí, không bị tắt!

---

## 💡 Ưu điểm và nhược điểm

### ✅ Ưu điểm:
- Hoàn toàn MIỄN PHÍ (cả AI lẫn hosting)
- Bot chạy 24/7, trả lời ngay lập tức
- Gemini AI rất thông minh, hiểu tiếng Việt tốt
- Nhớ ngữ cảnh hội thoại (nhớ anh đang nói gì)
- Có thể mở rộng thêm tính năng sau này
- Không cần biết code để sử dụng

### ⚠️ Nhược điểm:
- Giới hạn 15 tin nhắn/phút (đủ dùng cá nhân)
- Nếu Google thay đổi chính sách free tier thì phải điều chỉnh
- Bot không xử lý được hình ảnh (phiên bản này), nhưng có thể thêm sau
- Koyeb free tier chỉ cho 1 dịch vụ

---

## 🔮 Mở rộng trong tương lai

Code được thiết kế dạng module, sau này có thể dễ dàng thêm:
- 🖼️ Dịch hình ảnh (dùng Gemini Vision)
- 👥 Lệnh tag all trong nhóm
- 🌐 Dịch thuật đa ngôn ngữ
- 📊 Tóm tắt văn bản, link
- 🔗 Kết hợp với bot hiện tại của anh

---

## ❓ Câu hỏi thường gặp

**Q: Có mất phí gì không?**
A: KHÔNG! Hoàn toàn miễn phí 100%.

**Q: Bot có chạy mãi không?**
A: Có, bot chạy 24/7 trên Koyeb miễn phí. Chỉ cần anh không xóa dịch vụ thì bot luôn online.

**Q: Nếu bot không trả lời thì sao?**
A: Kiểm tra lại Gemini API key có đúng không, hoặc đợi vài phút rồi thử lại (có thể do giới hạn request/phút).

**Q: Có thể dùng cho nhóm không?**
A: Có! Thêm bot vào nhóm Telegram và nó sẽ trả lời khi được nhắn tin.

---

## 📞 Hỗ trợ

Nếu anh gặp khó khăn trong quá trình cài đặt, cứ hỏi em (Manus) nha! Em sẽ hướng dẫn anh từng bước một! 😊

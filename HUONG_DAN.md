# 🤖 Agent của Tiến - Telegram Bot AI

Bot Telegram trợ lý AI cá nhân, hoàn toàn MIỄN PHÍ.

Bot sử dụng 2 nguồn AI:
- **Google Gemini** (nguồn chính) - thông minh, nhanh
- **OpenRouter** (nguồn dự phòng) - khi Gemini lỗi, bot tự chuyển sang đây

---

## 📋 Anh cần chuẩn bị gì?

| STT | Cần gì | Ở đâu | Mất phí? |
|-----|--------|-------|----------|
| 1 | Tài khoản GitHub | github.com | Miễn phí |
| 2 | Tài khoản Render | render.com | Miễn phí |
| 3 | Gemini API Key | aistudio.google.com | Miễn phí |
| 4 | OpenRouter API Key | openrouter.ai | Miễn phí |

---

## 🔑 Bước 1: Lấy API Keys (MIỄN PHÍ)

### 1.1. Lấy Google Gemini API Key
1. Vào: https://aistudio.google.com/apikey
2. Đăng nhập bằng Gmail
3. Nhấn **"Create API key"** → **"Create API key in new project"**
4. Sao chép chuỗi key (bắt đầu bằng "AIza...") và lưu lại

### 1.2. Lấy OpenRouter API Key (DỰ PHÒNG)
1. Vào: https://openrouter.ai
2. Nhấn **"Sign up"** - đăng ký bằng Google (Gmail)
3. Sau khi đăng nhập, nhấn vào avatar góc trên phải → **"Keys"**
4. Nhấn **"Create Key"** → đặt tên gì cũng được (ví dụ: "telegram-bot")
5. Sao chép key và lưu lại

> ⚠️ Cả 2 đều MIỄN PHÍ, không cần thẻ visa!

---

## 📦 Bước 2: Đưa code lên GitHub

### 2.1. Tạo tài khoản GitHub (nếu chưa có)
1. Vào https://github.com → nhấn **"Sign up"**

### 2.2. Tạo Repository mới
1. Đăng nhập GitHub
2. Nhấn dấu **"+"** góc trên phải → **"New repository"**
3. Đặt tên: `telegram-bot`
4. Chọn **"Public"**
5. Tick vào **"Add a README file"**
6. Nhấn **"Create repository"**

### 2.3. Upload code
1. Trong repository vừa tạo, nhấn **"Add file"** → **"Upload files"**
2. Kéo thả TẤT CẢ các file sau vào (KHÔNG kéo thư mục, chỉ kéo các file bên trong):
   - `app.py`
   - `config.py`
   - `ai_service.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `render.yaml`
3. Nhấn **"Commit changes"** (nút xanh bên dưới)

---

## 🚀 Bước 3: Deploy lên Render (MIỄN PHÍ)

### 3.1. Tạo tài khoản Render
1. Vào https://render.com
2. Nhấn **"Get Started for Free"**
3. Chọn **"GitHub"** để đăng ký (nhanh nhất)
4. Cho phép Render truy cập GitHub của anh

### 3.2. Tạo Web Service mới
1. Sau khi đăng nhập, nhấn **"New +"** ở góc trên → chọn **"Web Service"**
2. Chọn **"Build and deploy from a Git repository"** → nhấn **"Next"**
3. Tìm và chọn repository `telegram-bot` của anh → nhấn **"Connect"**

### 3.3. Cấu hình dịch vụ
Điền các thông tin sau:

| Mục | Điền gì |
|-----|---------|
| Name | `agent-cua-tien` (hoặc tên gì anh thích) |
| Region | Chọn `Singapore` (gần Việt Nam nhất) |
| Branch | `main` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:flask_app --bind 0.0.0.0:$PORT` |
| Instance Type | Chọn **"Free"** |

### 3.4. Thêm biến môi trường (QUAN TRỌNG!)
Kéo xuống tìm phần **"Environment Variables"**, nhấn **"Add Environment Variable"** và thêm:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `8787881290:AAGBgMl-rEXEO6frOXMdD9bmMfVsVk3vXNs` |
| `GEMINI_API_KEY` | Chuỗi key Gemini anh lấy ở Bước 1.1 |
| `OPENROUTER_API_KEY` | Chuỗi key OpenRouter anh lấy ở Bước 1.2 |

### 3.5. Deploy!
1. Nhấn **"Create Web Service"** (nút cuối trang)
2. Đợi 2-5 phút để Render cài đặt
3. Khi thấy trạng thái **"Live"** (xanh lá) là thành công!

---

## 🔗 Bước 4: Kích hoạt Webhook (LÀM 1 LẦN DUY NHẤT)

Sau khi deploy thành công, anh cần kích hoạt webhook:

1. Nhìn trên trang Render, tìm URL của service (dạng: `https://agent-cua-tien-xxxx.onrender.com`)
2. Mở trình duyệt, truy cập: `https://agent-cua-tien-xxxx.onrender.com/set_webhook`
3. Nếu thấy dòng "Webhook set to: ..." là thành công!

---

## ✅ Bước 5: Kiểm tra bot

1. Mở Telegram
2. Tìm bot `@spVNP_bot`
3. Nhấn **Start** hoặc gõ `/start`
4. Gửi tin nhắn bất kỳ để test!

---

## ⚡ Giới hạn và thông tin quan trọng

### Google Gemini Free Tier:
| Giới hạn | Mức cho phép |
|----------|-------------|
| Request/phút | 15 lần |
| Request/ngày | ~1,500 lần |
| Thời hạn | Vĩnh viễn (không hết hạn) |
| Cần thẻ visa? | KHÔNG |

### OpenRouter Free Tier (dự phòng):
| Giới hạn | Mức cho phép |
|----------|-------------|
| Request/phút | 20 lần |
| Request/ngày | 50 lần (nếu chưa nạp $10 thì bị giới hạn) |
| Thời hạn | Vĩnh viễn |
| Cần thẻ visa? | KHÔNG |

### Render Free Tier:
| Giới hạn | Mức cho phép |
|----------|-------------|
| Số service | Tối đa 25 |
| RAM | 512 MB |
| Bandwidth | 5 GB/tháng |
| Sleep | Bot ngủ sau 15 phút không ai nhắn |
| Thức dậy | ~30-50 giây khi có tin nhắn mới |
| Thời hạn | Vĩnh viễn |
| Cần thẻ visa? | KHÔNG |

---

## 💡 Cách bot hoạt động

1. Anh nhắn tin cho bot trên Telegram
2. Telegram gửi tin nhắn đến server Render (webhook)
3. Server nhận tin → gọi Gemini AI để tạo câu trả lời
4. Nếu Gemini lỗi → tự động chuyển sang OpenRouter
5. Bot gửi câu trả lời về cho anh

**Về việc bot "ngủ":** Render free tier sẽ tắt bot sau 15 phút không có ai nhắn. Khi anh nhắn tin mới, Telegram sẽ "đánh thức" bot dậy. Tin nhắn đầu tiên sau khi bot ngủ sẽ chậm khoảng 30-50 giây, nhưng sau đó bot trả lời ngay lập tức.

---

## 🔮 Mở rộng trong tương lai

Code được thiết kế dạng module, sau này có thể thêm:
- 🖼️ Dịch hình ảnh (dùng Gemini Vision)
- 👥 Lệnh tag all trong nhóm
- 🌐 Dịch thuật đa ngôn ngữ
- 📊 Tóm tắt văn bản
- 🔗 Kết hợp với bot hiện tại của anh

---

## ❓ Câu hỏi thường gặp

**Q: Tổng cộng mất phí gì không?**
A: KHÔNG! 100% miễn phí. Không cần thẻ visa ở bất kỳ bước nào.

**Q: Bot có chạy mãi không?**
A: Có! Render free tier không giới hạn thời gian. Bot chỉ "ngủ" khi không ai nhắn 15 phút, nhưng tự thức khi có tin nhắn mới.

**Q: Nếu Gemini hết quota thì sao?**
A: Bot tự động chuyển sang OpenRouter (dự phòng). Anh không cần làm gì cả.

**Q: Anh quên API key thì sao?**
A: Vào lại trang tạo key (Bước 1) để tạo key mới, rồi cập nhật trên Render (vào Settings → Environment).

**Q: Muốn thêm tính năng mới?**
A: Nhờ em (Manus) giúp! Em sẽ viết code mới và hướng dẫn anh cập nhật.

---

## 📞 Hỗ trợ

Nếu anh gặp khó khăn, cứ hỏi em nha! Em sẽ hướng dẫn từng bước! 😊

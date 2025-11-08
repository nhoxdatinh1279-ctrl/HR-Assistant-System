# 🚀 Deploy Vercel - Quick Start (5 phút)

## ✅ Bước 1: Truy cập Vercel
1. Mở: https://vercel.com/signup
2. Click "Continue with GitHub"
3. Authorize Vercel to access GitHub
4. Hoàn thành setup

---

## ✅ Bước 2: Import Project

1. Sau khi login, truy cập: https://vercel.com/new
2. Bạn sẽ thấy:"Import Git Repository"
3. Tìm và click: **HR-Assistant-System**

---

## ✅ Bước 3: Configure Project

### 3.1 Root Directory
- Tìm section "Root Directory"
- Thay đổi thành: `./frontend`
- Click "Edit" rồi chọn `frontend` folder

### 3.2 Build & Development Settings
- **Framework**: Next.js (sẽ tự detect)
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)
- **Install Command**: `npm install` (default)

**Nên để mặc định, không thay đổi!**

---

## ✅ Bước 4: Environment Variables (QUAN TRỌNG!)

Trong "Environment Variables" section, thêm:

```
Name: NEXT_PUBLIC_API_URL
Value: http://localhost:8000
```

**Ghi chú**: 
- Nếu deploy backend trên Render sau, update giá trị này
- VD: `https://hr-assistant-api.onrender.com`

---

## ✅ Bước 5: Deploy!

1. Click "Deploy" button
2. Chờ build complete (~2-5 phút)
3. Vercel sẽ cấp URL: `https://[your-project].vercel.app`

---

## ✅ Bước 6: Xác Minh

1. Truy cập URL bạn vừa nhận được
2. Kiểm tra:
   - ✅ UI hiển thị đúng
   - ✅ Không có lỗi console (F12 → Console tab)
   - ✅ Chat box, CV upload visible

---

## 🔗 Links Quan Trọng

| Bước | Link |
|------|------|
| Sign Up | https://vercel.com/signup |
| Import Project | https://vercel.com/new |
| Dashboard | https://vercel.com/dashboard |
| GitHub Repo | https://github.com/nhoxdatinh1279-ctrl/HR-Assistant-System |

---

## ⚙️ Tiếp Theo: Deploy Backend (Optional)

Nếu bạn muốn frontend thực sự kết nối backend:

### Option 1: Local Backend (Đơn giản)
- Giữ backend chạy ở máy local
- `NEXT_PUBLIC_API_URL=http://localhost:8000` (current)
- Chỉ dùng locally, không thực tế cho production

### Option 2: Render.com (Khuyên dùng)
1. Truy cập: https://render.com/signup
2. "New Web Service"
3. Connect GitHub repo
4. Settings:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `cd backend && python run.py`
5. Add env vars (AZURE keys, etc.)
6. Deploy
7. Copy URL, cập nhật `NEXT_PUBLIC_API_URL` trong Vercel

---

## 📝 Lưu Ý

- **Vercel free tier**: OK cho frontend
- **Build time**: ~2-5 phút
- **Automatic deploys**: Mỗi push lên `main` tự deploy
- **Domain tùy chỉnh**: Settings → Domains (nếu có domain riêng)

---

## 🎉 Done!

Frontend của bạn đã live trên Vercel!

**URL Frontend**: `https://[your-project].vercel.app`

Để frontend kết nối backend, cần setup backend trên Render/AWS/Azure tương tự.

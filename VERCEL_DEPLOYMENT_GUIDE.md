# 🚀 Hướng Dẫn Deploy Lên Vercel

## 📋 Yêu Cầu
- ✅ GitHub Repository: https://github.com/nhoxdatinh1279-ctrl/HR-Assistant-System
- ✅ Git đã cài đặt và project đã push
- ✅ Vercel account (tạo miễn phí tại vercel.com)

---

## 🎯 Bước 1: Chuẩn Bị Backend

### Option A: Deploy Backend trên Render (Khuyên dùng)
1. Truy cập: https://render.com
2. Tạo account + login
3. Click "New +" → "Web Service"
4. Connect GitHub repository
5. Cấu hình:
   - **Name**: `hr-assistant-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python run.py`
   - **Plan**: Free
6. Thêm Environment Variables:
   ```
   AZURE_OPENAI_API_KEY=<your_key>
   AZURE_OPENAI_ENDPOINT=<your_endpoint>
   LLM_DEPLOYMENT=GPT-5-mini
   EMBEDDING_DEPLOYMENT=GPT-5-mini
   ```
7. Click "Create Web Service"
8. Chờ deploy xong, copy URL (vd: `https://hr-assistant-api.onrender.com`)

### Option B: Dùng Backend Hiện Tại (Local)
- Giữ backend chạy ở local/máy chủ khác
- Frontend sẽ kết nối tới nó

---

## 🌐 Bước 2: Deploy Frontend Lên Vercel

### 2.1 Tạo Vercel Account
1. Truy cập: https://vercel.com
2. Click "Sign Up" → "Continue with GitHub"
3. Authorize Vercel để access GitHub
4. Hoàn thành setup

### 2.2 Deploy Project
1. Sau khi login Vercel, click "Add New..." → "Project"
2. Chọn repository: **HR-Assistant-System**
3. Configure Project:
   ```
   Framework Preset: Next.js ✅
   Root Directory: ./frontend
   Build Command: npm run build (default)
   Output Directory: .next (default)
   Install Command: npm install (default)
   ```

### 2.3 Environment Variables (QUAN TRỌNG)
Trong Vercel dashboard, chọn project → "Settings" → "Environment Variables"

Thêm:
```
NEXT_PUBLIC_API_URL = https://hr-assistant-api.onrender.com
```

(Thay bằng URL backend thực tế của bạn)

### 2.4 Deploy
- Click "Deploy"
- Chờ build xong (2-5 phút)
- Vercel sẽ cấp cho bạn URL: `https://your-project-name.vercel.app`

---

## 🔄 Bước 3: Cấu Hình CORS (Backend)

Nếu backend không chấp nhận request từ Vercel frontend, thêm CORS settings vào `backend/app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",  # Vercel domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📤 Bước 4: Update GitHub & Auto-Deploy

### 4.1 Commit & Push Changes
```bash
cd "c:\Users\lethu\OneDrive\Máy tính\AI\WORKSHOP 4"
git add frontend/vercel.json frontend/.env.example
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### 4.2 Automatic Deployments
- Vercel tự động deploy khi bạn push lên `main` branch
- Mỗi push = một deployment mới
- Xem history tại: Vercel Dashboard → Deployments

---

## ✅ Kiểm Tra Deployment

### Frontend
1. Truy cập: `https://your-project.vercel.app`
2. Nên thấy:
   - ✅ HR Assistant UI
   - ✅ Chat Box
   - ✅ CV Upload
   - ✅ Language Toggle

### Backend Connectivity
1. Mở DevTools (F12)
2. Vào tab Console
3. Test API call:
```javascript
fetch('https://your-backend-api.com/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'Hello', language: 'en'})
})
.then(r => r.json())
.then(d => console.log(d))
```

---

## 🔧 Troubleshooting

### "NEXT_PUBLIC_API_URL is not defined"
**Fix**: Thêm vào `frontend/pages/_app.jsx`:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### "CORS error when calling backend"
**Fix**: Thêm CORS middleware vào backend như phần 3

### "Build failed"
**Fix**: 
1. Check logs trong Vercel Dashboard
2. Đảm bảo `frontend/package.json` có đúng dependencies
3. Chạy `npm install` locally để test

### "Backend không respond"
**Fix**:
1. Kiểm tra backend còn chạy không
2. Cập nhật `NEXT_PUBLIC_API_URL` trong Vercel settings
3. Test backend URL trực tiếp trong browser

---

## 📊 Project Links (Sau Deploy)

| Component | URL |
|-----------|-----|
| Frontend | https://your-project.vercel.app |
| Backend API | https://your-api.onrender.com |
| GitHub | https://github.com/nhoxdatinh1279-ctrl/HR-Assistant-System |
| Vercel Dashboard | https://vercel.com/dashboard |
| Render Dashboard | https://dashboard.render.com |

---

## 🚀 Tiếp Theo (Optional)

### Domain Tùy Chỉnh
1. Mua domain tại Namecheap, GoDaddy, etc.
2. Vercel settings → "Domains" → Add custom domain
3. Update DNS records

### Monitoring & Analytics
- Vercel: Built-in analytics, speed insights
- Backend: Add logging, monitoring tools

### CI/CD Pipeline
- GitHub Actions
- Automated testing trước deploy

### Database (Nếu cần)
- PostgreSQL trên Railway/Render
- MongoDB Atlas (cloud)
- Firebase Realtime Database

---

## 📞 Support

- **Vercel Help**: https://vercel.com/docs
- **Render Help**: https://render.com/docs
- **Next.js Deployment**: https://nextjs.org/docs/deployment

---

**Chúc mừng! 🎉 Bạn đã sẵn sàng deploy!**

Sau khi hoàn tất:
1. Share frontend URL với team
2. Monitor performance tại Vercel Dashboard
3. Continue developing, push to main = auto-deploy

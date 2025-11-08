# 📤 Hướng Dẫn Upload Project Lên Git

## 🚀 Bước 1: Cài Đặt Git (Nếu Chưa Có)

### Trên Windows:
1. Tải Git from: https://git-scm.com/download/win
2. Chạy installer và chọn "Git Bash"
3. Chọn "Use Git from Windows Command Prompt"
4. Hoàn thành cài đặt

### Xác Nhận Cài Đặt:
```bash
git --version
```

---

## 🔐 Bước 2: Cấu Hình Git

### Thiết Lập Username & Email:
```bash
git config --global user.name "Your Full Name"
git config --global user.email "your-email@example.com"
```

### Kiểm Tra Cấu Hình:
```bash
git config --global --list
```

---

## 📁 Bước 3: Khởi Tạo Repository

### Tại Thư Mục Project:
```bash
cd "c:\Users\lethu\OneDrive\Máy tính\AI\WORKSHOP 4"
git init
```

---

## 🚫 Bước 4: Tạo .gitignore (Loại Bỏ Các File Không Cần)

Tạo file `.gitignore` trong thư mục project:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.next/

# Environment Variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
backend/embeddings/faiss_index/
*.pdf
*.docx

# Logs
*.log
```

### Lệnh Tạo File:
```bash
# Windows PowerShell
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
.next/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store

# Project specific
backend/embeddings/faiss_index/
"@ | Out-File -FilePath .gitignore -Encoding utf8
```

---

## ✅ Bước 5: Thêm Files Vào Git

### Thêm Tất Cả Files:
```bash
git add .
```

### Kiểm Tra Files Sẽ Được Commit:
```bash
git status
```

---

## 💾 Bước 6: Commit Lần Đầu

```bash
git commit -m "Initial commit: HR Assistant Chatbot with RAG

- FastAPI backend with LangChain RAG system
- Next.js frontend with multi-language support
- CV evaluation engine with intelligent skill matching
- Azure OpenAI integration with fallback mechanisms
- FAISS vector database for semantic search"
```

---

## 🌐 Bước 7: Tạo Remote Repository

### Trên GitHub:
1. Truy cập: https://github.com/new
2. Repository name: `HR-Assistant-Chatbot` (hoặc tên khác)
3. Description: "AI-powered HR Assistant with RAG system for CV evaluation and policy chatbot"
4. Chọn "Public" hoặc "Private"
5. **Không** tick "Add a README file"
6. Click "Create repository"

### Copy Remote URL:
- HTTPS: `https://github.com/YOUR-USERNAME/HR-Assistant-Chatbot.git`
- SSH: `git@github.com:YOUR-USERNAME/HR-Assistant-Chatbot.git`

---

## 🔗 Bước 8: Kết Nối Với Remote

```bash
# Thay YOUR-USERNAME bằng username GitHub của bạn
git remote add origin https://github.com/YOUR-USERNAME/HR-Assistant-Chatbot.git

# Kiểm Tra Remote:
git remote -v
```

---

## 📤 Bước 9: Push Lên GitHub

### Lần Đầu Tiên:
```bash
git branch -M main
git push -u origin main
```

### Sau Đó (Để Push Changes):
```bash
git push origin main
```

---

## 🔄 Bước 10: Xác Minh Upload Thành Công

1. Truy cập: `https://github.com/YOUR-USERNAME/HR-Assistant-Chatbot`
2. Kiểm Tra Xem Tất Cả Files Có Ở Đây Không:
   - ✅ backend/
   - ✅ frontend/
   - ✅ README.md
   - ✅ .gitignore
   - ✅ Các file documentation

---

## 📋 Complete Command Summary

### Dùng Cho Copy-Paste:

```bash
# 1. Di Chuyển Tới Thư Mục Project
cd "c:\Users\lethu\OneDrive\Máy tính\AI\WORKSHOP 4"

# 2. Cấu Hình Git (Lần Đầu)
git config --global user.name "Your Full Name"
git config --global user.email "your-email@example.com"

# 3. Khởi Tạo Repository
git init

# 4. Tạo .gitignore (Optional)
# Nếu chưa có file .gitignore

# 5. Thêm Tất Cả Files
git add .

# 6. Kiểm Tra Status
git status

# 7. Commit Lần Đầu
git commit -m "Initial commit: HR Assistant Chatbot with RAG"

# 8. Thêm Remote (Thay YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/HR-Assistant-Chatbot.git

# 9. Rename Branch Thành Main (Nếu Cần)
git branch -M main

# 10. Push Lên GitHub
git push -u origin main
```

---

## 🐛 Troubleshooting

### Lỗi: "fatal: not a git repository"
**Giải Pháp:**
```bash
git init
```

### Lỗi: "fatal: Authentication failed"
**Giải Pháp:** (Dùng SSH Key hoặc Personal Access Token)
```bash
# Thay đổi Remote từ HTTPS sang SSH:
git remote set-url origin git@github.com:YOUR-USERNAME/HR-Assistant-Chatbot.git
```

### Lỗi: "Updates were rejected because the remote contains work"
**Giải Pháp:**
```bash
git pull origin main
git push origin main
```

### Thấy `.env` Files Được Commit
**Giải Pháp:**
```bash
# Xóa file đã commit nhưng giữ file local
git rm --cached .env
git commit -m "Remove .env from git tracking"
```

---

## 🎯 Tiếp Theo (Optional)

### Tạo README.md Chi Tiết
```bash
# Dùng file README.md đã có hoặc tạo mới
```

### Tạo Release/Tags
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

### Tạo .github/workflows/ Cho CI/CD
```bash
# Optional: GitHub Actions workflows
```

---

## ✨ Best Practices

1. **Commit Thường Xuyên**: Commit mỗi feature hoàn thành
2. **Viết Commit Message Tốt**: Mô tả rõ ràng những thay đổi
3. **Sử Dụng Branches**: `main` cho production, `develop` cho development
4. **Code Review**: Trước khi merge vào `main`
5. **Tags**: Đánh dấu các phiên bản stable

---

## 📚 Tài Liệu Tham Khảo

- GitHub Guide: https://guides.github.com/
- Git Documentation: https://git-scm.com/doc
- GitHub Student Pack: https://education.github.com/pack

---

## 🎉 Chúc Mừng!

Bạn đã sẵn sàng để upload project lên GitHub!

**Tiếp Theo:**
1. Chia sẻ link repository với team
2. Thêm collaborators nếu cần
3. Bắt đầu track changes
4. Deploy từ GitHub (optional)

---

*Hướng Dẫn Được Tạo: 08/11/2025*

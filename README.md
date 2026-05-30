# Mini Social Network

Mạng xã hội mini theo kiến trúc Layered (Presentation → Business → Persistence → Database).

## Kiến trúc
- Backend: Python + FastAPI + asyncpg
- Database: PostgreSQL
- Auth: JWT với `python-jose` + hash mật khẩu `passlib[bcrypt]`
- Frontend: HTML/CSS/JavaScript thuần, gọi API qua `fetch()`

## Cấu trúc thư mục
```
mini-social/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   │   ├── deps.py
│   │   └── routers/auth.py
│   ├── services/auth_service.py
│   ├── repositories/user_repo.py
│   ├── schemas/user.py
│   └── core/
│       ├── security.py
│       ├── responses.py
│       └── exceptions.py
├── migrations/001_init.sql
├── frontend/
│   ├── index.html
│   ├── feed.html
│   ├── css/style.css
│   └── js/
│       ├── api.js
│       └── auth.js
├── .env.example
├── requirements.txt
└── README.md
```

## Quick Start
### Lần đầu tiên (Setup toàn bộ)
1. Mở PowerShell tại thư mục dự án rồi chạy script setup:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\setup.ps1
   ```
   Script này sẽ:
   - Tạo virtual environment (`venv/`)
   - Kích hoạt `venv`
   - Cài tất cả dependency từ `requirements.txt`

2. Đảm bảo PostgreSQL đang chạy, rồi tạo database:
   ```powershell
   createdb mini_social
   ```

3. Copy `.env.example` → `.env` và chỉnh sửa giá trị:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/mini_social
   JWT_SECRET=ReplaceWithStrongSecret
   JWT_EXPIRE_MINUTES=60
   ```

4. Chạy migration để tạo schema:
   ```powershell
   psql $env:DATABASE_URL -f migrations/001_init.sql
   ```
   *Hoặc sử dụng Terminal chung nếu `DATABASE_URL` đã set global*

### Chạy ứng dụng (sau này)
```powershell
.\run.ps1
```
Script này tự động kích hoạt `venv` rồi chạy FastAPI server.

Server sẽ chạy tại: **`http://127.0.0.1:8000/index.html`**

### Cấu hình VS Code (tùy chọn — auto kích hoạt venv)
`.vscode/settings.json` đã được tạo sẵn, VS Code sẽ tự nhận diện Python từ `venv/Scripts/python.exe`.

## Các endpoint auth đã triển khai
- `POST /auth/register` — đăng ký người dùng
- `POST /auth/login` — đăng nhập, trả JWT
- `GET  /auth/me` — lấy thông tin người dùng hiện tại

## Ghi chú
- Frontend chỉ dùng HTML/CSS/JS thuần.
- Router chỉ gọi service, service chỉ gọi repository.
- Module Post / Social / Feed đã chuẩn bị khung sẵn nhưng chưa triển khai logic.

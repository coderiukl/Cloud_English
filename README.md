# Hướng dẫn chạy project Django

## 1. Cài đặt môi trường

### Cài Python
- Cài Python >= 3.8: https://www.python.org/downloads/
- Kiểm tra bằng lệnh:
  ```bash
  python --version
  ```

### Tạo Virtual Environment
- Tạo môi trường ảo:
  ```bash
  python -m venv venv
  ```
- Kích hoạt:
  - Windows:
    ```bash
    .\venv\Scripts\activate
    ```
  - MacOS/Linux:
    ```bash
    source venv/bin/activate
    ```

### Cài package
- Cài đặt đầy đủ package cần thiết:
  ```bash
  pip install -r requirements.txt
  ```


## 2. Cấu hình Database

### Chạy migrate
- Tạo database ban đầu:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### (Tuỳ chọn) Tạo superuser
- Đăng nhập admin:
  ```bash
  python manage.py createsuperuser
  ```


## 3. Chạy server local

### Khởi chạy server
```bash
python manage.py runserver
```

- Truy cập trang web tại: http://127.0.0.1:8000/
- Truy cập admin panel: http://127.0.0.1:8000/admin/


# Linux Server Deploy Guide — bugun.uz backend

## 1. Server tayyor qilish

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib
```

## 2. PostgreSQL setup

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE bugun;
CREATE USER bugun WITH PASSWORD 'bugun';
GRANT ALL PRIVILEGES ON DATABASE bugun TO bugun;
\q
```

## 3. Repo clone

```bash
cd /var/www
sudo git clone https://github.com/dovudbek7/bugun.uz-backend.git bugunuz
sudo chown -R $USER:$USER /var/www/bugunuz
cd /var/www/bugunuz
```

## 4. Virtual environment va dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. .env fayl

```bash
nano /var/www/bugunuz/.env
```

Ichiga yoz:

```
SECRET_KEY=random-50-char-string
DEBUG=False
ALLOWED_HOSTS=serverip_yoki_domen,bugunuz.uz
DATABASE_URL=postgres://bugunuz:kuchli_parol@localhost:5432/bugunuz
BOT_TOKEN=yangi_bot_token
MINI_APP_URL=https://bugunuz.vercel.app/
```

## 6. Migrations va static

```bash
source /var/www/bugunuz/venv/bin/activate
cd /var/www/bugunuz
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 7. Gunicorn systemd service

```bash
sudo nano /etc/systemd/system/bugunuz.service
```

```ini
[Unit]
Description=bugunuz Django
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/bugunuz
EnvironmentFile=/var/www/bugunuz/.env
ExecStart=/var/www/bugunuz/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

## 8. Bot systemd service

```bash
sudo nano /etc/systemd/system/bugunuz-bot.service
```

```ini
[Unit]
Description=bugunuz Telegram Bot
After=network.target bugunuz.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/bugunuz
EnvironmentFile=/var/www/bugunuz/.env
ExecStart=/var/www/bugunuz/venv/bin/python -m apps.telegram_bot.run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 9. Servicelarni ishga tushirish

```bash
sudo systemctl daemon-reload
sudo systemctl enable bugunuz bugunuz-bot
sudo systemctl start bugunuz bugunuz-bot

# status tekshirish
sudo systemctl status bugunuz
sudo systemctl status bugunuz-bot
```

## 10. Nginx setup

```bash
sudo nano /etc/nginx/sites-available/bugunuz
```

```nginx
server {
    listen 80;
    server_name serverip_yoki_domen;

    location /static/ {
        alias /var/www/bugunuz/staticfiles/;
    }

    location /media/ {
        alias /var/www/bugunuz/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/bugunuz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 11. SSL (domen bo'lsa)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d bugunuz.uz -d www.bugunuz.uz
```

## 12. Yangilash (deploy update)

```bash
cd /var/www/bugunuz
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart bugunuz bugunuz-bot
```

## Foydali buyruqlar

```bash
# loglar
sudo journalctl -u bugunuz -f
sudo journalctl -u bugunuz-bot -f

# restart
sudo systemctl restart bugunuz
sudo systemctl restart bugunuz-bot

# nginx log
sudo tail -f /var/log/nginx/error.log
```

#!/bin/sh
CERT="/etc/nginx/certs/live/sbr-obr.ru/fullchain.pem"
CONFIG="/etc/nginx/conf.d/default.conf"

# Если сертификата нет — используем HTTP-конфигурацию
if [ -f "$CERT" ]; then
    echo "Certificate found. Using HTTPS configuration."
    cp /etc/nginx/conf.d/https/default-https.conf $CONFIG
else
    echo "Certificate not found. Using HTTP configuration."
    cp /etc/nginx/conf.d/http/default-http.conf $CONFIG
fi

# Запускаем nginx в фоне
nginx

# Периодически проверяем наличие сертификата и, если он появился, переключаем конфигурацию
while true; do
    if [ -f "$CERT" ]; then
        # Если текущий конфиг не содержит HTTPS-части, переключаем его
        if ! grep -q "listen 443 ssl" $CONFIG; then
            echo "Certificate detected during runtime. Switching to HTTPS configuration."
            cp /etc/nginx/conf.d/https/default-https.conf $CONFIG
            nginx -s reload
        fi
    fi
    sleep 60
done

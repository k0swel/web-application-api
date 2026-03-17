# Инструкция по деплою API
1. Зайти на сервер API по SSH (**ssh -J debian@37.18.14.43 debian@192.168.0.204**)
2. Запустить bash скрипт ( **/home/debian/api/run_api.sh &**)

UPD: написал systemd unit файл **web-lab1-api.service** , так удобнее:
```
[Unit]
Description="API сервис web-lab1"
After=network.target

[Service]
Type=simple
User=debian
Group=debian
ExecStart=/home/debian/api/run_api.sh

[Install]
WantedBy=multi-user.target
```

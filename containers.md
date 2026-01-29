# Start up commands
podman pod create --name bot-server --userns auto  -p 8443:443 -p 8080:80
podman run -d --name nginx --pod bot-server  --mount  type=bind,src=/home/tgbot/ssl,target=/ssl,ro  -v /home/tgbot/misbot/nginx/nginx.conf:/etc/nginx/nginx.conf:ro  nginx
podman run -d --name bot-app --pod bot-server -v misbot-db:/app/db --env-file /home/tgbot/misbot/.env   localhost/misbot:application-containerize
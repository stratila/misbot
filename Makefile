.PHONY: build up down restart logs ps clean

POD_NAME := bot-server
NGINX_NAME := nginx
APP_NAME := bot-app

SSL_DIR := /home/tgbot/ssl
NGINX_CONF := /home/tgbot/misbot/nginx/nginx.conf
ENV_FILE := /home/tgbot/misbot/.env

IMAGE_APP := localhost/misbot:latest
IMAGE_NGINX := nginx
VOLUME_DB := misbot-db

build:
	@echo "Building application image..."
	podman build -t $(IMAGE_APP) .

up: build
	@echo "Starting pod $(POD_NAME)..."
	-@podman pod create --name $(POD_NAME) --userns auto -p 8443:443 -p 8080:80

	@echo "Starting nginx..."
	-@podman run -d \
		--name $(NGINX_NAME) \
		--pod $(POD_NAME) \
		--mount type=bind,src=$(SSL_DIR),target=/ssl,ro \
		-v $(NGINX_CONF):/etc/nginx/nginx.conf:ro \
		$(IMAGE_NGINX)

	@echo "Starting app..."
	-@podman run -d \
		--name $(APP_NAME) \
		--pod $(POD_NAME) \
		-v $(VOLUME_DB):/app/db \
		--env-file $(ENV_FILE) \
		$(IMAGE_APP)

down:
	@echo "Stopping and removing pod $(POD_NAME)..."
	-@podman pod stop $(POD_NAME)
	-@podman pod rm $(POD_NAME)

restart: down up

logs:
	podman pod logs $(POD_NAME)

logs-app:
	podman logs -f $(APP_NAME)

ps:
	podman ps --pod

clean: down
	@echo "Removing volume $(VOLUME_DB)..."
	-@podman volume rm $(VOLUME_DB)

.env
```
TELEGRAM_BOT_TOKEN=
WEBHOOK_SECRET_TOKEN=
ENVIRONMENT=
WEBHOOK_URL=
SQLITE_DB_FILENAME=
MANAGED_CHAT_IDS=
ADMIN_USER_ID=
```

# How to Run the Project Locally

## Bot Creation and Receiving Your IDs

1. In the Telegram app, go to [@BotFather] and create your bot using the `/newbot` command. After providing your bot name and username, you will receive a token in the format like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`.

2. After that, send a message to your bot and add your bot to any channel as an admin.

3. Then go to `https://api.telegram.org/bot<token>/getUpdates`, replacing `<token>` with your actual token.

4. You will see a response with two updates in the results list. Copy your user ID from the `"message"` update object and the channel ID from the `"my_chat_member"` update object.

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 336436588,
      "message": {
        "message_id": 2,
        "from": {
          "id": "12345" // <<-- Your user ID
        }
      }
    },
    {
      "update_id": 336436589,
      "my_chat_member": {
        "chat": {
          "id": "-12345" // <<-- Your channel ID
        }
      }
    }
  ]
}
```

## Environment File Creation

1. Create a `.dev.env` file in the project directory.

2. Populate it with the following environment variables using your actual values instead of the placeholders:

```
ENVIRONMENT=dev
TELEGRAM_BOT_TOKEN=<Your Bot Token>
ADMIN_USER_ID=<Your user ID, example: "12345">
MANAGED_CHAT_IDS=<Your channel ID, example: "-12345">

SQLITE_DB_FILENAME=/app/db/botdb.sqlite

# The following can be ignored; they are used in production.
# WEBHOOK_URL=
# WEBHOOK_SECRET_TOKEN=
```


## Run Project

You can use Docker or Podman to run the project locally.

```bash
# Build the image
docker compose -f container-compose.yml build 

# Start containers
docker compose -f container-compose.yml up -d 

# Stop containers
docker compose -f container-compose.yml down
```

Starting the containers currently runs only one `app` container, which performs database migrations and starts the bot app and web server in the event loop:

```bash
# Start containers
docker compose -f container-compose.yml up -d
```

To stop the containers:

```bash
# Stop containers
docker compose -f container-compose.yml down
```

### Restarting the Container After Editing Code

If you make changes to the code and want them to take effect, you can restart the `app` container without rebuilding the entire image:

```bash
# Restart the app container
docker compose -f container-compose.yml restart app
```

This will stop and start the container, applying your code changes immediately.


## Editing DB Schema and Applying Migrationgs

TBD



[@BotFather]: https://t.me/BotFather
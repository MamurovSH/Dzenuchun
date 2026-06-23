import os

# Bot token - BotFather dan olingan token
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin ID - sizning Telegram ID ingiz
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# Bot nomi
BOT_NAME = "🎬 Kino Bot"

# Sahifa boshida ko'rsatiladigan filmlar soni
MOVIES_PER_PAGE = 5

# Kanal username (agar majburiy obuna bo'lsa)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@your_channel")

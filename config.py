# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os

# Login feature, if you want then True , if you don't want then False
LOGIN_SYSTEM = bool(os.environ.get('LOGIN_SYSTEM', True)) # True or False

if LOGIN_SYSTEM == False:
    # if login system is False then fill your tg account session below 
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
else:
    STRING_SESSION = None

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "6073523936"))

# Your Channel Id In Which Bot Upload Downloaded Video/File/Message etc.
# And Make Your Bot Admin In this channel with full rights.
# if you don't want to upload in channel then leave it blank don't fill anything.
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "vjsavecontentbot")

# Increase time as much as possible to avoid floodwait, spamming and tg account ban issues.
WAITING_TIME = int(os.environ.get("WAITING_TIME", "10")) # time in seconds

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

# ==================== PREMIUM SYSTEM CONFIG ====================

# Premium Payment Settings
UPI_ID = "aryan0278@ptyes"

# Paste your QR code base64 here after converting from https://www.base64-image.de/
UPI_QR_BASE64 = "PASTE_YOUR_BASE64_STRING_HERE"

# Free User Limits
FREE_USER_DAILY_LIMIT = 10  # Maximum downloads per day for free users
FREE_USER_WAIT_TIME = 0  # No artificial wait time - let Telegram decide speed

# Premium User Settings
PREMIUM_USER_WAIT_TIME = 0  # No wait time for premium users
MAX_BATCH_SIZE_PREMIUM = 500  # Maximum files per batch for premium users

# Premium Plans (in rupees)
PREMIUM_PLANS = {
    "3_hours": {"price": 15, "days": 0.125, "title": "3 Hours"},  # 3 hours = 0.125 days
    "1_day": {"price": 30, "days": 1, "title": "1 Day"},
    "3_days": {"price": 40, "days": 3, "title": "3 Days"},
    "7_days": {"price": 80, "days": 7, "title": "7 Days"},
    "15_days": {"price": 140, "days": 15, "title": "15 Days"},
    "30_days": {"price": 249, "days": 30, "title": "1 Month"},
    "90_days": {"price": 599, "days": 90, "title": "3 Months"}
}

# Support & Community Links
SUPPORT_USERNAME = "aryansmilezzz"
COMMUNITY_GROUP = "https://t.me/CleanYourVibe"

# Progress Update Frequency
PROGRESS_UPDATE_INTERVAL = 50  # Show progress every 50 files

# ==================== END PREMIUM CONFIG ====================

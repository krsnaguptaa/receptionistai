import os

GEMINI_API_KEY    = os.environ.get(
    'GEMINI_API_KEY',
    'AQ.Ab8RN6KfiyBdTEAGPaRmX6F4-c7j-mhYS6xKLo5mQu08N340zw')
WHATSAPP_TOKEN    = os.environ.get(
    'WHATSAPP_TOKEN',
    'your_local_token')
PHONE_NUMBER_ID   = os.environ.get(
    'PHONE_NUMBER_ID',
    'your_local_phone_id')
VERIFY_TOKEN      = os.environ.get(
    'VERIFY_TOKEN',
    'receptionistai2026')
BUSINESS_NAME     = os.environ.get(
    'BUSINESS_NAME',
    'Glamour Studio')
BUSINESS_TYPE     = os.environ.get(
    'BUSINESS_TYPE', 'salon')
BUSINESS_LOCATION = os.environ.get(
    'BUSINESS_LOCATION',
    'Lajpat Nagar, New Delhi')
BUSINESS_HOURS    = os.environ.get(
    'BUSINESS_HOURS',
    'Mon-Sat, 10am to 8pm')
BUSINESS_CLOSED   = ['Sunday']
OWNER_WHATSAPP    = os.environ.get(
    'OWNER_WHATSAPP', '')
GOOGLE_REVIEW_URL = os.environ.get(
    'GOOGLE_REVIEW_URL', '')
WALKIN_BUFFER_PERCENT  = 40
CHURN_DAY_1       = 30
CHURN_DAY_2       = 60
CHURN_DAY_3       = 90
CHURN_DISCOUNT_1  = 10
CHURN_DISCOUNT_2  = 15
CHURN_DISCOUNT_3  = 20
BIRTHDAY_DISCOUNT = 20
AI_MODEL          = "gemini-2.0-flash"
FALLBACK_MESSAGE  = (
    "Ek second! 😊 "
    "Thoda technical issue. "
    "Dobara try karo!")

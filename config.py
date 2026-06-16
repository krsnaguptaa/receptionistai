import os

GEMINI_API_KEY    = os.environ.get(
    'GEMINI_API_KEY',
    'AQ.Ab8RN6IvUOf9BsD4M_BriCj-DzKj1480P5DGFLAaouiQ4mYFhQ')
WHATSAPP_TOKEN    = os.environ.get(
    'WHATSAPP_TOKEN',
    'EAAclVWgdGaIBRiiDQVnLbSBvFSUir3ht0P6VdHHJbdIjz9lWpMj5DQimLKI7gEgIutnaj56sNztYtOyla14GyH8YNotwbQM7hXOKcvPOMcmuvtZAAjZCHvcjDytifNIMdPWfLglmQvgLSIn9S264VWjv7e5fvlqdx2RKkFL1zS33SZAj9LOqWVZCPv2e7WqcSGONEyBUMJPAzklkz1ZAOjSOrEC5ZCQkYZAWQNXALO34vITHvJQXJhB5xBpOmxysZALZASzoCvxdjqHSbQIiuLy00')
PHONE_NUMBER_ID   = os.environ.get(
    'PHONE_NUMBER_ID',
    '1146753105192263')
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
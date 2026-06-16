from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from whatsapp import send_message
import base64
import requests

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_face_and_suggest(
        phone, image_url, style_requested):
    try:
        # Download image from WhatsApp
        img_response = requests.get(
            image_url,
            headers={
                "Authorization":
                f"Bearer {__import__('config').WHATSAPP_TOKEN}"
            })
        img_data = base64.b64encode(
            img_response.content).decode('utf-8')

        prompt = f"""
You are a professional hair stylist AI.

Analyze this person's selfie and:
1. Identify their face shape
   (oval, round, square, heart, oblong)
2. Note their current hair type and length
3. They want: {style_requested}
4. Give specific recommendations for
   this hairstyle on their face shape
5. Mention what will look good and what
   to avoid
6. Keep it friendly and in Hinglish

Format:
Face Shape: [shape]
Current Hair: [description]
For {style_requested}:
✅ What will look amazing: [details]
⚠️ Tips for your face shape: [tips]
👨‍💼 Ask your stylist for: [specific instructions]
"""

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_data
                            }
                        },
                        {"text": prompt}
                    ]
                }
            ]
        )

        analysis = response.text

        # Send analysis to customer
        send_message(phone,
            f"🔍 *AI Style Analysis*\n\n"
            f"{analysis}\n\n"
            f"Book karna hai? 😊\n"
            f"Main slot check karta hoon!")

        return True

    except Exception as e:
        print(f"Image analysis error: {e}")
        send_message(phone,
            "Selfie nahi dekh paya 😅\n"
            "Dobara try karo please!")
        return False

def handle_image_message(phone,
                          image_id,
                          caption):
    try:
        # Get image URL from WhatsApp
        import requests as req
        from config import WHATSAPP_TOKEN
        url_response = req.get(
            f"https://graph.facebook.com"
            f"/v18.0/{image_id}",
            headers={
                "Authorization":
                f"Bearer {WHATSAPP_TOKEN}"
            })
        image_url = url_response.json().get('url')

        if not image_url:
            send_message(phone,
                "Image nahi mili 😅\n"
                "Dobara bhejo please!")
            return

        # Get style from caption or ask
        style = caption or "best hairstyle"

        send_message(phone,
            "📸 Selfie mil gayi!\n"
            "AI analyze kar raha hai... ⏳\n"
            "30 seconds mein batata hoon! 🔍")

        analyze_face_and_suggest(
            phone, image_url, style)

    except Exception as e:
        print(f"Image handle error: {e}")
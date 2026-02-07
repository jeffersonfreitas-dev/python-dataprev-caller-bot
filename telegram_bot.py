import os

import requests
from dotenv import load_dotenv
load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

class TelegramBot:
    def __init__(self):
        self.token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.url = f"{self.base_url}/sendMessage"

    def send_message(self, message):
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }

        try:
            response = requests.post(self.url, json=payload,timeout=20)
            response.raise_for_status()

            result = response.json()
            if result['ok']:
                print(f"✅ Message sent to chat {chat_id}")
                return True
            else:
                print(f"❌ Failed to send message: {result.get('description', 'Unknown error')}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False
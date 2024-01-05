import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
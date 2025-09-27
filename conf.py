from dotenv import load_dotenv
import os
from zoneinfo import ZoneInfo
from datetime import datetime


load_dotenv()

USER = os.getenv('USER')
PASS = os.getenv('PASS')
HOST = os.getenv('HOST', 'localhost')
PORT = os.getenv('PORT', '5432')
DBNAME = os.getenv('DBNAME')
LINKS = os.getenv('LINKS')

links = [i for i in LINKS.split()]

url = f'postgresql+psycopg://{USER}:{PASS}@{HOST}:{PORT}/{DBNAME}'

# link = os.getenv("LINK")
now_utc = datetime.now(ZoneInfo("UTC")).astimezone(ZoneInfo(os.getenv("TMZONE")))
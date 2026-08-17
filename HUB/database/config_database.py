from dotenv import load_dotenv
import os

load_dotenv("./database/.env.database")

host = os.getenv("DB_HOST")
port = int(os.getenv("DB_PORT"))
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_DATABASE")
pool_size = int(os.getenv("DB_POOL_SIZE"))

from dotenv import load_dotenv

import os

load_dotenv()


DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_NAME_2 = os.environ.get('DATABASE_NAME_2')
DATABASE_PORT = os.environ.get('DATABASE_PORT')
DATABASE_OWNER = os.environ.get('DATABASE_OWNER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
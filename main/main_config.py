from datetime import timedelta
import os

class Configuration:
    DATABASE_HOST = 'localhost' if 'DATABASE_HOST' not in os.environ else os.environ['DATABASE_HOST']
    DATABASE_PORT = '5431' if 'DATABASE_PORT' not in os.environ else os.environ['DATABASE_PORT']

    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://postgres:postgres_root_password@{DATABASE_HOST}:{DATABASE_PORT}/main_db'
    JWT_SECRET_KEY = 'JWT_SECRET_KEY'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

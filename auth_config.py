from datetime import timedelta


class Configuration():
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres_root_password@localhost:5432/auth_db'
    JWT_SECRET_KEY = 'JWT_SECRET_KEY'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

from decouple import config
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = config('JWT_SECRET_KEY', cast=str)
    REFRESH_SECRET_KEY: str = config('REFRESH_SECRET_KEY', cast=str)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = config('REFRESH_TOKEN_EXPIRE_MINUTES', cast=int)

    # Database
    SQLALCHEMY_DATABASE_URL: str = config('SQLALCHEMY_DATABASE_URL', cast=str)

    DB_NAME: str = config("DB_NAME", cast=str)
    BACKEND_CORS_ORIGINS: list = config("BACKEND_CORS_ORIGINS", cast=str).split(',')

    AWS_ACCESS_KEY_ID: str = config("AWS_ACCESS_KEY_ID", cast=str)
    AWS_SECRET_ACCESS_KEY: str = config("AWS_SECRET_ACCESS_KEY", cast=str)
    REGION_NAME: str = config("REGION_NAME", cast=str)
    S3_BUCKET_NAME: str = config("S3_BUCKET_NAME", cast=str)

    class Config:
        case_sensitive = True


settings = Settings()

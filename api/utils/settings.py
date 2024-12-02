from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Class to access env variables
    """

    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    DATABASE_URL_TEST: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    REFRESH_TOKEN_EXPIRY: int
    ACCESS_TOKEN_EXPIRY: int

    TEST: str
    APP_NAME: str
    SECRET_KEY: str

    SUPERADMIN_SECRET_ONE: str
    SUPERADMIN_SECRET_TWO: str
    SUPERADMIN_SECRET_THREE: str
    TEST_SUPERADMIN_SECRET: str

    REDIS_URL: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    CELERY_BROKER_URL_TEST: str
    CELERY_RESULT_BACKEND_TEST: str

    MODE: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: str
    MAIL_SERVER: str
    MAIL_FROM: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    model_config: SettingsConfigDict = {"env_file": ".env", "case_sensitive": False}


Config = Settings()

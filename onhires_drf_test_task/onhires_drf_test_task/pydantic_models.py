from pydantic import SecretStr
from pydantic_settings import BaseSettings


class MySQLConnectionSettings(BaseSettings):
    """MySQL connection settings."""

    DB_NAME: SecretStr
    DB_HOST: SecretStr
    DB_PORT: SecretStr
    DB_USER: SecretStr
    DB_PASS: SecretStr

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 10


class ApplicationSettings(BaseSettings):
    """Application settings."""

    SECRET_KEY: SecretStr


application_settings = ApplicationSettings()
mysql_connection_settings = MySQLConnectionSettings()

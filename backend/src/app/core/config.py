from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Catastrophe Exposure Aggregator"
    version: str = "0.1.0"
    debug: bool = False

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ssl: bool = True

    db_secret_arn: str = ""

    cors_origins: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

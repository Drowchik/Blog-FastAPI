import os
from dynaconf import Dynaconf
from pydantic_settings import BaseSettings
from pydantic import AnyUrl

_settings = Dynaconf(
    settings_files=["config.yaml"]
)
_project_timezone = "Europe/Moscow"

_db_dsn = AnyUrl.build(
    scheme="postgresql+asyncpg",
    username=_settings.database.user,
    password=_settings.database.password,
    host=_settings.database.host,
    port=_settings.database.port,
    path=_settings.database.db,
)

class Settings(BaseSettings):
    db_dsn: str
    timezone: str
    secret_key: str
    algorithm: str
    celery_broker: str
    email: str
    password: str
    smtp_host: str
    smtp_port: int
    
settings = Settings(db_dsn=str(_db_dsn), 
                    timezone=_project_timezone, 
                    secret_key=_settings.jwt.secret_key, 
                    algorithm=_settings.jwt.algorithm,
                    celery_broker=_settings.celery.broker,
                    email=_settings.celery.email,
                    password=_settings.celery.password,
                    smtp_host=_settings.celery.smtp_host,
                    smtp_port=_settings.celery.smtp_port
                    )

from typing import Optional
from pydantic import BaseSettings, Field

class ETLSettings(BaseSettings):
    postgres_db: str
    postgres_host: int
    postgres_port: int
    

    class Config:
        env_file = "../.env"

if __name__ == '__main__':
    print(ETLSettings().dict())
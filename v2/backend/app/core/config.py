from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GenAI Learning App"
    # Add other configuration variables as needed

settings = Settings()

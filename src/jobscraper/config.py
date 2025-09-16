from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import os

class EmailConfig(BaseModel):
    email: str
    password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    recipients: List[str] = Field(default_factory=list)

class AppConfig(BaseModel):
    db_path: str = "data/jobs.sqlite"
    user_agent: str = "Mozilla/5.0"
    accept_language: str = "en-US,en;q=0.9"
    email: EmailConfig

    @staticmethod
    def from_env() -> "AppConfig":
        email = os.getenv("JOBMAIL_EMAIL", "")
        password = os.getenv("JOBMAIL_PASSWORD", "")
        smtp = os.getenv("JOBMAIL_SMTP", "smtp.gmail.com")
        port = int(os.getenv("JOBMAIL_PORT", "587"))
        recips = [r.strip() for r in os.getenv("JOBMAIL_RECIPIENTS", "").split(",") if r.strip()]
        cfg = AppConfig(
            db_path=os.getenv("JOBSCRAPER_DB", "data/jobs.sqlite"),
            user_agent=os.getenv("SCRAPER_USER_AGENT", "Mozilla/5.0"),
            accept_language=os.getenv("SCRAPER_ACCEPT_LANGUAGE", "en-US,en;q=0.9"),
            email=EmailConfig(
                email=email, password=password, smtp_server=smtp, smtp_port=port, recipients=recips
            ),
        )
        return cfg

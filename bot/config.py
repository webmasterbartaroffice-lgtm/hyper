import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    WOOCOMMERCE_CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
    WOOCOMMERCE_CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")
    WOOCOMMERCE_BASE_URL = os.getenv("WOOCOMMERCE_BASE_URL", "")

    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.2"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    @classmethod
    def validate(cls) -> None:
        missing = []
        if not cls.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not cls.WOOCOMMERCE_CONSUMER_KEY:
            missing.append("WOOCOMMERCE_CONSUMER_KEY")
        if not cls.WOOCOMMERCE_CONSUMER_SECRET:
            missing.append("WOOCOMMERCE_CONSUMER_SECRET")
        if not cls.WOOCOMMERCE_BASE_URL:
            missing.append("WOOCOMMERCE_BASE_URL")
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")



from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

app = FastAPI()

# Allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load .env
load_dotenv()

# ------------------------
# Defaults
# ------------------------
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def convert(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    # ------------------------
    # Layer 1: Defaults
    # ------------------------
    config = DEFAULTS.copy()

    # ------------------------
    # Layer 2: YAML
    # ------------------------
    with open("config.development.yaml", "r") as f:
        yaml_config = yaml.safe_load(f)
        if yaml_config:
            config.update(yaml_config)

    # ------------------------
    # Layer 3: .env
    # ------------------------
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("APP_LOG_LEVEL"):
        config["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    # ------------------------
    # Layer 4: OS Environment
    # (Assignment values)
    # ------------------------
    config["port"] = int(os.getenv("APP_PORT", "8162"))
    config["debug"] = to_bool(os.getenv("APP_DEBUG", "true"))
    config["api_key"] = os.getenv("APP_API_KEY", "key-2mlblxss3k")

    # ------------------------
    # Layer 5: CLI overrides
    # ------------------------
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            config[key] = convert(key, value)

    # Mask secret
    config["api_key"] = "****"

    return config
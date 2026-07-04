from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}
def to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


def convert(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)
@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    config = DEFAULTS.copy()

    with open("config.development.yaml") as f:
        config.update(yaml.safe_load(f))

    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("APP_LOG_LEVEL"):
        config["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_DEBUG"):
        config["debug"] = to_bool(os.getenv("APP_DEBUG"))

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            config[key] = convert(key, value)

    config["api_key"] = "****"

    return config
"""Строки подключения для локальной демонстрации."""

from __future__ import annotations

import os


POSTGRES_APP_DSN = os.getenv(
    "POSTGRES_APP_DSN",
    "postgresql://app_user:app_password@localhost:5432/db_security",
)

MONGODB_UNAUTH_URI = os.getenv(
    "MONGODB_UNAUTH_URI",
    "mongodb://localhost:27017",
)

MONGODB_APP_URI = os.getenv(
    "MONGODB_APP_URI",
    "mongodb://mongo_app:mongo_app_password@localhost:27017/"
    "secure_app?authSource=secure_app",
)

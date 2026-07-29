"""
=========================================================
Family Expense Manager Pro
Production Configuration
=========================================================
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:

    # ==========================================
    # APP
    # ==========================================

    APP_NAME = os.getenv(
        "APP_NAME",
        "Family Expense Manager Pro"
    )

    APP_VERSION = os.getenv(
        "APP_VERSION",
        "1.0.0"
    )

    APP_ENV = os.getenv(
        "APP_ENV",
        "production"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "False"
    ).lower() == "true"

    # ==========================================
    # STREAMLIT
    # ==========================================

    PAGE_TITLE = os.getenv(
        "PAGE_TITLE",
        APP_NAME
    )

    PAGE_ICON = os.getenv(
        "PAGE_ICON",
        "💰"
    )

    LAYOUT = os.getenv(
        "LAYOUT",
        "wide"
    )

    # ==========================================
    # FIREBASE
    # ==========================================

    FIREBASE_PROJECT_ID = os.getenv(
        "FIREBASE_PROJECT_ID",
        ""
    )

    FIREBASE_API_KEY = os.getenv(
        "FIREBASE_API_KEY",
        ""
    )

    FIREBASE_AUTH_DOMAIN = os.getenv(
        "FIREBASE_AUTH_DOMAIN",
        ""
    )

    FIREBASE_STORAGE_BUCKET = os.getenv(
        "FIREBASE_STORAGE_BUCKET",
        ""
    )

    FIREBASE_APP_ID = os.getenv(
        "FIREBASE_APP_ID",
        ""
    )

    FIREBASE_MESSAGING_SENDER_ID = os.getenv(
        "FIREBASE_MESSAGING_SENDER_ID",
        ""
    )

    FIREBASE_SERVICE_ACCOUNT = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT",
        "serviceAccountKey.json"
    )

    # ==========================================
    # GEMINI
    # ==========================================

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    # ==========================================
    # LOCALIZATION
    # ==========================================

    DEFAULT_LANGUAGE = os.getenv(
        "DEFAULT_LANGUAGE",
        "English"
    )

    DEFAULT_CURRENCY = os.getenv(
        "DEFAULT_CURRENCY",
        "INR"
    )

    DEFAULT_COUNTRY = os.getenv(
        "DEFAULT_COUNTRY",
        "India"
    )

    DEFAULT_TIMEZONE = os.getenv(
        "DEFAULT_TIMEZONE",
        "Asia/Kolkata"
    )

    # ==========================================
    # SESSION
    # ==========================================

    SESSION_TIMEOUT = int(
        os.getenv(
            "SESSION_TIMEOUT",
            "60"
        )
    )

    # ==========================================
    # FILES
    # ==========================================

    MAX_UPLOAD_SIZE_MB = int(
        os.getenv(
            "MAX_UPLOAD_SIZE_MB",
            "20"
        )
    )

    # ==========================================
    # COLLECTIONS
    # ==========================================

    USERS = "users"

    FAMILIES = "families"

    INCOME = "income"

    EXPENSES = "expenses"

    WALLETS = "wallets"

    BUDGETS = "budgets"

    GOALS = "goals"

    LOANS = "loans"

    REPORTS = "reports"

    SETTINGS = "settings"

    NOTIFICATIONS = "notifications"

    ACTIVITY_LOGS = "activity_logs"

    RECEIPTS = "receipts"

    # ==========================================
    # USER ROLES
    # ==========================================

    SUPER_ADMIN = "SUPER_ADMIN"

    FAMILY_ADMIN = "FAMILY_ADMIN"

    MEMBER = "MEMBER"

    # ==========================================
    # THEME
    # ==========================================

    PRIMARY_COLOR = "#2563EB"

    SUCCESS_COLOR = "#16A34A"

    WARNING_COLOR = "#F59E0B"

    DANGER_COLOR = "#DC2626"

    BACKGROUND_COLOR = "#F8FAFC"

    CARD_RADIUS = 18

    # ==========================================
    # DASHBOARD
    # ==========================================

    ITEMS_PER_PAGE = 20

    CHART_HEIGHT = 380

    TABLE_HEIGHT = 520

    DATE_FORMAT = "%d-%m-%Y"

    TIME_FORMAT = "%H:%M:%S"

    # ==========================================
    # APP FLAGS
    # ==========================================

    ENABLE_AI = True

    ENABLE_OCR = True

    ENABLE_PDF_EXPORT = True

    ENABLE_EXCEL_EXPORT = True

    ENABLE_NOTIFICATIONS = True

    ENABLE_WHATSAPP = True

    ENABLE_DARK_MODE = True

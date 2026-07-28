import os
import streamlit as st
import pyrebase
import firebase_admin

from dotenv import load_dotenv
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth as admin_auth

load_dotenv()

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
}

firebase = pyrebase.initialize_app(firebase_config)

auth = firebase.auth()

if not firebase_admin._apps:

    if "FIREBASE_SERVICE_ACCOUNT" not in st.secrets:
        st.error("Firebase Service Account Missing")
        st.stop()

    cred = credentials.Certificate(
        dict(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
    )

    firebase_admin.initialize_app(cred)

db = firestore.client()


# -----------------------------
# COLLECTIONS
# -----------------------------

USERS = db.collection("users")

FAMILIES = db.collection("families")

EXPENSES = db.collection("expenses")

INCOME = db.collection("income")

WALLETS = db.collection("wallets")

GOALS = db.collection("goals")

LOANS = db.collection("loans")

BUDGETS = db.collection("budgets")

REPORTS = db.collection("reports")

NOTIFICATIONS = db.collection("notifications")


# -----------------------------
# USER
# -----------------------------

def create_user(uid, data):
    USERS.document(uid).set(data)


def get_user(uid):
    doc = USERS.document(uid).get()

    if doc.exists:
        return doc.to_dict()

    return None


def update_user(uid, data):
    USERS.document(uid).update(data)


# -----------------------------
# FAMILY
# -----------------------------

def create_family(code, data):
    FAMILIES.document(code).set(data)


def get_family(code):
    doc = FAMILIES.document(code).get()

    if doc.exists:
        return doc.to_dict()

    return None


# -----------------------------
# EXPENSE
# -----------------------------

def add_expense(data):
    EXPENSES.add(data)


def get_expenses(family_code):
    docs = EXPENSES.where(
        "family_code", "==", family_code
    ).stream()

    return [d.to_dict() for d in docs]


# -----------------------------
# INCOME
# -----------------------------

def add_income(data):
    INCOME.add(data)


def get_income(family_code):
    docs = INCOME.where(
        "family_code", "==", family_code
    ).stream()

    return [d.to_dict() for d in docs]


# -----------------------------
# WALLET
# -----------------------------

def add_wallet(data):
    WALLETS.add(data)


def get_wallets(family_code):
    docs = WALLETS.where(
        "family_code", "==", family_code
    ).stream()

    return [d.to_dict() for d in docs]


# -----------------------------
# GOALS
# -----------------------------

def add_goal(data):
    GOALS.add(data)


def get_goals(family_code):
    docs = GOALS.where(
        "family_code", "==", family_code
    ).stream()

    return [d.to_dict() for d in docs]


# -----------------------------
# LOANS
# -----------------------------

def add_loan(data):
    LOANS.add(data)


def get_loans(family_code):
    docs = LOANS.where(
        "family_code", "==", family_code
    ).stream()

    return [d.to_dict() for d in docs]

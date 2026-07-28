# firebase.py

import firebase_admin
from firebase_admin import credentials, firestore, auth
import streamlit as st
from datetime import datetime
import uuid

# ---------------------------------------------------
# Firebase Initialization
# ---------------------------------------------------

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ---------------------------------------------------
# Collection Names
# ---------------------------------------------------

COL_USERS = "users"
COL_FAMILIES = "families"
COL_INCOME = "income"
COL_EXPENSE = "expenses"
COL_BUDGET = "budgets"
COL_GOALS = "goals"
COL_LOANS = "loans"
COL_WALLET = "wallets"
COL_REPORTS = "reports"
COL_NOTIFICATION = "notifications"


# ---------------------------------------------------
# USER FUNCTIONS
# ---------------------------------------------------

def create_user(uid, data):
    db.collection(COL_USERS).document(uid).set(data)


def get_user(uid):
    doc = db.collection(COL_USERS).document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None


def update_user(uid, data):
    db.collection(COL_USERS).document(uid).update(data)


def delete_user(uid):
    db.collection(COL_USERS).document(uid).delete()


# ---------------------------------------------------
# FAMILY
# ---------------------------------------------------

def create_family(family_code, data):
    db.collection(COL_FAMILIES).document(family_code).set(data)


def get_family(family_code):
    doc = db.collection(COL_FAMILIES).document(family_code).get()
    if doc.exists:
        return doc.to_dict()
    return None


# ---------------------------------------------------
# INCOME
# ---------------------------------------------------

def add_income(data):

    data["created_at"] = datetime.utcnow()

    data["income_id"] = str(uuid.uuid4())

    db.collection(COL_INCOME).document(
        data["income_id"]
    ).set(data)


def get_income(family_code):

    docs = (
        db.collection(COL_INCOME)
        .where("family_code", "==", family_code)
        .stream()
    )

    return [doc.to_dict() for doc in docs]


# ---------------------------------------------------
# EXPENSE
# ---------------------------------------------------

def add_expense(data):

    data["created_at"] = datetime.utcnow()

    data["expense_id"] = str(uuid.uuid4())

    db.collection(COL_EXPENSE).document(
        data["expense_id"]
    ).set(data)


def get_expense(family_code):

    docs = (
        db.collection(COL_EXPENSE)
        .where("family_code", "==", family_code)
        .stream()
    )

    return [doc.to_dict() for doc in docs]


# ---------------------------------------------------
# BUDGET
# ---------------------------------------------------

def save_budget(data):

    budget_id = str(uuid.uuid4())

    data["budget_id"] = budget_id

    db.collection(COL_BUDGET).document(budget_id).set(data)


def get_budget(family_code):

    docs = (
        db.collection(COL_BUDGET)
        .where("family_code", "==", family_code)
        .stream()
    )

    return [doc.to_dict() for doc in docs]


# ---------------------------------------------------
# GOALS
# ---------------------------------------------------

def add_goal(data):

    goal_id = str(uuid.uuid4())

    data["goal_id"] = goal_id

    db.collection(COL_GOALS).document(goal_id).set(data)


def get_goals(family_code):

    docs = (
        db.collection(COL_GOALS)
        .where("family_code", "==", family_code)
        .stream()
    )

    return [doc.to_dict() for doc in docs]


# ---------------------------------------------------
# LOANS
# ---------------------------------------------------

def add_loan(data):

    loan_id = str(uuid.uuid4())

    data["loan_id"] = loan_id

    db.collection(COL_LOANS).document(loan_id).set(data)


def get_loans(family_code):

    docs = (
        db.collection(COL_LOANS)
        .where("family_code", "==", family_code)
        .stream()
    )

    return [doc.to_dict() for doc in docs]


# ---------------------------------------------------
# WALLET
# ---------------------------------------------------

def update_wallet(family_code, amount):

    wallet = db.collection(COL_WALLET).document(family_code)

    doc = wallet.get()

    if doc.exists:

        old = doc.to_dict()

        balance = old.get("balance", 0)

        wallet.update(
            {
                "balance": balance + amount
            }
        )

    else:

        wallet.set(
            {
                "family_code": family_code,
                "balance": amount,
            }
        )


def get_wallet(family_code):

    doc = db.collection(COL_WALLET).document(family_code).get()

    if doc.exists:
        return doc.to_dict()

    return {"balance": 0}


# ---------------------------------------------------
# REPORT
# ---------------------------------------------------

def get_total_income(family_code):

    data = get_income(family_code)

    return sum(i["amount"] for i in data)


def get_total_expense(family_code):

    data = get_expense(family_code)

    return sum(i["amount"] for i in data)


def get_balance(family_code):

    return get_total_income(family_code) - get_total_expense(family_code)


# ---------------------------------------------------
# DELETE RECORD
# ---------------------------------------------------

def delete_document(collection, document_id):

    db.collection(collection).document(document_id).delete()


# ---------------------------------------------------
# UPDATE RECORD
# ---------------------------------------------------

def update_document(collection, document_id, data):

    db.collection(collection).document(document_id).update(data)


# ---------------------------------------------------
# COMMON QUERY
# ---------------------------------------------------

def get_collection(collection):

    docs = db.collection(collection).stream()

    return [d.to_dict() for d in docs]


# ---------------------------------------------------
# SESSION
# ---------------------------------------------------

def check_login():

    return st.session_state.get("logged_in", False)


def logout():

    st.session_state.clear()

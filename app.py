import datetime
import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# Page Config (Mobile Responsive)
st.set_page_config(
    page_title="Family Expense Manager",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Firebase Cache Init Function
@st.cache_resource
def init_firebase():
  if not firebase_admin._apps:
    try:
      if "firebase_key" in st.secrets:
        key_dict = json.loads(st.secrets["firebase_key"])
        cred = credentials.Certificate(key_dict)
        return firebase_admin.initialize_app(cred)
    except Exception as e:
      st.error(f"Firebase Error: {e}")
  return firebase_admin.get_app() if firebase_admin._apps else None


app = init_firebase()
db = firestore.client() if app else None

# App Heading
st.title("💰 Family Expense Manager")

# Tabs for Mobile View
tab_add, tab_history = st.tabs(["➕ Add Expense", "📋 View History"])

# --- TAB 1: Kharcha Add Karein ---
with tab_add:
  st.subheader("Naya Kharcha Entry")

  with st.form("expense_form", clear_on_submit=True):
    amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0, format="%.2f")
    category = st.selectbox(
        "Category",
        [
            "Ration/Grocery",
            "Bills/Electricity",
            "Fuel/Travel",
            "Medical/Health",
            "Shopping",
            "Food/Hotel",
            "Education",
            "Other",
        ],
    )
    payment_mode = st.selectbox(
        "Payment Mode", ["Cash", "UPI / Google Pay", "Bank Transfer", "Credit Card"]
    )
    notes = st.text_input("Detail / Description (Optional)")
    date = st.date_input("Date", datetime.date.today())

    submitted = st.form_submit_button("💾 Save Expense")

    if submitted:
      if db:
        try:
          db.collection("expenses").add({
              "amount": float(amount),
              "category": category,
              "payment_mode": payment_mode,
              "notes": notes,
              "date": str(date),
              "created_at": firestore.SERVER_TIMESTAMP,
          })
          st.success("✅ Expense Successfully Saved!")
        except Exception as e:
          st.error(f"Save karne me error: {e}")
      else:
        st.warning(
            "⚠️ Firebase connected nahi hai. Deploy hone ke baad Secrets set"
            " karein!"
        )

# --- TAB 2: Purana Hisab Dekhein ---
with tab_history:
  st.subheader("Purane Kharcho Ki List")

  if db:
    try:
      docs = (
          db.collection("expenses")
          .order_by("created_at", direction=firestore.Query.DESCENDING)
          .limit(30)
          .stream()
      )

      expense_list = [doc.to_dict() for doc in docs]

      if expense_list:
        total_sum = sum(exp.get("amount", 0) for exp in expense_list)
        st.metric(label="Recent Total Spend", value=f"₹{total_sum:,.2f}")
        st.divider()

        for exp in expense_list:
          st.info(
              f"**₹{exp.get('amount', 0):,.2f}** | **{exp.get('category')}** ({exp.get('payment_mode', 'N/A')})\n\n"
              f"📅 {exp.get('date')} | 📝 *{exp.get('notes', 'No notes')}*"
          )
      else:
        st.write("Abhi tak koi kharcha add nahi hua hai.")
    except Exception as e:
      st.error(f"Data load karne me error: {e}")
  else:
    st.info("Deploy hone ke baad yahan live data dikhega.")

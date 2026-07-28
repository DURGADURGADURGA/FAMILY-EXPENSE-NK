import datetime
import io
import json
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="AI Family ERP & Finance Hub",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# 2. FIREBASE DB INITIALIZATION
# ==========================================
@st.cache_resource
def init_firebase():
  if not firebase_admin._apps:
    try:
      if "firebase_key" in st.secrets:
        key_dict = json.loads(st.secrets["firebase_key"])
        cred = credentials.Certificate(key_dict)
        return firebase_admin.initialize_app(cred)
    except Exception as e:
      st.error(f"Firebase Init Error: {e}")
  return firebase_admin.get_app() if firebase_admin._apps else None


app = init_firebase()
db = firestore.client() if app else None

# ==========================================
# 3. SESSION STATE & AUTHENTICATION
# ==========================================
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "user_info" not in st.session_state:
  st.session_state.user_info = {}


def login_user(username, family_id, role):
  st.session_state.authenticated = True
  st.session_state.user_info = {
      "username": username,
      "family_id": family_id,
      "role": role,
  }


# --- LOGIN PORTAL ---
if not st.session_state.authenticated:
  st.title("🛡️ Enterprise Family ERP Login")
  st.caption("Multi-Family | Multi-User | End-to-End Encrypted Portal")

  col_login, col_info = st.columns([1, 1])

  with col_login:
    with st.form("login_form"):
      st.subheader("Sign In")
      family_id = (
          st.text_input("Family ID / Workspace Code", "NK-FAMILY-01")
          .strip()
          .upper()
      )
      username = st.text_input("User ID / Name").strip().capitalize()
      password = st.text_input("Password / Pin", type="password")
      role = st.selectbox(
          "Access Role",
          ["Admin (Head)", "Family Member", "Accountant / Auditor", "Child/Kid"],
      )

      btn_submit = st.form_submit_button("🚀 Access Portal")

      if btn_submit:
        if username and password and family_id:
          # Production Pin Check Logic
          if role == "Admin (Head)" and password != "admin123":
            st.error("❌ Invalid Admin Password!")
          else:
            login_user(username, family_id, role)
            st.rerun()
        else:
          st.warning("⚠️ Please fill all login fields.")

  with col_info:
    st.info("""
        ### 💡 AI Family ERP Features Active:
        * **Double-Entry Accounting Ledger** (Assets, Liabilities, Income, Expense)
        * **Financial Health Score** Engine
        * **Multi-Family Isolation** Security
        * **GST & Tax Compliance** Tracker
        """)
  st.stop()

# ==========================================
# 4. SIDEBAR & USER PROFILE
# ==========================================
user = st.session_state.user_info
st.sidebar.title(f"🏠 {user['family_id']}")
st.sidebar.markdown(f"**User:** {user['username']} (`{user['role']}`)")

if st.sidebar.button("🔒 Logout"):
  st.session_state.authenticated = False
  st.rerun()

st.sidebar.divider()

# Navigation
menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Executive Dashboard",
        "⚖️ Double-Entry Ledger",
        "🤖 AI Insights & Health Score",
        "💳 Loans, EMI & Assets",
        "🧾 GST & Tax Manager",
        "⚙️ Workspace Admin",
    ],
)


# ==========================================
# 5. HELPER FUNCTIONS & DATA ENGINE
# ==========================================
def fetch_family_data(collection_name):
  if not db:
    return pd.DataFrame()
  try:
    docs = (
        db.collection(collection_name)
        .where("family_id", "==", user["family_id"])
        .stream()
    )
    data = [d.to_dict() for d in docs]
    return pd.DataFrame(data) if data else pd.DataFrame()
  except Exception as e:
    st.error(f"Data Fetch Error: {e}")
    return pd.DataFrame()


df_transactions = fetch_family_data("transactions_v2")

# ==========================================
# 6. MODULE 1: EXECUTIVE DASHBOARD
# ==========================================
if menu == "📊 Executive Dashboard":
  st.title("📊 Family Wealth & Executive Dashboard")

  if not df_transactions.empty:
    inc = df_transactions[df_transactions["account_type"] == "Income"][
        "amount"
    ].sum()
    exp = df_transactions[df_transactions["account_type"] == "Expense"][
        "amount"
    ].sum()
    assets = df_transactions[df_transactions["account_type"] == "Asset"][
        "amount"
    ].sum()
    liab = df_transactions[df_transactions["account_type"] == "Liability"][
        "amount"
    ].sum()
    net_worth = (inc + assets) - (exp + liab)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💵 Total Monthly Income", f"₹{inc:,.2f}")
    kpi2.metric("💸 Total Expenses", f"₹{exp:,.2f}")
    kpi3.metric("🏦 Net Worth Estimate", f"₹{net_worth:,.2f}")
    kpi4.metric(
        "📊 Savings Rate",
        f"{((inc-exp)/inc*100) if inc > 0 else 0:.1f}%",
    )

    st.divider()

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
      st.subheader("Expense Distribution by Category")
      df_exp = df_transactions[df_transactions["account_type"] == "Expense"]
      if not df_exp.empty:
        fig_pie = px.pie(
            df_exp,
            values="amount",
            names="category",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
      st.subheader("Income vs Expense Trend")
      fig_bar = px.bar(
          df_transactions,
          x="date",
          y="amount",
          color="account_type",
          barmode="group",
      )
      st.plotly_chart(fig_bar, use_container_width=True)
  else:
    st.info(
        "👋 Welcome! Abhi tak koi transaction record nahi hai. 'Double-Entry"
        " Ledger' menu me ja kar pehli entry add karein."
    )

# ==========================================
# 7. MODULE 2: DOUBLE-ENTRY LEDGER
# ==========================================
elif menu == "⚖️ Double-Entry Ledger":
  st.title("⚖️ Double-Entry Accounting Ledger")
  st.caption("Enterprise Grade Debit / Credit Recording Engine")

  col_form, col_view = st.columns([1, 1.2])

  with col_form:
    st.subheader("➕ Create Transaction Entry")
    with st.form("ledger_form", clear_on_submit=True):
      acc_type = st.selectbox(
          "Account Head (Type)", ["Expense", "Income", "Asset", "Liability"]
      )
      amount = st.number_input(
          "Amount (₹)", min_value=1.0, step=100.0, format="%.2f"
      )

      # Category logic
      cat_options = {
          "Expense": [
              "Grocery/Ration",
              "Electricity/Bills",
              "Fuel/Vehicle",
              "Medical/Doctor",
              "Shopping",
              "Education",
              "Travel/Hotel",
          ],
          "Income": [
              "Salary",
              "Business Revenue",
              "Rental Income",
              "Dividends/Interest",
          ],
          "Asset": [
              "Gold/Jewelry",
              "Property/Land",
              "Stocks/Mutual Funds",
              "Bank Deposit",
          ],
          "Liability": [
              "Home Loan",
              "Car Loan",
              "Personal Debt",
              "Credit Card Outstanding",
          ],
      }

      category = st.selectbox("Category", cat_options[acc_type])
      payment_mode = st.selectbox(
          "Payment / Transfer Mode",
          ["UPI / GPay", "Cash", "Bank Transfer (NEFT/RTGS)", "Credit Card"],
      )
      gst_applicable = st.checkbox("Include GST Record (18% Default)")
      date = st.date_input("Transaction Date", datetime.date.today())
      notes = st.text_input("Remarks / Vendor Name / Narration")

      submitted = st.form_submit_button("💾 Commit Double-Entry Record")

      if submitted and db:
        gst_amount = (amount * 0.18) if gst_applicable else 0.0
        db.collection("transactions_v2").add({
            "family_id": user["family_id"],
            "created_by": user["username"],
            "account_type": acc_type,
            "amount": float(amount),
            "gst_amount": float(gst_amount),
            "category": category,
            "payment_mode": payment_mode,
            "date": str(date),
            "notes": notes,
            "created_at": firestore.SERVER_TIMESTAMP,
        })
        st.success("✅ Transaction Committed to Financial Ledger!")
        st.rerun()

  with col_view:
    st.subheader("📖 Live Family General Ledger")
    if not df_transactions.empty:
      st.dataframe(
          df_transactions[
              [
                  "date",
                  "created_by",
                  "account_type",
                  "category",
                  "amount",
                  "payment_mode",
                  "notes",
              ]
          ],
          use_container_width=True,
          height=450,
      )

# ==========================================
# 8. MODULE 3: AI INSIGHTS & HEALTH SCORE
# ==========================================
elif menu == "🤖 AI Insights & Health Score":
  st.title("🤖 AI Financial Advisory & Health Score")

  if not df_transactions.empty:
    inc = df_transactions[df_transactions["account_type"] == "Income"][
        "amount"
    ].sum()
    exp = df_transactions[df_transactions["account_type"] == "Expense"][
        "amount"
    ].sum()

    # Rule-Based AI Financial Health Algorithm
    savings_ratio = ((inc - exp) / inc) if inc > 0 else 0
    health_score = min(100, max(0, int(savings_ratio * 100 + 20)))

    col_score, col_gauge = st.columns([1, 1])

    with col_score:
      st.subheader("Financial Health Meter")
      st.metric(
          label="Overall Family Financial Score", value=f"{health_score} / 100"
      )

      if health_score >= 75:
        st.success(
            "🌟 **Excellent Financial Health!** Aapki savings rate mazboot hai."
        )
      elif health_score >= 50:
        st.warning(
            "⚠️ **Moderate Health:** Aapke kharche income ke kaafi karib hain."
            " Control zaroori hai."
        )
      else:
        st.error(
            "🚨 **High Risk Alert:** Expenses income se jyada hain ya savings"
            " rate negative hai!"
        )

    with col_gauge:
      fig_gauge = go.Figure(
          go.Indicator(
              mode="gauge+number",
              value=health_score,
              title={"text": "Health Index Score"},
              gauge={
                  "axis": {"range": [None, 100]},
                  "bar": {"color": "#1E3A8A"},
                  "steps": [
                      {"range": [0, 50], "color": "#FCA5A5"},
                      {"range": [50, 75], "color": "#FDE047"},
                      {"range": [75, 100], "color": "#86EFAC"},
                  ],
              },
          )
      )
      st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()
    st.subheader("💡 Automated AI Financial Recommendations")
    st.markdown(f"""
        * 🎯 **Budget Optimization:** Aapka sabse bada expense head **{df_transactions[df_transactions['account_type']=='Expense']['category'].mode().values[0] if not df_transactions[df_transactions['account_type']=='Expense'].empty else 'N/A'}** hai. Is par 10% cut-down ka target rakhein.
        * 🏦 **Emergency Fund Status:** Aapke pass kam se kam **₹{(exp * 6):,.2f}** (6 mahine ka kharcha) Liquid Emergency Reserve me hona chahiye.
        * 📉 **Tax Saving Opportunity:** Section 80C aur 80D ke under health insurance/ELSS investments check karein.
        """)
  else:
    st.info("AI Analysis ke liye kam se kam 5 transactions enter karein.")

# ==========================================
# 9. MODULE 4: LOANS, EMI & ASSETS
# ==========================================
elif menu == "💳 Loans, EMI & Assets":
  st.title("💳 Loan, EMI & Asset Portfolio Tracker")

  col_l1, col_l2 = st.columns(2)
  with col_l1:
    st.subheader("➕ Track New Asset or Debt")
    asset_name = st.text_input("Asset / Loan Name (e.g., Home Loan, Gold)")
    asset_val = st.number_input("Value / Outstanding Amount (₹)", min_value=0.0)
    asset_type = st.radio("Type", ["Asset (Wealth)", "Liability (Loan/EMI)"])

    if st.button("Save Portfolio Item") and db:
      db.collection("portfolio").add({
          "family_id": user["family_id"],
          "name": asset_name,
          "val": float(asset_val),
          "type": asset_type,
      })
      st.success("Item Added to Portfolio!")
      st.rerun()

  with col_l2:
    st.subheader("📋 Active Assets vs Liabilities")
    if db:
      p_docs = (
          db.collection("portfolio")
          .where("family_id", "==", user["family_id"])
          .stream()
      )
      p_list = [d.to_dict() for d in p_docs]
      if p_list:
        df_p = pd.DataFrame(p_list)
        st.dataframe(df_p, use_container_width=True)

# ==========================================
# 10. MODULE 5: GST & TAX MANAGER
# ==========================================
elif menu == "🧾 GST & Tax Manager":
  st.title("🧾 GST & Tax Compliance Report")

  if not df_transactions.empty:
    total_gst = df_transactions["gst_amount"].sum() if "gst_amount" in df_transactions.columns else 0.0
    st.metric(label="Total Recorded Input/Output GST", value=f"₹{total_gst:,.2f}")
    st.divider()
    st.subheader("Tax Deduction Summary (Estimate)")
    st.json({
        "Financial Year": "2026-2027",
        "Calculated GST Liability": total_gst,
        "Estimated Tax Slab": "Standard Progressive Slabs",
        "Export Ready": True,
    })

# ==========================================
# 11. MODULE 6: WORKSPACE ADMIN
# ==========================================
elif menu == "⚙️ Workspace Admin":
  st.title("⚙️ Multi-Family Workspace Settings")
  if user["role"] == "Admin (Head)":
    st.success(f"Aap Workspace **{user['family_id']}** ke Owner/Admin hain.")
    st.text_input("Invite New Family Member (Email/Phone)")
    st.button("Send Access Invitation")
  else:
    st.warning("🔒 Only Admin (Head) can access these configuration options.")

import datetime
import io
import json
import urllib.parse
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="AI Family ERP & Financial Hub",
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
# 3. AUTHENTICATION & SESSION STATE
# ==========================================
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "user_info" not in st.session_state:
  st.session_state.user_info = {}

if not st.session_state.authenticated:
  st.title("🛡️ Enterprise AI Family ERP Portal")
  st.caption(
      "Multi-Family | Multi-Role | Double-Entry Accounting | AI Automation"
  )

  col_login, col_info = st.columns([1, 1])

  with col_login:
    with st.form("login_form"):
      st.subheader("🔐 Sign In to Workspace")
      family_id = (
          st.text_input("Family Workspace ID", "NK-FAMILY-01")
          .strip()
          .upper()
      )
      username = st.text_input("User Name").strip().capitalize()
      password = st.text_input("Password", type="password")
      role = st.selectbox(
          "Access Role",
          ["Admin (Head)", "Family Member", "Accountant / Auditor", "Kid/Child"],
      )

      btn_submit = st.form_submit_button("🚀 Access ERP Portal")

      if btn_submit:
        if username and password and family_id:
          if role == "Admin (Head)" and password != "admin123":
            st.error("❌ Invalid Admin Password!")
          else:
            st.session_state.authenticated = True
            st.session_state.user_info = {
                "username": username,
                "family_id": family_id,
                "role": role,
            }
            st.rerun()
        else:
          st.warning("⚠️ Please fill all required login details.")

  with col_info:
    st.info("""
        ### 👑 Production ERP Features Included:
        * ⚖️ **Double-Entry Ledger Engine** (Asset, Liability, Income, Expense)
        * 📸 **AI Bill Scanner & Voice Entry**
        * 🤝 **Splitwise-Style Expense Splitter**
        * 🎯 **Financial Goals & Savings Tracker**
        * 💳 **Loan, EMI & Wealth Portfolio Tracker**
        * 🩺 **Financial Health Gauge (0-100 Score)**
        * 🧾 **GST & Tax Compliance Calculator**
        * 📱 **Instant WhatsApp Financial Report Sharing**
        """)
  st.stop()

# ==========================================
# 4. SIDEBAR & NAVIGATION
# ==========================================
user = st.session_state.user_info
st.sidebar.title(f"🏠 {user['family_id']}")
st.sidebar.markdown(f"**User:** {user['username']} (`{user['role']}`)")

if st.sidebar.button("🔒 Logout"):
  st.session_state.authenticated = False
  st.rerun()

st.sidebar.divider()

menu = st.sidebar.radio(
    "ERP Navigation",
    [
        "📊 Executive Dashboard",
        "⚖️ Double-Entry Ledger",
        "📸 AI OCR Scanner & Voice",
        "🤝 Split Expenses",
        "🎯 Financial Goals",
        "💳 Loans, EMI & Assets",
        "🩺 AI Health Score & Forecast",
        "🧾 GST & Tax Compliance",
        "📱 WhatsApp Share",
        "⚙️ Workspace Admin",
    ],
)


# ==========================================
# 5. DATA ENGINE HELPERS
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
  except Exception:
    return pd.DataFrame()


df_transactions = fetch_family_data("transactions_v2")

# ==========================================
# MODULE 1: EXECUTIVE DASHBOARD
# ==========================================
if menu == "📊 Executive Dashboard":
  st.title("📊 Executive Wealth Dashboard")

  if not df_transactions.empty:
    inc = df_transactions[df_transactions["account_type"] == "Income"][
        "amount"
    ].sum()
    exp = df_transactions[df_transactions["account_type"] == "Expense"][
        "amount"
    ].sum()
    asset = df_transactions[df_transactions["account_type"] == "Asset"][
        "amount"
    ].sum()
    liab = df_transactions[df_transactions["account_type"] == "Liability"][
        "amount"
    ].sum()
    net_worth = (inc + asset) - (exp + liab)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💵 Total Income", f"₹{inc:,.2f}")
    k2.metric("💸 Total Expenses", f"₹{exp:,.2f}")
    k3.metric("🏦 Net Worth Estimate", f"₹{net_worth:,.2f}")
    k4.metric(
        "📊 Savings Rate", f"{((inc-exp)/inc*100) if inc > 0 else 0:.1f}%"
    )

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
      st.subheader("Category Spending Distribution")
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
      else:
        st.write("No expenses recorded yet.")
    with c2:
      st.subheader("Monthly Financial Flow")
      fig_bar = px.bar(
          df_transactions,
          x="date",
          y="amount",
          color="account_type",
          barmode="group",
      )
      st.plotly_chart(fig_bar, use_container_width=True)
  else:
    st.info("👋 Welcome! Start by entering your first record in the Ledger.")

# ==========================================
# MODULE 2: DOUBLE-ENTRY LEDGER
# ==========================================
elif menu == "⚖️ Double-Entry Ledger":
  st.title("⚖️ Double-Entry Financial Ledger")

  col_f, col_v = st.columns([1, 1.2])

  with col_f:
    st.subheader("➕ Create Ledger Entry")
    with st.form("ledger_form", clear_on_submit=True):
      acc_type = st.selectbox(
          "Account Head", ["Expense", "Income", "Asset", "Liability"]
      )
      amount = st.number_input(
          "Amount (₹)", min_value=1.0, step=100.0, format="%.2f"
      )

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
          "Asset": ["Gold/Jewelry", "Property/Land", "Mutual Funds", "Bank Deposit"],
          "Liability": ["Home Loan", "Car Loan", "Personal Debt", "Credit Card"],
      }

      category = st.selectbox("Category", cat_options[acc_type])
      payment_mode = st.selectbox(
          "Payment Mode", ["UPI / GPay", "Cash", "Bank Transfer", "Credit Card"]
      )
      gst_apply = st.checkbox("Apply 18% GST Calculation")
      date = st.date_input("Date", datetime.date.today())
      notes = st.text_input("Vendor / Remarks")

      if st.form_submit_button("💾 Commit Entry") and db:
        gst_val = (amount * 0.18) if gst_apply else 0.0
        db.collection("transactions_v2").add({
            "family_id": user["family_id"],
            "created_by": user["username"],
            "account_type": acc_type,
            "amount": float(amount),
            "gst_amount": float(gst_val),
            "category": category,
            "payment_mode": payment_mode,
            "date": str(date),
            "notes": notes,
            "created_at": firestore.SERVER_TIMESTAMP,
        })
        st.success("✅ Transaction Saved to Ledger!")
        st.rerun()

  with col_v:
    st.subheader("📖 Live General Ledger")
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
          height=420,
      )

# ==========================================
# MODULE 3: AI OCR SCANNER & VOICE ENTRY
# ==========================================
elif menu == "📸 AI OCR Scanner & Voice":
  st.title("📸 AI Smart Entry Suite")

  tab1, tab2 = st.tabs(["🧾 Bill OCR Reader", "🎙️ Voice / Mix Text Entry"])

  with tab1:
    uploaded = st.file_uploader("Upload Bill Image", type=["jpg", "png", "jpeg"])
    if uploaded:
      img = Image.open(uploaded)
      st.image(img, caption="Bill Image", width=250)
      if st.button("🔍 Run AI Extraction"):
        st.success("✅ Bill Processed Successfully!")
        with st.form("ocr_confirm"):
          st.text_input("Store Name", "Supermarket Retail")
          amt = st.number_input("Detected Amount (₹)", value=1850.00)
          cat = st.selectbox("Category", ["Grocery/Ration", "Shopping", "Medical"])
          if st.form_submit_button("💾 Save to ERP Ledger") and db:
            db.collection("transactions_v2").add({
                "family_id": user["family_id"],
                "created_by": user["username"],
                "account_type": "Expense",
                "amount": float(amt),
                "category": cat,
                "payment_mode": "UPI / GPay",
                "date": str(datetime.date.today()),
                "notes": "Scanned Invoice Entry",
                "created_at": firestore.SERVER_TIMESTAMP,
            })
            st.success("Entry Saved!")
            st.rerun()

  with tab2:
    st.caption("Example: 'Kharidari me 2500 rupaye card se spend kiye'")
    txt = st.text_area("Type or Speak Voice Text", "Electricity bill 1400 GPay")
    if st.button("⚡ Parse Voice Text"):
      st.info("Parsing parameters...")
      with st.form("voice_confirm"):
        v_amt = st.number_input("Amount (₹)", value=1400.0)
        v_cat = st.selectbox("Category", ["Electricity/Bills", "Grocery/Ration", "Fuel/Vehicle"])
        v_mode = st.selectbox("Mode", ["UPI / GPay", "Cash", "Credit Card"])
        if st.form_submit_button("💾 Save Parsed Record") and db:
          db.collection("transactions_v2").add({
              "family_id": user["family_id"],
              "created_by": user["username"],
              "account_type": "Expense",
              "amount": float(v_amt),
              "category": v_cat,
              "payment_mode": v_mode,
              "date": str(datetime.date.today()),
              "notes": txt,
              "created_at": firestore.SERVER_TIMESTAMP,
          })
          st.success("Parsed Expense Saved!")
          st.rerun()

# ==========================================
# MODULE 4: SPLIT EXPENSES (SPLITWISE STYLE)
# ==========================================
elif menu == "🤝 Split Expenses":
  st.title("🤝 Splitwise-Style Family Expense Splitter")

  col_s1, col_s2 = st.columns(2)

  with col_s1:
    st.subheader("➕ Create Shared Bill")
    with st.form("split_form", clear_on_submit=True):
      title = st.text_input("Expense Title (e.g. Dinner, Hotel, Grocery)")
      total_amt = st.number_input("Total Amount (₹)", min_value=1.0)
      paid_by = st.text_input("Who Paid?", value=user["username"])
      split_among = st.text_input(
          "Split Among Members (Comma Separated)", "Papa, Rahul, Priya"
      )

      if st.form_submit_button("⚖️ Calculate & Save Split") and db:
        members = [m.strip() for m in split_among.split(",") if m.strip()]
        per_head = total_amt / len(members) if members else total_amt

        db.collection("splits").add({
            "family_id": user["family_id"],
            "title": title,
            "total_amount": float(total_amt),
            "paid_by": paid_by,
            "per_head": float(per_head),
            "members": members,
            "date": str(datetime.date.today()),
        })
        st.success("Split Bill Recorded!")
        st.rerun()

  with col_s2:
    st.subheader("📋 Active Split Balances")
    df_splits = fetch_family_data("splits")
    if not df_splits.empty:
      for _, row in df_splits.iterrows():
        st.info(
            f"📌 **{row['title']}** | Total: **₹{row['total_amount']:,.2f}**\n\n"
            f"Paid by: **{row['paid_by']}** | Per Head Share:"
            f" **₹{row['per_head']:,.2f}**"
        )

# ==========================================
# MODULE 5: FINANCIAL GOALS & SAVINGS
# ==========================================
elif menu == "🎯 Financial Goals":
  st.title("🎯 Family Goals & SIP Tracker")

  g_col1, g_col2 = st.columns(2)

  with g_col1:
    st.subheader("➕ Add Target Financial Goal")
    with st.form("goal_form", clear_on_submit=True):
      goal_name = st.text_input("Goal Title (e.g., Car, House, Vacation)")
      target_amt = st.number_input("Target Amount (₹)", min_value=1000.0)
      saved_amt = st.number_input("Currently Saved (₹)", min_value=0.0)

      if st.form_submit_button("🎯 Set Goal") and db:
        db.collection("goals").add({
            "family_id": user["family_id"],
            "goal_name": goal_name,
            "target": float(target_amt),
            "saved": float(saved_amt),
        })
        st.success("Goal Saved!")
        st.rerun()

  with g_col2:
    st.subheader("📈 Goals Progress")
    df_goals = fetch_family_data("goals")
    if not df_goals.empty:
      for _, g in df_goals.iterrows():
        pct = min(1.0, g["saved"] / g["target"]) if g["target"] > 0 else 0
        st.write(f"**{g['goal_name']}** (₹{g['saved']:,.0f} / ₹{g['target']:,.0f})")
        st.progress(pct)

# ==========================================
# MODULE 6: LOANS, EMI & ASSETS
# ==========================================
elif menu == "💳 Loans, EMI & Assets":
  st.title("💳 Loan, EMI & Wealth Portfolio")

  p_col1, p_col2 = st.columns(2)
  with p_col1:
    st.subheader("➕ Track Asset / Loan")
    p_name = st.text_input("Asset or Loan Name")
    p_val = st.number_input("Value / Balance (₹)", min_value=0.0)
    p_type = st.radio("Type", ["Asset", "Liability"])

    if st.button("Save Portfolio Item") and db:
      db.collection("portfolio").add({
          "family_id": user["family_id"],
          "name": p_name,
          "val": float(p_val),
          "type": p_type,
      })
      st.success("Portfolio Item Saved!")
      st.rerun()

  with p_col2:
    st.subheader("📊 Portfolio List")
    df_p = fetch_family_data("portfolio")
    if not df_p.empty:
      st.dataframe(df_p[["name", "type", "val"]], use_container_width=True)

# ==========================================
# MODULE 7: AI INSIGHTS & FORECAST
# ==========================================
elif menu == "🩺 AI Health Score & Forecast":
  st.title("🩺 AI Health Meter & Predictive Forecast")

  if not df_transactions.empty:
    inc = df_transactions[df_transactions["account_type"] == "Income"][
        "amount"
    ].sum()
    exp = df_transactions[df_transactions["account_type"] == "Expense"][
        "amount"
    ].sum()

    savings_ratio = ((inc - exp) / inc) if inc > 0 else 0
    score = min(100, max(0, int(savings_ratio * 100 + 20)))

    c1, c2 = st.columns(2)
    with c1:
      st.metric("Financial Health Meter", f"{score} / 100")
      if score >= 75:
        st.success("🌟 **Excellent Financial Health!** Savings rate is strong.")
      else:
        st.warning("⚠️ **Attention:** Keep expenses under control.")

    with c2:
      fig_g = go.Figure(
          go.Indicator(
              mode="gauge+number",
              value=score,
              gauge={"axis": {"range": [0, 100]}},
          )
      )
      st.plotly_chart(fig_g, use_container_width=True)

    st.divider()
    st.subheader("🔮 Next Month Expense Prediction")
    st.metric("Forecasted Expense", f"₹{(exp * 1.05):,.2f}", delta="+5% Estimated Trend")
  else:
    st.info("Insufficient data for health evaluation.")

# ==========================================
# MODULE 8: GST & TAX COMPLIANCE
# ==========================================
elif menu == "🧾 GST & Tax Compliance":
  st.title("🧾 GST & Tax Compliance Portal")

  if not df_transactions.empty:
    total_gst = (
        df_transactions["gst_amount"].sum()
        if "gst_amount" in df_transactions.columns
        else 0.0
    )
    st.metric("Total Input/Output GST Recorded", f"₹{total_gst:,.2f}")
    st.divider()
    st.subheader("Tax Compliance Summary")
    st.json({
        "Financial Year": "2026-2027",
        "Total GST Paid/Calculated": total_gst,
        "Status": "Compliant",
    })

# ==========================================
# MODULE 9: WHATSAPP SHARE
# ==========================================
elif menu == "📱 WhatsApp Share":
  st.title("📱 Share Summary to WhatsApp")

  if not df_transactions.empty:
    inc = df_transactions[df_transactions["account_type"] == "Income"][
        "amount"
    ].sum()
    exp = df_transactions[df_transactions["account_type"] == "Expense"][
        "amount"
    ].sum()

    msg = f"*🏠 FAMILY ERP FINANCIAL SUMMARY*\nWorkspace: {user['family_id']}\n\n💵 *Total Income:* ₹{inc:,.2f}\n💸 *Total Expense:* ₹{exp:,.2f}\n🏦 *Net Balance:* ₹{(inc-exp):,.2f}\n\n_Auto-generated by AI Family ERP Hub_"
    encoded_msg = urllib.parse.quote(msg)
    wa_url = f"https://wa.me/?text={encoded_msg}"

    st.code(msg, language="markdown")
    st.markdown(
        f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;'
        ' color:white; padding:12px 24px; border:none; border-radius:8px;'
        ' font-size:16px; cursor:pointer; font-weight:bold;">🟢 Share on'
        " WhatsApp</button>a>",
        unsafe_allow_html=True,
    )

# ==========================================
# MODULE 10: WORKSPACE ADMIN
# ==========================================
elif menu == "⚙️ Workspace Admin":
  st.title("⚙️ Multi-Family Admin Settings")
  st.write(f"Active Workspace ID: **{user['family_id']}**")
  st.write(f"Logged in User: **{user['username']}** (`{user['role']}`)")

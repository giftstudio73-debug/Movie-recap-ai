import streamlit as st
import sqlite3
import os
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AI Movie Recap Script Generator", page_icon="🎬", layout="wide")

# Gemini API Key Config ("AQ.Ab8RN6LzZhHAR6k0nTn7dcWzkz1VyL5nLIA-vkIlBR_jmA9W_Q")
GEMINI_API_KEY = "AQ.Ab8RN6LzZhHAR6k0nTn7dcWzkz1VyL5nLIA-vkIlBR_jmA9W_Q"
genai.configure(api_key=GEMINI_API_KEY)

# Admin & Payment Config
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Ah199421"
KPAY_PHONE = "09961668096"
KPAY_NAME = "Ngwa Jon Li"

# Database Initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, credits INTEGER, is_admin INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS topup_requests 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, amount TEXT, tid TEXT, status TEXT)''')
    conn.commit()
    
    # Ensure Admin Account Exists
    c.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USERNAME,))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?, 1)", (ADMIN_USERNAME, ADMIN_PASSWORD, 9999))
        conn.commit()
    conn.close()

init_db()

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = 0

# Functions
def check_user_credits(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT credits FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def update_user_credits(username, new_credits):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET credits = ? WHERE username = ?", (new_credits, username))
    conn.commit()
    conn.close()

# Sidebar Authentication & Navigation
st.sidebar.title("👤 Account & Billing")

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
    
    if menu == "Register":
        st.sidebar.subheader("အကောင့်သစ်ပြုလုပ်ရန်")
        reg_user = st.sidebar.text_input("Username (အသုံးပြုသူအမည်)")
        reg_pass = st.sidebar.text_input("Password (စကားဝှက်)", type="password")
        if st.sidebar.button("Register"):
            if reg_user and reg_pass:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO users VALUES (?, ?, 5, 0)", (reg_user, reg_pass))
                    conn.commit()
                    st.sidebar.success("အကောင့်ဖွင့်လှစ်ခြင်း အောင်မြင်ပါသည်။ Free Credits 5 ကြိမ် ရရှိပါသည်။ Login ဝင်ရောက်ပါ။")
                except sqlite3.IntegrityError:
                    st.sidebar.error("ဒီ Username ဖြင့် အကောင့်ရှိပြီးသားဖြစ်ပါသည်။")
                conn.close()
            else:
                st.sidebar.warning("အချက်အလက်များ ပြည့်စုံစွာ ဖြည့်ပါ။")

    elif menu == "Login":
        st.sidebar.subheader("အကောင့်ဝင်ရောက်ရန်")
        login_user = st.sidebar.text_input("Username")
        login_pass = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (login_user, login_pass))
            user = c.fetchone()
            conn.close()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.is_admin = user[3]
                st.sidebar.success(f"Welcome, {user[0]}!")
                st.rerun()
            else:
                st.sidebar.error("Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။")

else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    user_credits = check_user_credits(st.session_state.username)
    st.sidebar.metric("လက်ကျန် Credits (အကြိမ်)", user_credits)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.is_admin = 0
        st.rerun()

    # Subscription / Top-up Section
    st.sidebar.markdown("---")
    st.sidebar.subheader("💳 ၁ လစာ / Credit ဝယ်ယူရန်")
    st.sidebar.info(f"KPay Phone: **{KPAY_PHONE}**\nAccount: **{KPAY_NAME}**")
    
    topup_amount = st.sidebar.number_input("ငွေပမာဏ (ကျပ်)", min_value=1000, step=1000)
    topup_tid = st.sidebar.text_input("KPay Transaction Last 4 Digits")
    
    if st.sidebar.button("Submit Top-up Request"):
        if topup_tid:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO topup_requests (username, amount, tid, status) VALUES (?, ?, ?, 'Pending')",
                      (st.session_state.username, str(topup_amount), topup_tid))
            conn.commit()
            conn.close()
            st.sidebar.success("တောင်းဆိုချက် ပေးပို့ပြီးပါပြီ။ Admin မှ စစ်ဆေးပြီး အတည်ပြုပေးပါမည်။")
        else:
            st.sidebar.warning("Transaction ID ထည့်ပါ။")

# Main Application Layout
st.title("🎬 AI Movie Recap Script Generator (Myanmar)")

if st.session_state.is_admin:
    st.subheader("🛠 Admin Dashboard (ငွေလွှဲတောင်းဆိုချက်များ စစ်ဆေးရန်)")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, username, amount, tid, status FROM topup_requests WHERE status = 'Pending'")
    requests = c.fetchall()
    conn.close()

    if requests:
        for req in requests:
            req_id, req_user, req_amount, req_tid, req_status = req
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            col1.write(f"User: **{req_user}**")
            col2.write(f"Amount: {req_amount} Ks")
            col3.write(f"TID: {req_tid}")
            if col4.button("Approve (50 Credits ပေးမည်)", key=f"app_{req_id}"):
                current_c = check_user_credits(req_user)
                update_user_credits(req_user, current_c + 50)
                
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("UPDATE topup_requests SET status = 'Approved' WHERE id = ?", (req_id,))
                conn.commit()
                conn.close()
                st.success(f"{req_user} သို့ 50 Credits ထည့်သွင်းပေးပြီးပါပြီ။")
                st.rerun()
    else:
        st.write("လက်ရှိတွင် စစ်ဆေးရန် တောင်းဆိုချက် မရှိပါ။")
    st.markdown("---")

# Generator Interface
if not st.session_state.logged_in:
    st.warning("⚠️ ဇာတ်ညွှန်းများ ထုတ်ယူရန်အတွက် ဘယ်ဘက် Sidebar တွင် အကောင့်အရင် Login ဝင်ရောက်ပေးပါရှင့်။")
else:
    current_credits = check_user_credits(st.session_state.username)
    
    story_input = st.text_area(
        "ဇာတ်လမ်း သို့မဟုတ် ဇာတ်ညွှန်းအကျဉ်း ရိုက်ထည့်ပါ:",
        height=250,
        placeholder="ဥပမာ- ကောင်လေးတစ်ယောက်ဟာ ရှေးဟောင်းသေတ္တာတစ်လုံးကို တွေ့ရှိခဲ့ရာကနေ အတိတ်ကာလကို ခရီးသွားနိုင်တဲ့ စွမ်းအားရရှိခဲ့ပါတယ်။..."
    )

    target_duration = st.selectbox(
        "ဖန်တီးလိုသော ဗီဒီယို ကြာချိန်ကို ရွေးချယ်ပါ:",
        ["၁၅ မိနစ်စာ Recap (အသေးစိတ်)", "၁၀ မိနစ်စာ Recap", "၅ မိနစ်စာ Recap"]
    )

    if st.button("Generate Recap Script", type="primary"):
        if current_credits <= 0 and not st.session_state.is_admin:
            st.error("❌ သင်၏ လက်ကျန် Credit ပြည့်သွားပါပြီ။ ဘယ်ဘက် Sidebar တွင် Credit ထပ်မံဝယ်ယူပါရှင့်။")
        elif not story_input.strip():
            st.warning("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကြောင်းအရာ ရိုက်ထည့်ပါ။")
        else:
            with st.spinner("AI မှ ဇာတ်ညွှန်း ရေးသားနေပါသည်... ခဏစောင့်ပါ..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    မင်းက ကျွမ်းကျင်တဲ့ Movie Recap Script Writer တစ်ယောက်ပါ။
                    အောက်ပါ ဇာတ်လမ်းအကျဉ်းကို အခြေခံပြီး {target_duration} စာကြာမြင့်မယ့် စိတ်ဝင်စားဖွယ် Movie Recap စာသား (Voiceover Script) ကို မြန်မာဘာသာဖြင့် အသေးစိတ် ရေးသားပေးပါ။

                    ဇာတ်လမ်းအကြောင်းအရာ:
                    {story_input}

                    ရေးသားရမည့် ပုံစံ:
                    1. စိတ်ဝင်စားဖွယ် Intro (စတင်ပျိုးထောင်ခြင်း)
                    2. ဇာတ်လမ်း အစိတ်ပိုင်းအလိုက် အသေးစိတ် ရှင်းလင်းချက်များ (Detailed Scene-by-Scene Description)
                    3. Climax နှင့် အမှတ်မထင် အကေ့အကွက်များ (Twists & Climax)
                    4. ဇာတ်သိမ်းနှင့် သုံးသပ်ချက် Outro
                    5. စာဖတ်သူ/နားထောင်သူ ဆွဲဆောင်မှုရှိစေမည့် စကားပြောဟန်ဖြင့် ရေးပေးပါရှင်။
                    """
                    response = model.generate_content(prompt)
                    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
မင်းက ကျွမ်းကျင်တဲ့ Movie Recap Script Writer တစ်ယောက်ပါ။
အောက်ပါ ဇာတ်လမ်းအကျဉ်းကို အခြေခံပြီး {target_duration} အကြာမြင့်ဖြင့်မည့် စိတ်ဝင်စားဖွယ် Movie Recap စာသားတစ်ခုကို ရေးပေးပါ။

ဇာတ်လမ်းအကြောင်းအရာ:
{story_input}

ရေးသားရမည့် ပုံစံ:
1. စိတ်ဝင်စားဖွယ် Intro (စတင်ပျိုးထောင်ခြင်း)
2. ဇာတ်လမ်း အစိတ်ပိုင်းအလိုက် အသေးစိတ် ရှင်းလင်းချက်များ (Detailed Scene-by-Scene Description)
3. Climax နှင့် အမှတ်တထင် အတွေ့အကြုံများ (Twists & Climax)
4. ဇာတ်သိမ်းနှင့် သုံးသပ်ချက် Outro
5. စာဖတ်သူ/နားထောင်သူ ဆွဲဆောင်မှုရှိစေမည့် စကားပြောဟန်ဖြင့် ရေးပေးပါရန်။
"""
        response = model.generate_content(prompt)

        # ကြာချိန်အလိုက် Credit ကုန်ကျစရိတ် သတ်မှတ်ခြင်း
        if target_duration == "၅ မိနစ်စာ Recap":
            credit_cost = 1
        elif target_duration == "၁၀ မိနစ်စာ Recap":
            credit_cost = 5
        elif target_duration == "၁၅ မိနစ်စာ Recap (အသေးစိတ်)":
            credit_cost = 10
        else:
            credit_cost = 1

        # Deduct credit
        if not st.session_state.is_admin:
            update_user_credits(st.session_state.username, current_credits - credit_cost)

        st.success("✨ ဇာတ်ညွှန်း ဖန်တီးမှု အောင်မြင်ပါသည်။")
        st.subheader("📝 ထွက်ရှိလာသော Movie Recap Script:")
        st.markdown(response.text)
        st.rerun()

    except Exception as e:
        st.error(f"အမှားယွင်း ဖြစ်ပေါ်သွားပါသည်: {str(e)}")
        
       

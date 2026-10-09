import streamlit as st
import sqlite3
import os
import yt_dlp
import whisper
from googletrans import Translator

st.set_page_config(page_title="YouTube Movie Recap AI", page_icon="🎬", layout="wide")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Ah199421"
KPAY_PHONE = "09961668096"
KPAY_NAME = "Ngwa Jon Li"

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, credits INTEGER, is_admin INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS topup_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, amount TEXT, phone TEXT, status TEXT)')
    conn.commit()
    c.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USERNAME,))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, 9999, 1)", (ADMIN_USERNAME, ADMIN_PASSWORD))
        conn.commit()
    conn.close()

init_db()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = 0

if not st.session_state.logged_in:
    st.title("🎬 YouTube Movie Recap AI - Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.is_admin = user[3]
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register"):
            if new_user and new_pass:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO users VALUES (?, ?, ?, 0)", (new_user, new_pass, 5))
                    conn.commit()
                    st.success("Account created successfully! Please login.")
                except sqlite3.IntegrityError:
                    st.warning("Username already exists.")
                conn.close()
            else:
                st.warning("Please fill in all fields.")
else:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT credits FROM users WHERE username = ?", (st.session_state.username,))
    current_credits = c.fetchone()[0]
    conn.close()

    st.sidebar.title(f"Welcome, {st.session_state.username}")
    st.sidebar.metric(label="Available Credits", value=f"{current_credits} Credits")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("Top Up Credits (KPay)")
    st.sidebar.text(f"KPay: {KPAY_PHONE}\nName: {KPAY_NAME}\n1000 MMK = 5 Credits")
    topup_amount = st.sidebar.selectbox("Select Package", ["1000 MMK (5 Credits)", "5000 MMK (30 Credits)", "10000 MMK (70 Credits)"])
    sender_phone = st.sidebar.text_input("Your KPay Phone / Name")
    
    if st.sidebar.button("Submit Top Up Request"):
        if sender_phone:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO topup_requests (username, amount, phone, status) VALUES (?, ?, ?, ?)", (st.session_state.username, topup_amount, sender_phone, "Pending"))
            conn.commit()
            conn.close()
            st.sidebar.success("Top up request sent successfully!")
        else:
            st.sidebar.warning("Please enter your details.")

    if st.session_state.is_admin == 1:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Admin Panel")
        if st.sidebar.checkbox("View Top-up Requests"):
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT id, username, amount, phone, status FROM topup_requests WHERE status = 'Pending'")
            requests = c.fetchall()
            conn.close()
            if requests:
                for req in requests:
                    st.sidebar.write(f"ID: {req[0]} | User: {req[1]} | {req[2]} | By: {req[3]}")
                    if st.sidebar.button(f"Approve ID {req[0]}", key=f"app_{req[0]}"):
                        add_cr = 5 if "1000" in req[2] else (30 if "5000" in req[2] else 70)
                        conn = sqlite3.connect('database.db')
                        c = conn.cursor()
                        c.execute("UPDATE users SET credits = credits + ? WHERE username = ?", (add_cr, req[1]))
                        c.execute("UPDATE topup_requests SET status = 'Approved' WHERE id = ?", (req[0],))
                        conn.commit()
                        conn.close()
                        st.sidebar.success(f"Approved ID {req[0]}!")
                        st.rerun()
            else:
                st.sidebar.info("No pending requests.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🎬 YouTube Movie Recap AI (Myanmar Translated)")
    st.write("YouTube ဗီဒီယိုလင့်ခ်ကို ထည့်သွင်းပြီး မြန်မာဘာသာသို့ အလိုအလျောက် ပြန်ဆိုထုတ်လုပ်လိုက်ပါ။")

    youtube_url = st.text_input("Enter YouTube Video Link:")

    if st.button("Generate Recap"):
        if not youtube_url:
            st.warning("ကျေးဇူးပြု၍ YouTube လင့်ခ် ထည့်ပါ။")
        elif current_credits < 1:
            st.error("Credits မလုံလောက်ပါ။ KPay ဖြင့် ငွေဖြည့်ပါ။")
        else:
            with st.spinner("ဗီဒီယိုကို ဒေါင်းလုဒ်လုပ်နေပါပြီ..."):
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'audio.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                try:
                    if os.path.exists("audio.mp3"):
                        os.remove("audio.mp3")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                    
                    st.info("အသံဖိုင်ကို AI ဖြင့် စာသားပြောင်းနေပါပြီ...")
                    model = whisper.load_model("tiny")
                    result = model.transcribe("audio.mp3")
                    english_text = result["text"]

                    st.info("မြန်မာဘာသာသို့ ဘာသာပြန်ဆိုနေပါပြီ...")
                    translator = Translator()
                    translation = translator.translate(english_text, dest='my')
                    myanmar_text = translation.text

                    conn = sqlite3.connect('database.db')
                    c = conn.cursor()
                    c.execute("UPDATE users SET credits = credits - 1 WHERE username = ?", (st.session_state.username,))
                    conn.commit()
                    conn.close()

                    st.success("အောင်မြင်စွာ ထုတ်လုပ်ပြီးပါပြီ!")
                    st.subheader("📝 Movie Recap (Myanmar)")
                    st.write(myanmar_text)

                except Exception as e:
                    st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")

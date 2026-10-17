import streamlit as st
import sqlite3
import os
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="Text-to-Movie Recap AI", page_icon="🎬", layout="wide")

# Gemini API Key ချိန်ညှိရန်
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
genai.configure(api_key=GEMINI_API_KEY)

# Admin & Database Configuration
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

# UI Design
st.title("🎬 AI Movie Recap Script Generator (Myanmar)")
st.write("သင့်ကိုယ်ပိုင် ဇာတ်လမ်းအကျဉ်း သို့မဟုတ် ဇာတ်ညွှန်းကို ရိုက်ထည့်ပြီး ၁၅ မိနစ်စာ Movie Recap စာသားအပြည့်အစုံကို ဖန်တီးလိုက်ပါ။")

# Input Section
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
    if not story_input.strip():
        st.warning("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကြောင်းအရာ ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("AI မှ ၁၅ မိနစ်စာ Movie Recap ဇာတ်ညွှန်း ရေးသားနေပါသည်... ခဏစောင့်ပါ..."):
            try:
                # Gemini Model ခေါ်ယူခြင်း
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
                
                st.success("✨ ဇာတ်ညွှန်း ဖန်တီးမှု အောင်မြင်ပါသည်။")
                st.subheader("📝 ထွက်ရှိလာသော Movie Recap Script:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"အမှားယွင်း ဖြစ်ပေါ်သွားပါသည်: {str(e)}")

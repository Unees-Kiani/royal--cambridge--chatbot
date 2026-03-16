import streamlit as st
import pandas as pd
from PIL import Image
import os
from openai import OpenAI
import sqlite3
from datetime import datetime
from streamlit_lottie import st_lottie
import requests

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="Royal Cambridge School", page_icon="assets/logo.png", layout="wide")

# ---------------- STYLING ----------------
st.markdown("""
<style>
/* Background Gradient Animation */
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    animation: gradientBG 10s ease infinite;
    color:white;
}
@keyframes gradientBG {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}
h1,h2,h3,h4{text-align:center;}
.stButton>button {
    background:#FFD700;color:black;border-radius:10px;font-weight:bold;font-size:16px;
    transition: 0.3s;
}
.stButton>button:hover {background:#FFC300;color:white;transform: scale(1.05);}
.card {padding:20px;background: rgba(255,255,255,0.1);border-radius:15px;box-shadow:2px 2px 15px #000;}
</style>
""", unsafe_allow_html=True)

# ---------------- LOTTIE FUNCTION ----------------
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---------------- DATABASE ----------------
conn = sqlite3.connect("school.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT, role TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS notices(
id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, message TEXT, date TEXT)""")
conn.commit()

# ---------------- HEADER ----------------
try:
    logo = Image.open("assets/logo.png")
    st.image(logo, width=120)
except:
    st.warning("Logo not found")
st.markdown("<h1>Royal Cambridge School</h1><h4>Ari Syedan, Islamabad</h4>", unsafe_allow_html=True)

# ---------------- NAVIGATION ----------------
nav = st.sidebar.selectbox("Navigation", ["Home","Login","Signup","Gallery","Contact"])

# ---------------- HOME ----------------
if nav=="Home":
    st.subheader("Welcome to the School Portal")
    st_lottie(load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_jcikwtux.json"), height=250)
    st.write("Smart portal for students, parents, and teachers with AI assistant, homework, timetable, and more!")

# ---------------- SIGNUP ----------------
elif nav=="Signup":
    st.subheader("Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Student","Parent","Teacher"])
    if st.button("Signup"):
        c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",(name,email,password,role))
        conn.commit()
        st.success("Account created successfully!")

# ---------------- LOGIN ----------------
elif nav=="Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
        user = c.fetchone()
        if user:
            st.success(f"Welcome {user[1]} ({user[4]})")
            role = user[4]

            # ---------------- TEACHER DASHBOARD ----------------
            if role=="Teacher":
                st.subheader("Teacher Dashboard")
                option = st.radio("Select Feature", ["Post Notice","View Homework","View Attendance","View Timetable","AI Tutor"])
                if option=="Post Notice":
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    title = st.text_input("Title")
                    msg = st.text_area("Message")
                    if st.button("Post"):
                        c.execute("INSERT INTO notices(title,message,date) VALUES(?,?,?)",
                                  (title,msg,str(datetime.now())))
                        conn.commit()
                        st.success("Notice Posted!")
                    st.markdown('</div>', unsafe_allow_html=True)

                elif option=="View Homework":
                    st.write("Homework Uploads")
                    os.makedirs("homework_uploads", exist_ok=True)
                    files = os.listdir("homework_uploads")
                    for f in files:
                        st.write(f)
                        with open(os.path.join("homework_uploads", f), "rb") as file:
                            st.download_button(label=f"Download {f}", data=file, file_name=f)

                elif option=="View Attendance":
                    st.write("Attendance Chart")
                    df = pd.DataFrame({"Month":["Jan","Feb","Mar","Apr","May"],"Attendance":[90,85,92,88,95]})
                    st.line_chart(df.set_index("Month"))

                elif option=="View Timetable":
                    st.write("Timetable")
                    class_num = st.selectbox("Select Class", [f"Class {i}" for i in range(1,11)])
                    tt = pd.DataFrame({"Day":["Mon","Tue","Wed","Thu","Fri"], "Period1":["Math","English","Science","Math","Comp"],
                                       "Period2":["Urdu","Math","Eng","Science","Math"], "Period3":["Science","Urdu","Math","Eng","Islamiat"]})
                    st.table(tt)

                elif option=="AI Tutor":
                    question = st.text_input("Ask AI")
                    if st.button("Ask AI Tutor"):
                        try:
                            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                            response = client.chat.completions.create(model="gpt-3.5-turbo",
                                messages=[{"role":"user","content":question}])
                            answer = response.choices[0].message['content']
                            st.success(answer)
                        except:
                            st.error("AI not available")

# ---------------- GALLERY ----------------
elif nav=="Gallery":
    st.subheader("School Gallery")
    col1,col2,col3=st.columns(3)
    with col1: st.image("assets/school1.jpg")
    with col2: st.image("assets/school2.jpg")
    with col3: st.image("assets/school3.jpg")

# ---------------- CONTACT ----------------
elif nav=="Contact":
    st.subheader("Contact Us")
    st.write("📍 Ari Syedan, Islamabad")
    st.write("📞 +92-300-XXXXXXX")
    st.write("✉ royalcambridge@gmail.com")

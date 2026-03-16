import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from PIL import Image
import os
from openai import OpenAI

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Royal Cambridge School",
    page_icon="logo.png",
    layout="wide"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
color:white;
}

h1,h2,h3,h4{
text-align:center;
}

.stButton>button{
background:#FFD700;
color:black;
border-radius:10px;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("school.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
password TEXT,
role TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS notices(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
message TEXT,
date TEXT
)""")

conn.commit()

# ---------------- HEADER ----------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=120)
except:
    st.warning("Logo not found")

st.markdown("""
<h1>Royal Cambridge School</h1>
<h4>Ari Syedan, Islamabad</h4>
""", unsafe_allow_html=True)

st.info("Welcome to the Royal Cambridge School Smart Portal 🤖")

# ---------------- SIDEBAR MENU ----------------
menu = st.sidebar.selectbox(
"Navigation",
["Home","Login","Signup","AI Tutor","Homework","Notices","Timetable","Attendance","Gallery","Contact"]
)

# ---------------- HOME ----------------
if menu == "Home":

    st.title("School Smart Portal")

    st.write("""
This portal helps students, parents and teachers stay connected.

Features:
• AI Study Assistant  
• Homework updates  
• School notices  
• Attendance tracking  
• Timetable  
• School gallery
""")

# ---------------- SIGNUP ----------------
elif menu == "Signup":

    st.subheader("Create Account")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    role = st.selectbox("Role",["Student","Parent","Teacher"])

    if st.button("Signup"):

        c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
        (name,email,password,role))

        conn.commit()

        st.success("Account created successfully!")

# ---------------- LOGIN ----------------
elif menu == "Login":

    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        c.execute("SELECT * FROM users WHERE email=? AND password=?",
        (email,password))

        user = c.fetchone()

        if user:
            st.success("Login successful!")
            st.write("Welcome:", user[1])
            st.write("Role:", user[4])
        else:
            st.error("Invalid credentials")

# ---------------- AI TUTOR ----------------
elif menu == "AI Tutor":

    st.subheader("AI Study Assistant")

    question = st.text_input("Ask a study question")

    if st.button("Ask AI"):

        try:
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":question}]
            )

            answer = response.choices[0].message.content

            st.success(answer)

        except:
            st.error("AI service not available. Check API key.")

# ---------------- HOMEWORK ----------------
elif menu == "Homework":

    st.subheader("Homework Section")

    uploaded_file = st.file_uploader("Upload Homework")

    if uploaded_file:

        with open(uploaded_file.name,"wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("Homework uploaded successfully")

# ---------------- NOTICES ----------------
elif menu == "Notices":

    st.subheader("School Notices")

    title = st.text_input("Notice Title")
    message = st.text_area("Notice Message")

    if st.button("Post Notice"):

        c.execute("INSERT INTO notices(title,message,date) VALUES(?,?,?)",
        (title,message,str(datetime.now())))

        conn.commit()

        st.success("Notice Posted")

    st.markdown("---")

    st.subheader("All Notices")

    c.execute("SELECT title,message,date FROM notices ORDER BY id DESC")

    notices = c.fetchall()

    for n in notices:

        st.warning("📢 " + n[0])
        st.write(n[1])
        st.caption(n[2])

# ---------------- TIMETABLE ----------------
elif menu == "Timetable":

    st.subheader("School Timetable")

    data = {
    "Day":["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "Period 1":["Math","English","Science","Math","Computer"],
    "Period 2":["Urdu","Math","English","Science","Math"],
    "Period 3":["Science","Urdu","Math","English","Islamiat"]
    }

    st.table(data)

# ---------------- ATTENDANCE ----------------
elif menu == "Attendance":

    st.subheader("Attendance Chart")

    data = pd.DataFrame({
    "Month":["Jan","Feb","Mar","Apr","May"],
    "Attendance":[90,85,92,88,95]
    })

    st.line_chart(data.set_index("Month"))

# ---------------- GALLERY ----------------
elif menu == "Gallery":

    st.subheader("School Gallery")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.image("school1.jpg")

    with col2:
        st.image("school2.jpg")

    with col3:
        st.image("school3.jpg")

# ---------------- CONTACT ----------------
elif menu == "Contact":

    st.subheader("Contact Royal Cambridge School")

    st.write("📍 Ari Syedan, Islamabad")
    st.write("📞 +92-300-XXXXXXX")
    st.write("✉ royalcambridge@gmail.com")

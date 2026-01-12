import streamlit as st
import hashlib

st.set_page_config(page_title="Тайлан", layout="wide")

# ---------------------------
# 1. Load users from secrets
# ---------------------------
USERS = st.secrets["users"]
#st.write("Loaded users:", list(USERS.keys()))
# ---------------------------
# 2. Session state init
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ---------------------------
# 3. Login UI
# ---------------------------
def login_page():
    st.title("Нэвтрэх")

    username = st.text_input("Хэрэглэгчийн нэр")
    password = st.text_input("Нууц үг", type="password")

    if st.button("Нэвтрэх"):
        hashed = hashlib.sha256(password.encode()).hexdigest()

        if username in USERS and USERS[username] == hashed:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Буруу хэрэглэгчийн нэр эсвэл нууц үг")

# ---------------------------
# 4. Block app if not logged in
# ---------------------------
if not st.session_state.authenticated:
    login_page()
    st.stop()

# ---------------------------
# 5. Logout
# ---------------------------
with st.sidebar:
    st.write(f"Нэвтэрсэн: {st.session_state.username}")
    if st.button("Гарах"):
        st.session_state.clear()
        st.rerun()

# ---------------------------
# 6. Navigation
# ---------------------------
pages = {
    "Эхлэл": [
        st.Page("home.py", title="ДАТАСЕТ ТОВЧ ТАЙЛАН"),
    ],
    "Тайлан": [
        st.Page("page1.py", title="OVERVIEW"),
        st.Page("page2.py", title="PARTY MIXING"),
        st.Page("page3.py", title="CANDIDATE BEHAVIOR"),
        st.Page("page4.py", title="CROSS-CONTEST ALIGNMENT"),
    ],
}

pg = st.navigation(pages)
pg.run()

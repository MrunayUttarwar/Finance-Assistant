import streamlit as st
import sqlite3
import bcrypt

st.set_page_config(page_title="Smart Personal Finance Assistant", layout="wide")

# Connect to SQLite Database
def connect_db():
    conn = sqlite3.connect("users.db")
    return conn, conn.cursor()

# Create Users Table (Runs Once)
conn, c = connect_db()
c.execute('''CREATE TABLE IF NOT EXISTS users3 (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()
conn.close()

# Hash Password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify Password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Check if user exists and verify password
def check_user(username, password):
    conn, c = connect_db()
    c.execute("SELECT password FROM users3 WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user and verify_password(password, user[0])

# Register User
def register_user(username, password):
    conn, c = connect_db()
    hashed_pw = hash_password(password)
    try:
        c.execute("INSERT INTO users3 (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

# Reset Password
def reset_password(username, new_password):
    conn, c = connect_db()
    hashed_pw = hash_password(new_password)
    c.execute("UPDATE users3 SET password=? WHERE username=?", (hashed_pw, username))
    conn.commit()
    conn.close()

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_register" not in st.session_state:
    st.session_state.show_register = False
if "show_reset" not in st.session_state:
    st.session_state.show_reset = False

# Custom Styling
st.markdown(
    '''
    <style>
    .stApp { background-color: black; color: white; }
    .sidebar .sidebar-content { background-color: #1f1f1f; padding: 20px; border-right: 3px solid #00bfa5; }
    .profile-container { position: absolute; top: 15px; right: 20px; color: white; font-weight: bold; }
    </style>
    ''',
    unsafe_allow_html=True
)

# Upper Right Profile/Login Section
col1, col2 = st.columns([9, 2])  # Align right

with col2:
    st.markdown(
        "<div style='text-align: right; font-weight: bold;'>"
        f"👤 {st.session_state.username}" if st.session_state.logged_in else "",
        unsafe_allow_html=True
    )

    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.show_login = False
            st.session_state.show_register = False
            st.session_state.show_reset = False
            st.rerun()
    else:
        col_login, col_register = st.columns([1, 1])  # Side by side buttons
        with col_login:
            if st.button("Login", use_container_width=True):
                st.session_state.show_login = True
                st.session_state.show_register = False
                st.session_state.show_reset = False
        with col_register:
            if st.button("Register", use_container_width=True):
                st.session_state.show_register = True
                st.session_state.show_login = False
                st.session_state.show_reset = False

# Login Function
if st.session_state.show_login:
    st.subheader("Login")
    with st.form("Login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("Invalid credentials!")
    
    # Forgot Password
    if st.button("Forgot Password?"):
        st.session_state.show_login = False
        st.session_state.show_reset = True
        st.rerun()

# Register Function
if st.session_state.show_register:
    st.subheader("Register")
    with st.form("Register"):
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if register_user(new_user, new_pass):
                st.success("Account created successfully! Please login.")
                st.session_state.show_register = False
                st.session_state.show_login = True
                st.rerun()
            else:
                st.error("Username already exists! Try a different one.")

# Password Reset Function
if st.session_state.show_reset:
    st.subheader("Reset Password")
    with st.form("Reset Password"):
        username = st.text_input("Enter Your Username")
        new_password = st.text_input("Enter New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Reset Password")
        
        if submit:
            if new_password == confirm_password:
                conn, c = connect_db()
                c.execute("SELECT * FROM users3 WHERE username=?", (username,))
                user = c.fetchone()
                conn.close()
                
                if user:
                    reset_password(username, new_password)
                    st.success("Password reset successful! Please log in.")
                    st.session_state.show_reset = False
                    st.session_state.show_login = True
                    st.rerun()
                else:
                    st.error("Username not found!")
            else:
                st.error("Passwords do not match!")

# Main Page Content
st.markdown("<h1 style='text-align: center; font-size: 3.5rem; color: #00bfa5;'>💰 Smart Personal Finance Assistant</h1>", unsafe_allow_html=True)
st.write("### Explore Our Modules")
st.write("""
- **Expense Categorization**: Powered by BERT for accurate classification of expenses into 50 categories.
- **Budget Recommendation**: Reinforcement Learning ensures tailored budgeting based on your expenses.
""")

st.write("### Get Started")

# 🚀 Enforce Login for Module Access
if st.button("📊 Go to Expense Categorization"):
    if st.session_state.logged_in:
        st.switch_page("pages/1_Expense_Categorization.py")
    else:
        st.warning("⚠️ Please log in or register to access this module.")

if st.button("💡 Go to Budget Recommendation"):
    if st.session_state.logged_in:
        st.switch_page("pages/2_Budget_Recommendation.py")
    else:
        st.warning("⚠️ Please log in or register to access this module.")

st.markdown("<hr><p style='text-align:center; font-size: 0.9rem;'>© 2025 Smart Personal Finance Assistant | Built with ❤️ and AI.</p>", unsafe_allow_html=True)
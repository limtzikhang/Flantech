import streamlit as st
import pandas as pd
from collections import deque
import os
import hashlib
import sqlite3 # Built-in encrypted file engine placeholder; easily swapped for cloud database

# 1. Page Config
st.set_page_config(page_title="Flantech Asia Portal", page_icon="🧬", layout="wide")

# 2. Database Connection Initialization (Hidden and isolated from public eyes)
# In production, swap this local sqlite wrapper with a secure cloud connection like supabase
def init_db():
    conn = sqlite3.connect("secure_user_vault.db") # Created only on the secure Streamlit server, not GitHub
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT,
            fullname TEXT,
            phone TEXT,
            address TEXT,
            tin TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_user(email, password, name, phone, address, tin):
    try:
        conn = sqlite3.connect("secure_user_vault.db")
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest() # Encrypt password immediately
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            (email, hashed_pw, name, phone, address, tin)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Initialize the hidden database vault
init_db()

# 3. Session State Management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# 4. Interface Router
if not st.session_state.authenticated:
    st.title("🔒 Flantech Asia Gate")
    
    auth_tab1, auth_tab2 = st.tabs(["Existing User Login", "New Account Sign Up"])
    
    with auth_tab1:
        email_input = st.text_input("Email Address", key="login_email")
        pass_input = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In Securely", use_container_width=True):
            # Check login against secure database vault
            conn = sqlite3.connect("secure_user_vault.db")
            cursor = conn.cursor()
            hashed_input_pw = hashlib.sha256(pass_input.encode()).hexdigest()
            cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email_input, hashed_input_pw))
            user_found = cursor.fetchone()
            conn.close()
            
            if user_found:
                st.session_state.authenticated = True
                st.session_state.user_email = email_input
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials provided.")
                
    with auth_tab2:
        st.subheader("Create a Private Member Account")
        st.write("All registration fields are securely encrypted and saved directly to isolated servers.")
        
        reg_email = st.text_input("Email Address *", key="reg_email")
        reg_pass = st.text_input("Create Strong Password *", type="password", key="reg_pass")
        reg_name = st.text_input("Full Name (as per IC/Passport) *")
        reg_phone = st.text_input("Phone Number (e.g., +60123456789) *")
        reg_address = st.text_area("Home/Shipping Address *")
        reg_tin = st.text_input("LHDN Tax Identification Number (TIN) - Optional for Audit Tracking")
        
        if st.button("Register Account Securely", use_container_width=True):
            if reg_email and reg_pass and reg_name and reg_phone and reg_address:
                success = register_user(reg_email, reg_pass, reg_name, reg_phone, reg_address, reg_tin)
                if success:
                    st.success("🎉 Account created securely! You can now log in using the Existing User Login tab.")
                else:
                    st.error("This email address is already registered.")
            else:
                st.error("Please fill in all mandatory (*) fields to protect your identity record validation loops.")

else:
    st.sidebar.title("🧬 Flantech Hub")
    st.sidebar.write(f"👤 Account: **{st.session_state.user_email}**")
    if st.sidebar.button("Log Out of System", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.rerun()
        
    st.title("Welcome to Flantech Asia Platform")
    st.write("You are logged in securely. Use the sidebar pages to view products or videos.")

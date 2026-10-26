import streamlit as st
import pandas as pd
from collections import deque
import os
import hashlib
import sqlite3 # Built-in encrypted file engine placeholder; easily swapped for cloud database
import firebase_admin
from firebase_admin import credentials, firestore
import json

# 1. Page Configuration
st.set_page_config(page_title="Flantech Asia Portal", page_icon="🧬", layout="wide")

# 2. Securely Initialize Firebase App using Cloud Secrets
if not firebase_admin._apps:
    try:
        # Convert the Streamlit secrets dictionary directly into a proper credential token mapping
        firebase_secrets = dict(st.secrets["firebase"])
        # Fix potential newline escaping issues inside the private key configuration string
        firebase_secrets["private_key"] = firebase_secrets["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Failed to load cloud secrets validation matrix: {e}")

# Instantiate the active Firestore reference pointer engine
db = firestore.client()

# 3. Database Management Logic Functions (Consumes exactly 1 Read/Write per transaction call)
def register_user_in_firebase(email, password, name, phone, address, tin):
    cleaned_email = email.strip().lower()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    user_ref = db.collection("users").document(cleaned_email)
    
    # Check if the account record document already exists first to prevent overrides
    if user_ref.get().exists:
        return False
        
    payload = {
        "email": cleaned_email,
        "password": hashed_pw,
        "fullname": name,
        "phone": phone,
        "address": address,
        "tin": tin,
        "wallet_cash_myr": 0.00,
        "wallet_points": 0.00
    }
    try:
        user_ref.set(payload)
        return True
    except Exception:
        return False

def verify_firebase_login(email, password):
    cleaned_email = email.strip().lower()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        user_ref = db.collection("users").document(cleaned_email).get()
        if user_ref.exists:
            user_data = user_ref.to_dict()
            if user_data["password"] == hashed_pw:
                return True
        return False
    except Exception:
        return False

# 4. Session State Management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# 5. Interface Login Gate Router
if not st.session_state.authenticated:
    st.title("🔒 Flantech Asia Gate")
    
    auth_tab1, auth_tab2 = st.tabs(["Existing User Login", "New Account Sign Up"])
    
    with auth_tab1:
        email_input = st.text_input("Email Address", key="login_email")
        pass_input = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In Securely", use_container_width=True):
            if verify_firebase_login(email_input, pass_input):
                st.session_state.authenticated = True
                st.session_state.user_email = email_input.strip().lower()
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials or user account records not found.")
                
    with auth_tab2:
        st.subheader("Create a Private Member Account")
        st.write("All registration fields are securely routed directly into an isolated cloud database vault.")
        
        reg_email = st.text_input("Email Address *", key="reg_email")
        reg_pass = st.text_input("Create Strong Password *", type="password", key="reg_pass")
        reg_name = st.text_input("Full Name (as per IC/Passport) *")
        reg_phone = st.text_input("Phone Number (e.g., +60123456789) *")
        reg_address = st.text_area("Home/Shipping Address *")
        reg_tin = st.text_input("LHDN Tax Identification Number (TIN) - Optional for Audit Tracking")
        
        if st.button("Register Account Securely", use_container_width=True):
            if reg_email and reg_pass and reg_name and reg_phone and reg_address:
                success = register_user_in_firebase(reg_email, reg_pass, reg_name, reg_phone, reg_address, reg_tin)
                if success:
                    st.success("🎉 Account successfully saved to Firebase cloud! Switch to the Login tab to enter.")
                else:
                    st.error("Registration failed. This email might already be taken or connection failed.")
            else:
                st.error("Please fill in all mandatory (*) fields.")

else:
    st.sidebar.title("🧬 Flantech Hub")
    st.sidebar.write(f"👤 Account: **{st.session_state.user_email}**")
    if st.sidebar.button("Log Out of System", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.rerun()
        
    st.title("Welcome to Flantech Asia Platform")
    st.write("You are logged in securely. All user details are isolated safely inside your private Firebase Firestore vault cluster.")

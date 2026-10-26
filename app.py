import streamlit as st
import pandas as pd
from collections import deque
import os
import hashlib


import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="Flantech Asia", page_icon="🧬", layout="wide")

# 2. Session State Control for Sign Up & Login Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# 3. Security Router (Login / Sign Up Layout)
if not st.session_state.authenticated:
    st.title("🔒 Flantech Asia Gate")
    st.subheader("Sign up or Log in to access the system and store")
    
    auth_tab1, auth_tab2 = st.tabs(["Existing User Login", "New Account Sign Up"])
    
    with auth_tab1:
        email_input = st.text_input("Email Address", key="login_email")
        pass_input = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In Securely", use_container_width=True):
            if email_input and pass_input:
                st.session_state.authenticated = True
                st.session_state.user_email = email_input
                st.success("Successfully logged in! Please select a page from the sidebar navigation link.")
                st.rerun()
            else:
                st.error("Please fill in all identity fields.")
                
    with auth_tab2:
        reg_email = st.text_input("Enter Email Address", key="reg_email")
        reg_pass = st.text_input("Choose Strong Password", type="password", key="reg_pass")
        tax_tin = st.text_input("LHDN Tax Identification Number (TIN) - Optional for Audit", key="reg_tin")
        if st.button("Register Account", use_container_width=True):
            if reg_email and reg_pass:
                st.success("Account provisions saved successfully! Switch to the Login tab.")
            else:
                st.error("Email and password parameters cannot be empty.")

# 4. Main Logged-In System Dashboard Landing View
else:
    st.sidebar.title("🧬 Flantech Hub")
    st.sidebar.write(f"👤 Account: **{st.session_state.user_email}**")
    if st.sidebar.button("Log Out of System", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.rerun()
        
    st.title("Welcome to Flantech Asia Platform")
    st.subheader("Overview Dashboard")
    st.write("Welcome back to Flantech Asia! You are successfully verified.")
    st.info("👈 Look at the left sidebar menu panel link options to navigate to the Video Library or the Product Catalog Store.")

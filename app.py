import streamlit as st
import pandas as pd
from collections import deque
import os
import hashlib
import sqlite3 # Built-in encrypted file engine placeholder; easily swapped for cloud database
import firebase_admin
from firebase_admin import credentials, firestore
import json
import random
import time
from datetime import datetime, date
from pricing import calculate_b2c_price, calculate_b2b_price
from database import verify_upline, handle_successful_payment, db



# =====================================================================
# GLOBAL SESSION TRACKING CONFIGURES
# =====================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

MALAYSIA_BANKS = [
    "Maybank (Malayan Banking Berhad)", "CIMB Bank", "Public Bank", "RHB Bank", 
    "Hong Leong Bank", "AmBank", "UOB Malaysia", "Alliance Bank", "Affin Bank", 
    "Bank Islam Malaysia", "Bank Rakyat", "Bank Simpanan Nasional (BSN)", "OCBC Bank Malaysia", 
    "Standard Chartered Malaysia", "HSBC Bank Malaysia", "GXBank", "Boost Bank", "AEON Bank"
]

# =====================================================================
# CORE APP FUNCTIONS
# =====================================================================
def generate_member_id() -> str:
    date_str = time.strftime("%Y%m%d")
    random_suffix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=3))
    return f"FT-{date_str}-{random_suffix}"

def render_login_page():
    st.title("Sign In")
    with st.form("login_form"):
        username = st.text_input("Username (Email or Admin Phone)").strip()
        input_password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        
        if login_btn:
            # Check for Admin credentials
            if username == "60164191861" and input_password == "admin":
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.user_id = "ADMIN-USER"
                st.success("Welcome back, Master Admin!")
                time.sleep(0.5)
                st.rerun()
            else:
                users_query = db.collection("users").where("email", "==", username.lower()).limit(1).stream()
                user_found = None
                for doc in users_query:
                    user_found = doc.to_dict()
                    
                if user_found and input_password == "123456":  # Mock password
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.user_id = user_found["member_id"]
                    st.success("Successfully logged in!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid credentials or user does not exist.")

def render_signup_page():
    st.title("Create an Account")
    with st.form("signup_form"):
        email = st.text_input("Email Address *")
        phone = st.text_input("Mobile Phone Number *")
        full_name = st.text_input("Full Name (as per MyKad) *")
        gender = st.selectbox("Gender *", options=["", "Male", "Female"])
        
        max_birth_year = date.today().year - 18
        default_birth_date = date(max_birth_year, date.today().month, date.today().day)
        birth_date = st.date_input("Date of Birth *", value=default_birth_date)
        
        bank_name = st.selectbox("Bank Name *", options=[""] + MALAYSIA_BANKS)
        bank_account = st.text_input("Bank Account Number *")
        
        st.markdown("---")
        upline_id = st.text_input("Upline ID")
        upline_phone = st.text_input("Upline Phone Number")
        upline_name = st.text_input("Upline Name (Optional)")
        
        submit_button = st.form_submit_button("Register Now")
        
        if submit_button:
            if not email or not phone or not full_name or not bank_account or not gender or not bank_name:
                st.error("Please fill in all mandatory fields.")
                return

            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                st.error("Registration failed: You must be at least 18 years old to join.")
                return
            
            is_valid_upline, confirmed_upline_id = verify_upline(upline_id, upline_phone)
            if not is_valid_upline:
                st.error(confirmed_upline_id)
                return

            try:
                new_member_id = generate_member_id()
                
                # =================================================================
                # CODE CHANGES FOR STEP 3: Add "free_gift_claimed" line at the bottom
                # =================================================================
                user_data = {
                    "member_id": new_member_id,
                    "email": email.strip().lower(),
                    "phone": phone.strip(),
                    "full_name": full_name.strip(),
                    "gender": gender,
                    "birth_date": birth_date.strftime("%Y-%m-%d"),
                    "bank_name": bank_name,
                    "bank_account": bank_account.strip(),
                    "upline_id": confirmed_upline_id if confirmed_upline_id else "",
                    "upline_phone": upline_phone.strip() if upline_phone else "",
                    "upline_name": upline_name.strip() if upline_name else "",
                    "upline_locked": True if confirmed_upline_id else False,
                    "first_purchase_time": "No buy history",
                    "free_gift_claimed": False  # <-- PASTE THIS LINE HERE
                }
                db.collection("users").document(new_member_id).set(user_data)
                st.success(f"Registered! Your Member ID is: **{new_member_id}**")
_id}**")
            except Exception as e:
                st.error(f"Error during registration: {str(e)}")

def render_account_profile_page():
    st.title("My Profile Dashboard")
    user_ref = db.collection("users").document(st.session_state.user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        st.error("Profile records missing.")
        return
        
    user_profile = user_doc.to_dict()
    st.write(f"**Member ID:** {user_profile['member_id']}")
    st.write(f"**Full Name:** {user_profile['full_name']}")
    
    st.markdown("### Order History Baseline")
    purchase_time = user_profile.get("first_purchase_time", "No buy history")
    if purchase_time == "No buy history":
        st.warning("Status: 🛒 No buy history found for this account.")
    else:
        st.success(f"🗓️ **First Purchase Date & Time (Locked):** {purchase_time}")
        
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.is_admin = False
        st.rerun()

def render_checkout_flow():
    st.title("🛒 Product Checkout")
    account_type = st.radio("Select Account Type", ["Consumer (B2C)", "Business Agent (B2B)"])
    qty = st.number_input("Enter Bottle Quantity", min_value=1, value=1, step=1)
    
    if account_type == "Consumer (B2C)":
        pricing = calculate_b2c_price(qty)
    else:
        pricing = calculate_b2b_price(qty)
        
    st.write(f"**Price Per Unit:** RM {pricing['price_per_unit']}")
    st.subheader(f"**Total Amount Due:** RM {pricing['total_price']}")
    
    if st.button("Proceed to FPX Bank Payment"):
        st.warning("🔄 Redirecting securely to local Malaysia Bank Transfer gateway...")
        time.sleep(1.0)
        handle_successful_payment(st.session_state.user_id, qty, pricing['total_price'])
        st.success("✅ Payment Authorized Successfully! Order Record Created.")

def render_admin_dashboard():
    st.title("🛡️ Enterprise Admin Control Center")
    try:
        users_ref = db.collection("users").stream()
        orders_ref = db.collection("orders").stream()
        
        all_users = [u.to_dict() for u in users_ref]
        all_orders = [o.to_dict() for o in orders_ref]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Registered Members", len(all_users))
        col2.metric("Orders Completed", len(all_orders))
        
        total_rev = sum(float(o.get("total_amount", 0)) for o in all_orders if o.get("payment_status") == "Paid")
        col3.metric("Total Revenue", f"RM {total_rev:,.2f}")
        
        st.subheader("👥 Registered Member Directory")
        st.dataframe(all_users, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load admin metrics: {str(e)}")

# =====================================================================
# BOTTOM OF FILE: DYNAMIC NAVIGATION ROUTER BLOCK
# =====================================================================
if not st.session_state.logged_in:
    page_selection = st.sidebar.radio("Navigation", ["Login", "Sign Up Form"])
    if page_selection == "Login":
        render_login_page()
    else:
        render_signup_page()
else:
    menu_options = ["User Dashboard View", "Checkout Store"]
    if st.session_state.get("is_admin", False):
        menu_options.insert(0, "🛡️ Admin Dashboard")
        
    page_selection = st.sidebar.radio("Navigation", menu_options)
    
    if page_selection == "🛡️ Admin Dashboard":
        render_admin_dashboard()
    elif page_selection == "User Dashboard View":
        render_account_profile_page()
    elif page_selection == "Checkout Store":
        render_checkout_flow()

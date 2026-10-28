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

# Session State initialization code
if "user_id" not in st.session_state:
    st.session_state.user_id = "FT-20261028-SAMPLE"  # Tracked member instance


# ==========================================
# 1. FIREBASE INITIALIZATION
# ==========================================
if not firebase_admin._apps:
    # Ensure serviceAccountKey.json is placed in your project root directory
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==========================================
# 2. HELPER FUNCTIONS & LISTS
# ==========================================
MALAYSIA_BANKS = [
    "Maybank (Malayan Banking Berhad)", "CIMB Bank", "Public Bank", "RHB Bank", 
    "Hong Leong Bank", "AmBank", "UOB Malaysia", "Alliance Bank", "Affin Bank", 
    "Bank Islam Malaysia", "Bank Rakyat", "Bank Simpanan Nasional (BSN)", "OCBC Bank Malaysia", 
    "Standard Chartered Malaysia", "HSBC Bank Malaysia", "GXBank", "Boost Bank", "AEON Bank"
]

def generate_member_id() -> str:
    """Generates a professional ID format like FT-20261028-XY7"""
    date_str = time.strftime("%Y%m%d")
    random_suffix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=3))
    return f"FT-{date_str}-{random_suffix}"

def verify_upline(upline_id: str, upline_phone: str) -> tuple[bool, str]:
    """
    Scans Firestore to confirm if the sponsor exists before linking them.
    Returns (True, matching_document_id) or (False, error_message)
    """
    # If both are blank, skip validation (since it is optional)
    if not upline_id and not upline_phone:
        return True, ""
        
    # Check by Upline ID Document Key first
    if upline_id:
        doc_ref = db.collection("users").document(upline_id.strip()).get()
        if doc_ref.exists:
            return True, doc_ref.id
            
    # Check by Phone Number field query if ID was missed or incorrect
    if upline_phone:
        query = db.collection("users").where("phone", "==", upline_phone.strip()).limit(1).stream()
        for doc in query:
            return True, doc.id
            
    return False, "Sponsor not found. Please double-check the Upline ID or Phone Number."

# ==========================================
# 3. INTERFACE PAGES
# ==========================================
def render_signup_page():
    st.title("Create an Account")
    st.markdown("Please fill out the form below to complete registration.")
    
    with st.form("signup_form"):
        email = st.text_input("Email Address *")
        phone = st.text_input("Mobile Phone Number * (e.g. +60123456789)")
        full_name = st.text_input("Full Name (as per MyKad) *")
        gender = st.selectbox("Gender *", options=["", "Male", "Female"])
        
        # Enforce Age Minimum Constraint 
        max_birth_year = date.today().year - 18
        default_birth_date = date(max_birth_year, date.today().month, date.today().day)
        birth_date = st.date_input("Date of Birth *", value=default_birth_date)
        
        # Malaysian Banking Details
        bank_name = st.selectbox("Bank Name *", options=[""] + MALAYSIA_BANKS)
        bank_account = st.text_input("Bank Account Number *")
        
        st.markdown("---")
        st.subheader("Sponsor / Referral Details (Optional)")
        upline_id = st.text_input("Upline ID")
        upline_phone = st.text_input("Upline Phone Number")
        upline_name = st.text_input("Upline Name (Optional)")
        
        submit_button = st.form_submit_button("Register Now")
        
        if submit_button:
            # Step 1: Compulsory Field Validation
            if not email or not phone or not full_name or not bank_account or not gender or not bank_name:
                st.error("Please fill in all fields marked with an asterisk (*).")
                return

            # Step 2: 18+ Age Validation Check
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                st.error("Registration failed: You must be at least 18 years old to join.")
                return
            
            # Step 3: Verify Upline if entered [3]
            is_valid_upline, confirmed_upline_id = verify_upline(upline_id, upline_phone)
            if not is_valid_upline:
                st.error(confirmed_upline_id)
                return

            # Step 4: Write Record Entry to Database
            try:
                new_member_id = generate_member_id()
                
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
                    "upline_locked": True if confirmed_upline_id else False
                }
                
                db.collection("users").document(new_member_id).set(user_data)
                st.success(f"Successfully registered! Your Member ID is: **{new_member_id}**")
                
            except Exception as e:
                st.error(f"An error occurred during account creation: {str(e)}")

def render_account_profile_page(current_user_id: str):
    st.title("My Profile Settings")
    
    user_ref = db.collection("users").document(current_user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        st.error("Profile data could not be retrieved from Firebase.")
        return
        
    user_profile = user_doc.to_dict()
    
    st.subheader("Personal & Banking Particulars")
    st.write(f"**Member ID:** {user_profile['member_id']}")
    st.write(f"**Full Name:** {user_profile['full_name']}")
    st.write(f"**Banking:** {user_profile['bank_name']} — Acc: {user_profile['bank_account']}")
    
    st.markdown("---")
    st.subheader("My Sponsor (Upline)")
    
    # Case A: Upline Linked and Frozen
    if user_profile.get("upline_locked"):
        st.info("🔒 Your network sponsor tier is verified and permanently linked.")
        st.write(f"**Sponsor ID:** {user_profile.get('upline_id', 'N/A')}")
        st.write(f"**Sponsor Name:** {user_profile.get('upline_name', 'N/A')}")
        st.write(f"**Sponsor Phone:** {user_profile.get('upline_phone', 'N/A')}")
    
    # Case B: No Upline Present -> Allow Single Edit Add-on
    else:
        st.warning("⚠️ You currently don't have an upline sponsor linked to your profile.")
        
        with st.form("edit_upline_form"):
            new_up_id = st.text_input("Enter Sponsor Upline ID")
            new_up_phone = st.text_input("Enter Sponsor Upline Phone Number")
            new_up_name = st.text_input("Enter Sponsor Upline Name")
            
            save_upline = st.form_submit_button("Verify & Link Sponsor")
            
            if save_upline:
                if not new_up_id and not new_up_phone:
                    st.error("Please enter an Upline ID or Phone Number to associate a sponsor.")
                    return
                
                # Perform the same lookup verification [3]
                is_valid, confirmed_id = verify_upline(new_up_id, new_up_phone)
                if not is_valid:
                    st.error(confirmed_id)
                    return
                
                updated_network = {
                    "upline_id": confirmed_id,
                    "upline_phone": new_up_phone.strip(),
                    "upline_name": new_up_name.strip(),
                    "upline_locked": True  # Seal the field record
                }
                
                user_ref.update(updated_network)
                st.success("Sponsor profiles successfully verified and linked!")
                time.sleep(1)
                st.rerun()

# ==========================================
# 4. APP NAVIGATION ROUTER
# ==========================================
# Simple setup sidebar router selector for demonstration purposes
# 1. Update the sidebar radio menu options
page_selection = st.sidebar.radio(
    "Navigation", 
    ["Sign Up Form", "Login", "User Dashboard View", "Checkout Store"]
)

# 2. Direct the user to the correct page function based on their selection
if page_selection == "Sign Up Form":
    render_signup_page()

elif page_selection == "Login":
    render_login_page()

elif page_selection == "User Dashboard View":
    # If a user is logged in, pass their session ID. Otherwise, use the fallback.
    active_id = st.session_state.user_id if st.session_state.user_id else "FT-20261028-EXAMPLE"
    render_account_profile_page()

elif page_selection == "Checkout Store":
    # This renders the new bulk pricing calculator and FPX payment simulation
    render_checkout_flow()

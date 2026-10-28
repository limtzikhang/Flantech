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
# GLOBAL SESSION TRACKING ARCHITECTURE
# =====================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# Complete drop-down option dataset for Malaysian Banks
MALAYSIA_BANKS = [
    "Maybank (Malayan Banking Berhad)", 
    "CIMB Bank", 
    "Public Bank", 
    "RHB Bank", 
    "Hong Leong Bank", 
    "AmBank", 
    "UOB Malaysia", 
    "Alliance Bank", 
    "Affin Bank", 
    "Bank Islam Malaysia", 
    "Bank Rakyat", 
    "Bank Simpanan Nasional (BSN)", 
    "OCBC Bank Malaysia", 
    "Standard Chartered Malaysia", 
    "HSBC Bank Malaysia", 
    "GXBank", 
    "Boost Bank", 
    "AEON Bank"
]

# =====================================================================
# SYSTEM UTILITIES
# =====================================================================
def generate_member_id() -> str:
    """Generates a unique professional ID format like FT-20261028-XY7"""
    date_str = time.strftime("%Y%m%d")
    random_suffix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=3))
    return f"FT-{date_str}-{random_suffix}"

def render_login_page():
    st.title("🔐 Sign In")
    st.markdown("Access your Flantech affiliate network portal.")
    
    with st.form("login_form"):
        username = st.text_input("Username (Email or Admin Phone)").strip()
        input_password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login to Account")
        
        if login_btn:
            # Clean and sanitize the input fields
            cleaned_username = username.replace("+", "").replace(" ", "").strip()
            cleaned_password = input_password.strip().lower()  # Force lowercase to match "admin"
            
            # ====================================================================
            # FIXED ADMIN GATEWAY (Bypasses Firebase Completely)
            # ====================================================================
            if cleaned_username == "60164191861" and cleaned_password == "admin":
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.user_id = "ADMIN-USER"
                st.success("Welcome back, Master Admin!")
                time.sleep(0.5)
                st.rerun()
                return  # Force stop here so it never queries Firebase
                
            # ====================================================================
            # REGULAR USER FIREBASE LOOKUP BLOCK
            # ====================================================================
            users_query = db.collection("users").where("email", "==", cleaned_username.lower()).limit(1).stream()
            user_found = None
            for doc in users_query:
                user_found = doc.to_dict()
                
            if user_found and input_password.strip() == "123456":
                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.session_state.user_id = user_found["member_id"]
                st.success("Successfully logged in!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid credentials or user record does not exist.")


def render_signup_page():
    st.title("📝 Create a New Account")
    st.markdown("Mandatory information fields are required for centralized delivery logistics validation.")
    
    with st.form("signup_form"):
        email = st.text_input("Email Address *")
        phone = st.text_input("Mobile Phone Number * (e.g. +60123456789)")
        full_name = st.text_input("Full Name (as per MyKad/IC) *")
        gender = st.selectbox("Gender *", options=["", "Male", "Female"])
        
        # Enforce Age Minimum Constraint (18+ validation threshold layout)
        max_birth_year = date.today().year - 18
        default_birth_date = date(max_birth_year, date.today().month, date.today().day)
        birth_date = st.date_input("Date of Birth *", value=default_birth_date)
        
        # Centralized Banking Settlement Inputs
        bank_name = st.selectbox("Bank Name *", options=[""] + MALAYSIA_BANKS)
        bank_account = st.text_input("Bank Account Number *")
        
        st.markdown("---")
        st.subheader("Sponsor / Referral Details (Optional)")
        upline_id = st.text_input("Upline ID")
        upline_phone = st.text_input("Upline Phone Number")
        upline_name = st.text_input("Upline Name (Optional)")
        submit_button = st.form_submit_button("Complete Registration")
        
        if submit_button:
            # Step 1: Compulsory Parameter Checks
            if not email or not phone or not full_name or not bank_account or not gender or not bank_name:
                st.error("Please fill in all fields marked with an asterisk (*).")
                return

            # Step 2: Strict 18-Year Age Block
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                st.error("Registration denied: You must be at least 18 years old to join.")
                return
            
            # Step 3: Verify Upline Hierarchy Chain Info
            is_valid_upline, confirmed_upline_id = verify_upline(upline_id, upline_phone)
            if not is_valid_upline:
                st.error(confirmed_upline_id)
                return

            # Step 4: Write Record Mapping Matrix to Firestore Registry
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
                    "upline_locked": True if confirmed_upline_id else False,
                    "first_purchase_time": "No buy history",
                    "free_gift_claimed": False  # Initialized eligibility state
                }
                db.collection("users").document(new_member_id).set(user_data)
                st.success(f"Registered! Your Member ID is: **{new_member_id}**")
            except Exception as e:
                st.error(f"Database error during transaction execution: {str(e)}")

def render_account_profile_page():
    st.title("👤 My Account Profile")
    
    user_ref = db.collection("users").document(st.session_state.user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        st.error("Unable to query active session details.")
        return
        
    user_profile = user_doc.to_dict()
    st.write(f"**Member ID:** `{user_profile['member_id']}`")
    st.write(f"**Full Name:** {user_profile['full_name']}")
    st.write(f"**Linked Bank:** {user_profile['bank_name']} ({user_profile['bank_account']})")
    st.markdown("---")
    st.subheader("Hierarchy Management")
    
    # Check if user already has an active sponsor assigned
    if user_profile.get("upline_locked"):
        st.info("🔒 Your network sponsor tier is verified and permanently linked.")
        st.write(f"**Sponsor ID:** {user_profile.get('upline_id', 'Direct')}")
        st.write(f"**Sponsor Name:** {user_profile.get('upline_name', 'N/A')}")
    else:
        st.warning("⚠️ No upline linked. Fill this out before buying 6 bottles to qualify for rewards.")
        with st.form("link_upline_form"):
            up_id = st.text_input("Sponsor Upline ID")
            up_phone = st.text_input("Sponsor Upline Phone")
            up_name = st.text_input("Sponsor Upline Name")
            save_up = st.form_submit_button("Verify & Link Sponsor")
            
            if save_up:
                is_valid, conf_id = verify_upline(up_id, up_phone)
                if is_valid:
                    user_ref.update({
                        "upline_id": conf_id,
                        "upline_phone": up_phone.strip(),
                        "upline_name": up_name.strip(),
                        "upline_locked": True
                    })
                    st.success("Sponsor linked successfully!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(conf_id)

    st.markdown("---")
    st.subheader("📅 Purchase Conversion Tracker")
    purchase_time = user_profile.get("first_purchase_time", "No buy history")
    if purchase_time == "No buy history":
        st.warning("Status: 🛒 No buy history found for this account.")
    else:
        st.success(f"Confirmed First Purchase: **{purchase_time}**")
        
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.is_admin = False
        st.rerun()

def render_checkout_flow():
    st.title("🛒 Product Checkout Store")
    
    upline_sponsor = ""
    sponsor_name = ""
    has_claimed_free_gift = False

    try:
        user_doc = db.collection("users").document(st.session_state.user_id).get()
        if user_doc.exists:
            profile_data = user_doc.to_dict()
            upline_sponsor = profile_data.get("upline_id", "")
            sponsor_name = profile_data.get("upline_name", "Unknown")
            has_claimed_free_gift = profile_data.get("free_gift_claimed", False)
    except Exception:
        pass
    account_type = st.radio("Select Pricing Tier", ["Consumer (B2C Standard)", "Business Agent (B2B Bulk)"])
    qty = st.number_input("Enter Bottle Quantity", min_value=1, max_value=50, value=1, step=1)
    
    if account_type == "Consumer (B2C Standard)":
        pricing = calculate_b2c_price(qty)
    else:
        pricing = calculate_b2b_price(qty)
        
    # PROCESS ONE-TIME REGISTRATION INTRODUCTORY REWARD LOGIC
    is_eligible_for_free_gift = False
    if qty == 6:
        if has_claimed_free_gift:
            st.info("ℹ️ Note: You have already claimed your 1-time introductory free bottle registration gift on a previous order.")
        elif upline_sponsor != "":
            st.success(f"🎁 **First Time Registration Reward:** 1 FREE Bottle will be added under Upline Sponsor **{sponsor_name} ({upline_sponsor})**!")
            is_eligible_for_free_gift = True
        else:
            st.warning("⚠️ **Missed a Free Bottle?** You are ordering 6 bottles, but you haven't linked a sponsor to your profile yet. Link your Upline in your dashboard before paying to claim your introductory free reward!")

    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Price Per Unit", f"RM {pricing['price_per_unit']:.2f}")
    c2.metric("Total Amount Payable", f"RM {pricing['total_price']:,.2f}")
    
    if is_eligible_for_free_gift:
        st.caption("📦 Shipment Manifest: 6 Paid Units + 1 One-Time Registration Reward = **7 Total Bottles to Ship**")
    else:
        st.caption(f"📦 Shipment Manifest: **{qty} Total Bottles to Ship**")

    if st.button("Proceed to FPX Bank Payment"):
        if qty < 50 and account_type == "Business Agent (B2B Bulk)":
            st.error("Payment Denied: Wholesale B2B pricing requires a minimum configuration selection threshold of 50 bottles.")
            return
            
        st.warning("🔄 Connecting securely to local FPX payment clearing gateway...")
        time.sleep(1.0)
        handle_successful_payment(st.session_state.user_id, qty, pricing['total_price'])
        st.success("✅ Payment Authorized! Order parameters broadcasted to central warehousing log.")

def render_admin_dashboard():
    st.title("🛡️ Enterprise Admin Control Center")
    st.markdown("Real-time operational overview of Flantech distribution network and warehouse status.")
    
    try:
        # 1. Fetch real-time data streams from your Firestore Collections
        users_ref = db.collection("users").stream()
        orders_ref = db.collection("orders").stream()
        
        all_users = [u.to_dict() for u in users_ref]
        all_orders = [o.to_dict() for o in orders_ref]
        
        # 2. Calculate Top-Level System Analytics Metrics
        total_members = len(all_users)
        total_orders_processed = len(all_orders)
        
        # Only sum revenue from orders that are marked "Paid" or "Shipped" (excludes cancelled/pending)
        total_revenue = sum(
            float(o.get("total_amount", 0)) 
            for o in all_orders 
            if o.get("payment_status") in ["Paid", "Shipped"]
        )
        
        total_bottles_sold = sum(
            int(o.get("quantity_purchased", 0)) 
            for o in all_orders 
            if o.get("payment_status") in ["Paid", "Shipped"]
        )
        
        # 3. Render Metric Cards Layout Display
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Registered Members", total_members)
        col2.metric("Orders Processed", total_orders_processed)
        col3.metric("Total Revenue", f"RM {total_revenue:,.2f}")
        col4.metric("Total Bottles Sold", f"{total_bottles_sold} units")
        
        # 4. View Master Registered Member Directory
        st.markdown("---")
        st.subheader("👥 Registered Member Directory")
        
        member_list = []
        for u in all_users:
            member_list.append({
                "Member ID": u.get("member_id"),
                "Name": u.get("full_name"),
                "Phone": u.get("phone"),
                "Bank Account": f"{u.get('bank_name')} ({u.get('bank_account')})",
                "Sponsor ID": u.get("upline_id") if u.get("upline_id") else "Direct Signup",
                "1st Purchase Date": u.get("first_purchase_time", "No buy history")
            })
        st.dataframe(member_list, use_container_width=True)
        
        # 5. Interactive Central Packing & Warehouse Delivery Ledger
        st.markdown("---")
        st.subheader("📦 Central Packing & Warehouse Delivery Ledger")
        
        if not all_orders:
            st.info("No orders found in the central ledger system.")
        else:
            for o in all_orders:
                order_id = o.get("order_id")
                current_status = o.get("payment_status", "Paid")
                gift_count = o.get("free_bottles_gift", 0)
                upline = o.get("upline_sponsor_snapshot", "")
                
                # Determine fulfillment action alert status string notes
                note_str = "Standard Delivery"
                if gift_count > 0:
                    note_str = f"🎁 Includes 1-Time Free Gift Sign-Up under Upline Sponsor: {upline}"
                
                # Render interactive individual drop-down expander records
                with st.expander(f"📋 Order ID: {order_id} | Status: {current_status.upper()}"):
                    st.write(f"**Buyer ID:** `{o.get('member_id')}` | **Date/Time:** {o.get('timestamp')}")
                    st.write(f"**Paid Bottles:** {o.get('quantity_purchased')} units | **Gift Bottles:** {gift_count} units")
                    st.write(f"**Total Units to Package & Deliver:** {o.get('total_delivery_units')} bottles")
                    st.write(f"**Total Amount Collected:** RM {float(o.get('total_amount', 0)):.2f}")
                    st.info(f"**Fulfillment Action Note:** {note_str}")
                    
                    # Live Toggle Status Button Action Interface
                    if current_status == "Paid":
                        if st.button(f"Mark Order {order_id} as Shipped", key=f"ship_{order_id}"):
                            db.collection("orders").document(order_id).update({"payment_status": "Shipped"})
                            st.success(f"Order {order_id} updated to Shipped! Refreshing...")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.success("✅ This shipment package has left the facility and is with the courier.")
                        
    except Exception as e:
        st.error(f"Could not load enterprise workspace parameters: {str(e)}")


# =====================================================================
# SYSTEM APPLICATION CONTROLLER / ROUTER
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

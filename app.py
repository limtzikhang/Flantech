import streamlit as st
import pandas as pd
from collections import deque
import streamlit as st
import os
import hashlib

import streamlit as st
import os
import hashlib

# 1. Page Settings & Styling
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
                st.success("Successfully logged in!")
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

# 4. Main Logged-In System Dashboard
else:
    # --- LEFT SIDEBAR PANE MANIPULATION ---
    st.sidebar.title("🧬 Flantech Hub")
    st.sidebar.write(f"👤 Logged in as: **{st.session_state.user_email}**")
    st.sidebar.divider()
    
    # Left Pane Navigation Link Layout Menu Choice
    st.sidebar.markdown("### 🗺️ Navigation Link Options")
    navigation_choice = st.sidebar.radio(
        "Select Page View:",
        ["🏠 Home Dashboard", "📹 Video Library", "📦 product"]
    )
    
    st.sidebar.divider()
    if st.sidebar.button("Log Out of System", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.rerun()
        
    # --- RENDER MAIN INTERFACE SYSTEM BASED ON LEFT PANE LINK SELECTION ---
    
    # IF USER SELECTS HOME
    if navigation_choice == "🏠 Home Dashboard":
        st.title("Welcome to Flantech Asia Platform")
        st.subheader("Overview Dashboard")
        st.write("Welcome back to Flantech Asia. Use the layout links inside the left navigation pane to explore products or watch analysis updates.")
    
    # IF USER SELECTS VIDEO LIBRARY
    elif navigation_choice == "📹 Video Library":
        st.title("Welcome to Flantech Asia Platform")
        st.subheader("Flantech Video & Scientific Archives")
        
        video_target = "Megahydrate Live Blood Analysis.mp4"
        
        if os.path.exists(video_target):
            st.write(f"🎥 Playing: **{video_target}**")
            st.video(video_target)
        else:
            st.error(f"Asset lookup failure: '{video_target}' missing from main repo tree.")
            
        st.divider()
        st.write("Alternative archives inside project container:")
        st.code("• Dr Patrick Flanagan in his Laboratory.mp4\n• Use and Abuse of Live Blood Analysis.mp4")

    # IF USER SELECTS THE NEW 'PRODUCT' NAVIGATION LINK BELOW VIDEO
    elif navigation_choice == "📦 product":
        st.title("🛒 Flantech Authorized E-Commerce Terminal")
        st.subheader("Available Products Catalog")
        st.write("Click on any product image or button below to process transaction billing routes via Maybank2u FPX.")
        st.divider()
        
        # Split screen window into two columns for your products layout
        p_col1, p_col2 = st.columns(2)
        
        # Define paths targeting files inside your repository folder
        img_path_1 = os.path.join("product", "MegaH.jpg")
        img_path_2 = os.path.join("product", "CrystalEnergy.jpg")
        
        with p_col1:
            st.markdown("### 💎 Product 1: MegaHydrate Premium Pack")
            
            # Reads local product image file path check
            if os.path.exists(img_path_1):
                st.image(img_path_1, use_container_width=True)
            else:
                st.error(f"Image not found at path: {img_path_1}. Please verify your file setup.")
                
            st.write("**Description:** High-potency cellular hydration and antioxidant support compound formula.")
            st.write("## Price: RM 240.00")
            
            if st.button("Buy Product 1 via Maybank2u FPX", key="btn_prod_1", use_container_width=True):
                st.warning("Connecting via API gateway to Maybank2u (FPX)...")
                
                # Generated payload structural layouts mapping to future LHDN audit loops
                mock_lhdn_invoice = {
                    "document_type": "Invoice",
                    "buyer_email": st.session_state.user_email,
                    "item_description": "MegaHydrate Premium Pack",
                    "amount_myr": 240.00,
                    "tax_rate": "0%",
                    "currency": "MYR"
                }
                st.info("🔄 Creating verified tax audit tracking record...")
                st.json(mock_lhdn_invoice)
                st.success("Redirecting customer to secure online banking portal...")
                st.markdown("[👉 Click Here to Proceed to Maybank2u FPX Payment Gate](https://maybank2u.com.my)")
                
        with p_col2:
            st.markdown("### 🧪 Product 2: Crystal Energy Concentrate")
            
            if os.path.exists(img_path_2):
                st.image(img_path_2, use_container_width=True)
            else:
                st.error(f"Image not found at path: {img_path_2}. Please verify your file setup.")
                
            st.write("**Description:** Hunza type catalytic elixir liquid concentrate designed to enhance cellular wetness.")
            st.write("## Price: RM 195.00")
            
            if st.button("Buy Product 2 via Maybank2u FPX", key="btn_prod_2", use_container_width=True):
                st.warning("Connecting via API gateway to Maybank2u (FPX)...")
                
                mock_lhdn_invoice_2 = {
                    "document_type": "Invoice",
                    "buyer_email": st.session_state.user_email,
                    "item_description": "Crystal Energy Concentrate",
                    "amount_myr": 195.00,
                    "tax_rate": "0%",
                    "currency": "MYR"
                }
                st.info("🔄 Creating verified tax audit tracking record...")
                st.json(mock_lhdn_invoice_2)
                st.success("Redirecting customer to secure online banking portal...")
                st.markdown("[👉 Click Here to Proceed to Maybank2u FPX Payment Gate](https://maybank2u.com.my)")

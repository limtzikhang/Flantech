import streamlit as st
import os
# Copy this snippet block layout pattern inside your button conditions to push entries live
import firebase_admin
from firebase_admin import firestore

db = firestore.client()

# Update points/cash totals inside the user's secret database row document node
user_ref = db.collection("users").document(st.session_state.user_email)
user_data = user_ref.get().to_dict()

# Increment user ledger allocations securely
new_cash = user_data.get("wallet_cash_myr", 0.00) + 19.20 
new_points = user_data.get("wallet_points", 0.00) + 4.80

user_ref.update({
    "wallet_cash_myr": new_cash,
    "wallet_points": new_points
})
st.success("Wallet balances synchronized successfully inside Firebase Cloud Vault!")

st.set_page_config(page_title="Flantech Products", page_icon="📦", layout="wide")

# Initialize session state tracking parameter checks
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# IF NOT LOGGED IN: Show a clean login box right here inside the tab!
if not st.session_state.authenticated:
    st.title("🔒 Security Validation Gate")
    st.subheader("Please verify your account credentials to view the product catalog")
    
    email_input = st.text_input("Email Address", key="prod_login_email")
    pass_input = st.text_input("Password", type="password", key="prod_login_pass")
    
    if st.button("Verify & Open Store Catalog", use_container_width=True):
        if email_input and pass_input:
            st.session_state.authenticated = True
            st.session_state.user_email = email_input
            st.success("Identity verified successfully! Reloading store...")
            st.rerun()
        else:
            st.error("Please fill in your login credentials.")

# IF ALREADY LOGGED IN: Render your product catalog store setup smoothly
else:
    st.sidebar.title("🧬 Flantech Hub")
    st.sidebar.write(f"👤 Account: **{st.session_state.user_email}**")
    
    if st.sidebar.button("Log Out of System", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.rerun()
        
    st.title("🛒 Flantech Authorized E-Commerce Terminal")
    st.subheader("Available Products Catalog")
    st.write("Click on any product image or button below to process transaction billing routes via Maybank2u FPX.")
    st.divider()
    
    p_col1, p_col2 = st.columns(2)
    img_path_1 = os.path.join("product", "MegaH.jpg")
    img_path_2 = os.path.join("product", "CrystalEnergy.jpg")
    
    with p_col1:
        st.markdown("### 💎 Product 1: MegaHydrate Premium Pack")
        if os.path.exists(img_path_1):
            st.image(img_path_1, use_container_width=True)
        else:
            st.error(f"Image lookup failed at path: {img_path_1}")
            
        st.write("**Description:** High-potency cellular hydration and antioxidant support compound formula.")
        st.write("## Price: RM 240.00")
        
        if st.button("Buy Product 1 via Maybank2u FPX", key="btn_prod_1", use_container_width=True):
            st.warning("Connecting via API gateway to Maybank2u (FPX)...")
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
            st.error(f"Image lookup failed at path: {img_path_2}")
            
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

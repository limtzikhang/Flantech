import streamlit as st
import hashlib
import requests

# 1. Page Configuration
st.set_page_config(page_title="Flantech Asia", page_icon="🛍️", layout="wide")

# 2. Initialize Session State Variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 3. Authentication Interface (Before Login)
if not st.session_state.authenticated:
    st.title("Welcome to Flantech Asia")
    st.subheader("Please sign up or log in to view products")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In", use_container_width=True):
            if email and password:  # Basic check; replace with real database checks later
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Please fill in all fields")
                
    with tab2:
        new_email = st.text_input("Choose Email Address", key="reg_email")
        new_password = st.text_input("Create Password", type="password", key="reg_pass")
        if st.button("Sign Up", use_container_width=True):
            if new_email and new_password:
                st.success("Account created successfully! Please log in above.")
            else:
                st.error("Please fill in all fields")

# 4. Store Interface (After Successful Login)
else:
    # Sidebar navigation & logout
    st.sidebar.title("Navigation")
    st.sidebar.write(f"👤 Account: **{st.session_state.user_email}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.clear_cache()
        st.rerun()

    st.title("🛍️ Flantech Asia Marketplace")
    st.write("Click a product card below to securely process payment via FPX and sync with tax logs.")
    st.divider()

    # Product Catalog Grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Flantech Enterprise Suite")
        # Visual clickable image placeholder
        st.image("https://placehold.co", use_container_width=True)
        st.write("### Price: RM 150.00")
        
        if st.button("Purchase via FPX (Maybank2u)", key="buy_prod_1", use_container_width=True):
            st.info("Initiating FPX checkout engine...")
            
            # Simulated Gateway Action payload mapping to LHDN auditing
            invoice_payload = {
                "buyer_email": st.session_state.user_email,
                "amount": 150.00,
                "item": "Flantech Enterprise Suite"
            }
            
            # This triggers a simulated payment redirect link for user demonstration
            st.success("Mock Redirect: In a live system, this button points to the payment aggregator URL.")
            st.markdown("[👉 Simulate Maybank2u FPX Interface](https://maybank2u.com.my)")

    with col2:
        st.subheader("Flantech Cloud Storage Bundle")
        st.image("https://placehold.co", use_container_width=True)
        st.write("### Price: RM 300.00")
        
        if st.button("Purchase via FPX (Maybank2u)", key="buy_prod_2", use_container_width=True):
            st.info("Initiating FPX checkout engine...")
            st.success("Redirecting...")

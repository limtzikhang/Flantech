import streamlit as st
import os

st.set_page_config(page_title="Flantech Products", page_icon="📦", layout="wide")

# Check if the user is authenticated from the main page gate
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 Access Denied. Please navigate back to the main page and log in first.")
else:
    st.sidebar.title("🧬 Flantech Hub")
    st.sidebar.write(f"👤 Account: **{st.session_state.user_email}**")
    
    st.title("🛒 Flantech Authorized E-Commerce Terminal")
    st.subheader("Available Products Catalog")
    st.write("Click on any product image or button below to process transaction billing routes via Maybank2u FPX.")
    st.divider()
    
    p_col1, p_col2 = st.columns(2)
    
    # Target image structures inside your repository folder
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

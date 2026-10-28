# admin_view.py
import streamlit as st
import time
from database import db

# Paste the complete "def render_admin_dashboard()" block code we created earlier here:
st.title("🛡️ Admin Control Center")

try:
    users_ref = db.collection("users").stream()
    orders_ref = db.collection("orders").stream()
    
    all_users = [u.to_dict() for u in users_ref]
    all_orders = [o.to_dict() for o in orders_ref]
    
    col1, col2 = st.columns(2)
    col1.metric("Registered Members", len(all_users))
    col2.metric("Orders Processed", len(all_orders))
    
    st.subheader("👥 Live Member Database")
    st.dataframe(all_users, use_container_width=True)
except Exception as e:
    st.error(f"Waiting for database metrics initialization streaming connection: {str(e)}")

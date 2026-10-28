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

        # ... (Your existing Admin Dashboard metrics are up here) ...

        st.subheader("👥 Live Member Database")
        st.dataframe(all_users, use_container_width=True)
        
        # =====================================================================
        # PASTE METHOD 2 CODE BLOCK RIGHT HERE:
        # =====================================================================
        st.markdown("---")
        st.subheader("🛠️ Developer Sandbox Clean-up")
        st.caption("Admin utility to easily wipe out mock/testing accounts directly from the front-end dashboard.")
        
        test_id_to_remove = st.text_input("Enter Member ID to permanently delete:", placeholder="e.g. FT-20261029-XYZ")
        
        if st.button("Permanently Remove Account from System", type="primary", key="delete_member_btn"):
            if test_id_to_remove:
                # 1. Clear out their user profile document structure node
                db.collection("users").document(test_id_to_remove.strip()).delete()
                
                # 2. Optional: Scan and automatically clear matching test orders associated with this ID
                test_orders = db.collection("orders").where("member_id", "==", test_id_to_remove.strip()).stream()
                for order_doc in test_orders:
                    db.collection("orders").document(order_doc.id).delete()
                    
                st.success(f"💥 Account `{test_id_to_remove}` and its simulated invoices have been permanently wiped!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Please provide a valid Member ID reference token first.")
        # =====================================================================
        
        st.markdown("---")
        st.subheader("📦 Central Packing & Warehouse Delivery Ledger")
        # ... (Your packing expander boxes code continues down here) ...

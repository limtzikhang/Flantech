# admin_view.py
import streamlit as st
import time
from database import db

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
    
    # Only sum revenue from orders that are marked "Paid" or "Shipped"
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
    
    # =====================================================================
    # DEVELOPER SANDBOX CLEAN-UP UTILITY
    # =====================================================================
    st.markdown("---")
    st.subheader("🛠️ Developer Sandbox Clean-up")
    st.caption("Admin utility to easily wipe out mock/testing accounts directly from the front-end dashboard.")
    
    test_id_to_remove = st.text_input("Enter Member ID to permanently delete:", placeholder="e.g. FT-20261029-XYZ")
    
    if st.button("Permanently Remove Account from System", type="primary", key="delete_member_btn"):
        if test_id_to_remove:
            # 1. Clear out their user profile document structure node
            db.collection("users").document(test_id_to_remove.strip()).delete()
            
            # 2. Automatically clear matching test orders associated with this ID
            test_orders = db.collection("orders").where("member_id", "==", test_id_to_remove.strip()).stream()
            for order_doc in test_orders:
                db.collection("orders").document(order_doc.id).delete()
                
            st.success(f"💥 Account `{test_id_to_remove}` and its simulated invoices have been permanently wiped!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Please provide a valid Member ID reference token first.")
    
    # =====================================================================
    # 5. Interactive Central Packing & Warehouse Delivery Ledger
    # =====================================================================
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
                st.write(f"**Total Units to Deliver:** {o.get('total_delivery_units')} bottles")
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

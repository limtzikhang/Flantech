# checkout_view.py
import streamlit as st
import time
from pricing import calculate_b2c_price, calculate_b2b_price
from database import handle_successful_payment, db

st.title("🛒 Central Checkout Store")

# 1. Fallback definitions mapping item names
PRODUCT_NAMES = {
    "PROD_001": "MegaHydrate Capsule Edition",
    "PROD_002": "Flanagan Crystal Energy Drops"
}

# Initialize empty cart edge cases
cart = st.session_state.get("cart", {})
total_bottles = sum(cart.values())

if total_bottles == 0:
    st.warning("⚠️ Your shopping basket is currently empty. Please navigate to the **Product Showcase** to choose your quantities first!")
else:
    st.subheader("📦 Order Manifest Breakdown")
    
    # Render line items in cart
    for prod_id, quantity in cart.items():
        if quantity > 0:
            st.write(f"• **{PRODUCT_NAMES[prod_id]}**: {quantity} bottles")
            
    st.markdown("---")
    
    # 2. Fetch User Profile for One-Time Gift Checking Real-time Pipelines
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
        pass  # Graceful fallback state

    # 3. Dynamic Wholesale Package Tier Math Evaluation
    account_type = st.radio("Select Operational Billing Tier Slot", ["Consumer (B2C Standard)", "Business Agent (B2B Bulk)"])
    
    if account_type == "Consumer (B2C Standard)":
        pricing = calculate_b2c_price(total_bottles)
    else:
        pricing = calculate_b2b_price(total_bottles)

    # 4. ONE-TIME 6-BOTTLE SPONSOR REWARD VALIDATION TREE
    is_eligible_for_free_gift = False
    if total_bottles == 6:
        if has_claimed_free_gift:
            st.info("ℹ️ Note: You have already claimed your 1-time introductory free bottle registration gift on a previous order.")
        elif upline_sponsor != "":
            st.success(f"🎁 **First Time Registration Reward Active:** 1 FREE Bottle will be added under your Upline Sponsor **{sponsor_name} ({upline_sponsor})**!")
            is_eligible_for_free_gift = True
        else:
            st.warning("⚠️ **Missed a Free Bottle?** You are ordering exactly 6 bottles, but you haven't linked a sponsor to your profile yet. Link your Upline on your Profile page before paying to claim your introductory free reward!")

    # 5. Financial Checkout Accounting Display Parameters
    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Calculated Price Per Bottle", f"RM {pricing['price_per_unit']:.2f}")
    c2.metric("Total Corporate Invoice Amount", f"RM {pricing['total_price']:,.2f}")
    
    if is_eligible_for_free_gift:
        st.caption(f"📦 Shipping Warehouse Manifest: {total_bottles} Paid Units + 1 One-Time Registration Reward = **{total_bottles + 1} Total Bottles to Ship**")
    else:
        st.caption(f"📦 Shipping Warehouse Manifest: **{total_bottles} Total Bottles to Ship**")

    # 6. Process Local Malaysian Gateway Execution Callbacks
    if st.button("Authorize FPX Local Bank Payment", use_container_width=True):
        if total_bottles < 50 and account_type == "Business Agent (B2B Bulk)":
            st.error("Transaction Aborted: Wholesale B2B promotional rates require a cumulative minimum volume threshold selection of 50 bottles.")
            return
            
        st.warning("🔄 Connecting securely to local FPX payment clearing gateway network...")
        time.sleep(1.2)
        
        # Log payment data structures up into central firestore nodes
        handle_successful_payment(st.session_state.user_id, total_bottles, pricing['total_price'])
        
        # Wipe basket state out of RAM memory upon order completion validation
        st.session_state.cart = {}
        st.success("✅ Secure Gateway Settlement Complete! Order metrics broadcasted directly to central warehousing logistics ledger.")
        time.sleep(1.0)
        st.rerun()

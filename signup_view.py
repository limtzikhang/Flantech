# signup_view.py
import streamlit as st
from datetime import date
import time
import random
from database import verify_upline, db

st.title("📝 Create an Account")
st.markdown("Please fill out the form below to complete registration.")   

MALAYSIA_BANKS = [
    "Maybank (Malayan Banking Berhad)", "CIMB Bank", "Public Bank", "RHB Bank", 
    "Hong Leong Bank", "AmBank", "UOB Malaysia", "Alliance Bank", "Affin Bank", 
    "Bank Islam Malaysia", "Bank Rakyat", "Bank Simpanan Nasional (BSN)", "OCBC Bank Malaysia", 
    "Standard Chartered Malaysia", "HSBC Bank Malaysia", "GXBank", "Boost Bank", "AEON Bank"
]

def generate_member_id() -> str:
    """Generates a professional ID format like FT-20261029-XY7"""
    date_str = time.strftime("%Y%m%d")
    random_suffix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=3))
    return f"FT-{date_str}-{random_suffix}"

with st.form("signup_form"):
    email = st.text_input("Email Address *")
    phone = st.text_input("Mobile Phone Number * (e.g. 60123456789)")
    full_name = st.text_input("Full Name (as per IC) *")
    
    # 1. Compulsory Gender Dropdown
    gender = st.selectbox("Gender *", options=["", "Male", "Female"])
    
    # 2. Compulsory Age Configuration (Minimum 18 years old validation logic)
    max_birth_year = date.today().year - 18
    default_birth_date = date(max_birth_year, date.today().month, date.today().day)
    birth_date = st.date_input("Date of Birth *", value=default_birth_date)
    
    # 3. Compulsory Malaysian Bank Profile setup
    bank_name = st.selectbox("Bank Name *", options=[""] + MALAYSIA_BANKS)
    bank_account = st.text_input("Bank Account Number *")
    
    st.markdown("---")
    st.subheader("Sponsor / Referral Details (Optional)")
    st.info("💡 **Tip:** Fill in **any one (1) option below** to link your sponsor and qualify for your one-time 6-bottle registration free gift reward!")
    
    # 4. Optional Upline Fields
    upline_id = st.text_input("Upline ID (Fill any 1 option)")
    upline_phone = st.text_input("Upline Phone Number (Fill any 1 option)")
    upline_name = st.text_input("Upline Name (Optional reference)")
    
    submit_button = st.form_submit_button("Register Now")
    
    if submit_button:
        # Enforce Mandatory Fields
        if not email or not phone or not full_name or not bank_account or not gender or not bank_name:
            st.error("Please fill in all fields marked with an asterisk (*).")
            st.stop()

        # Enforce 18+ Rule
        today = date.today()
        calculated_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if calculated_age < 18:
            st.error("Registration failed: You must be at least 18 years old to join.")
            st.stop()
            
        # Verify Upline if any info is provided
        is_valid_upline, confirmed_upline_id = verify_upline(upline_id, upline_phone)
        if not is_valid_upline:
            st.error(confirmed_upline_id)
            st.stop()
            
        # Process Signup and Generate Profile in Firebase Firestore
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
                # Optional components (Saved empty if skipped)
                "upline_id": confirmed_upline_id if confirmed_upline_id else "",
                "upline_phone": upline_phone.strip() if upline_phone else "",
                "upline_name": upline_name.strip() if upline_name else "",
                "upline_locked": True if confirmed_upline_id else False,
                "first_purchase_time": "No buy history",
                "free_gift_claimed": False
            }
            
            # Write to Firestore using member_id as the primary document key
            db.collection("users").document(new_member_id).set(user_data)
            st.success(f"Successfully registered! Your Member ID is: **{new_member_id}**")
            
        except Exception as e:
            st.error(f"An error occurred during account creation: {str(e)}")

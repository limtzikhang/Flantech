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

with st.form("signup_form", clear_on_submit=False):
    email = st.text_input("Email Address *", placeholder="e.g. test@gmail.com")
    phone = st.text_input("Mobile Phone Number * (e.g. 60123456789)")
    full_name = st.text_input("Full Name (as per IC) *")
    
    password = st.text_input("Create Account Password *", type="password", placeholder="Minimum 6 characters recommended")
    gender = st.selectbox("Gender *", options=["", "Male", "Female"])
    
    # 18+ Age Constraint Selection Strategy
    min_birth_date = date(1940, 1, 1)
    max_birth_date = date.today()
    default_view_date = date(2000, 1, 1)
    
    birth_date = st.date_input(
        "Date of Birth *", 
        value=default_view_date,
        min_value=min_birth_date,
        max_value=max_birth_date
    )
    
    bank_name = st.selectbox("Bank Name *", options=[""] + MALAYSIA_BANKS)
    bank_account = st.text_input("Bank Account Number *")
    
    st.markdown("---")
    st.subheader("Sponsor / Referral Details (Optional)")
    st.info("💡 **Tip:** Fill in **any one (1) option below** to link your sponsor and qualify for your one-time 6-bottle registration free gift reward!")
    
    upline_id = st.text_input("Upline ID (Fill any 1 option)")
    upline_phone = st.text_input("Upline Phone Number (Fill any 1 option)")
    upline_name = st.text_input("Upline Name")
    
    submit_button = st.form_submit_button("Register Now", use_container_width=True)
    
    if submit_button:
        # Step 1: Compulsory Field Validation Check
        if not email or not phone or not full_name or not password or not bank_account or not gender or not bank_name:
            st.error("❌ Registration Blocked: Please fill in all fields marked with an asterisk (*).")
            
        else:
            # Step 2: Enforce 18+ Age Verification Rule
            today = date.today()
            calculated_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if calculated_age < 18:
                st.error("❌ Registration failed: You must be at least 18 years old to join.")
            else:
                # =====================================================================
                # NEW ANTI-DUPLICATE SCANNING PIPELINE
                # =====================================================================
                target_email = email.strip().lower()
                target_phone = phone.strip().replace(" ", "").replace("+", "")
                
                email_exists = False
                phone_exists = False
                
                try:
                    # Scan database collection stream for active duplicates
                    all_users = db.collection("users").stream()
                    for user_doc in all_users:
                        u_data = user_doc.to_dict()
                        if u_data.get("email") == target_email:
                            email_exists = True
                        if u_data.get("phone") == target_phone:
                            phone_exists = True
                except Exception:
                    pass # Fall through if database is initially empty
                
                if email_exists:
                    st.error("❌ Registration Rejected: This Email Address is already registered to another account.")
                elif phone_exists:
                    st.error("❌ Registration Rejected: This Mobile Phone Number is already registered to another account.")
                else:
                    # Step 3: Verify Upline Hierarchy Chain Info
                    is_valid_upline, confirmed_upline_id = verify_upline(upline_id, upline_phone)
                    
                    if not is_valid_upline:
                        st.error(f"❌ {confirmed_upline_id}")
                    else:
                        # Step 4: Write Record Mapping Parameters to Firestore Database
                        try:
                            new_member_id = generate_member_id()
                            
                            user_data = {
                                "member_id": new_member_id,
                                "email": target_email,
                                "phone": target_phone,
                                "full_name": full_name.strip(),
                                "password": password.strip(),
                                "gender": gender,
                                "birth_date": birth_date.strftime("%Y-%m-%d"),
                                "bank_name": bank_name,
                                "bank_account": bank_account.strip(),
                                "upline_id": confirmed_upline_id if confirmed_upline_id else "",
                                "upline_phone": upline_phone.strip() if upline_phone else "",
                                "upline_name": upline_name.strip() if upline_name else "",
                                "upline_locked": True if confirmed_upline_id else False,
                                "first_purchase_time": "No buy history",
                                "free_gift_claimed": False
                            }
                            
                            db.collection("users").document(new_member_id).set(user_data)
                            st.success(f"🎉 **Registration Successful!** Your unique Member ID is: **{new_member_id}**")
                            st.balloons()
                            
                            st.info("🔄 Redirecting to the Login screen...")
                            time.sleep(2.0)
                            st.switch_page("home_view.py")
                            
                        except Exception as e:
                            st.error(f"❌ Database Transaction Failure: {str(e)}")

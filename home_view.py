# home_view.py
import streamlit as st
import time
from database import db

# Initialize Bank list dropdown selection
MALAYSIA_BANKS = [
    "Maybank (Malayan Banking Berhad)", "CIMB Bank", "Public Bank", "RHB Bank", 
    "Hong Leong Bank", "AmBank", "UOB Malaysia", "Alliance Bank", "Affin Bank", 
    "Bank Islam Malaysia", "Bank Rakyat", "Bank Simpanan Nasional (BSN)", "OCBC Bank Malaysia", 
    "Standard Chartered Malaysia", "HSBC Bank Malaysia", "GXBank", "Boost Bank", "AEON Bank"
]

def render_login_view():
    st.title("🔐 Sign In")
    st.markdown("Access your Mega H Global distribution portal.")

    username = st.text_input("Username (Email or Phone Number)").strip()
    input_password = st.text_input("Password", type="password")
    
    if st.button("Login to Account", use_container_width=True):
        # Clean inputs: eliminate structural spaces, symbols, and force lowercasing
        cleaned_username = username.replace("+", "").replace(" ", "").strip().lower()
        cleaned_password = input_password.strip().lower()
        
        if not cleaned_username or not cleaned_password:
            st.error("Please fill in your login credentials.")
            return

        # ====================================================================
        # 1. FIXED ADMIN GATEWAY (Bypasses Firestore query entirely)
        # ====================================================================
        is_admin_phone = (cleaned_username == "60164191861" and cleaned_password == "admin")
        is_admin_email = (cleaned_username == "limtzikhang@gmail.com" and cleaned_password == "admin")
        
        if is_admin_phone or is_admin_email:
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.user_id = "ADMIN-USER"
            st.success("Welcome back, Master Admin!")
            time.sleep(0.5)
            st.rerun()
            return

        # ====================================================================
        # 2. DYNAMIC CUSTOMER LOGIN (Allows Email or Phone lookup streams)
        # ====================================================================
        else:
            try:
                user_found = None
                
                # Check A: Try routing as an Email address token match
                if "@" in cleaned_username:
                    db.where("email", "==", cleaned_username)
                    users_query = db.execute_query()
                    for doc in users_query:
                        user_found = doc.to_dict()
                
                # Check B: Fallback string matching via Phone Number
                if not user_found:
                    db.where("phone", "==", cleaned_username)
                    users_query = db.execute_query()
                    for doc in users_query:
                        user_found = doc.to_dict()

                # =====================================================================
                # VERIFY LOGINS USING CUSTOM SAVED PASSWORDS DYNAMICALLY
                # =====================================================================
                if user_found:
                    # Fetch the user's custom saved password string from Firestore
                    saved_password = user_found.get("password", "")
                    
                    # Match inputs exactly against the user's recorded database credential passport
                    if cleaned_password == saved_password:
                        st.session_state.logged_in = True
                        st.session_state.is_admin = False
                        st.session_state.user_id = user_found["member_id"]
                        st.success("Successfully logged in!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials provided. Check your email/phone number or password.")
                else:
                    st.error("Invalid credentials provided. Account record not found in system.")
            except Exception as e:
                st.error(f"System Network Error: {str(e)}")



def render_profile_view():
    st.title("👤 My Profile Dashboard")
    
    # Secure handling if an admin account clicks this dashboard profile row view
    if st.session_state.get("is_admin", False):
        st.info("System Privileges: Master Administrator Account Active.")
        st.write(f"**Admin Instance User ID:** `{st.session_state.user_id}`")
    else:
        # Standard customer profile pipeline pulling records from firestore
        try:
            user_ref = db.collection("users").document(st.session_state.user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                profile = user_doc.to_dict()
                
                st.subheader("Personal & Banking Particulars")
                st.write(f"**Member ID:** `{profile['member_id']}`")
                st.write(f"**Full Name:** {profile['full_name']}")
                st.write(f"**Email:** {profile['email']}")
                st.write(f"**Phone:** {profile['phone']}")
                st.write(f"**Banking Account:** {profile['bank_name']} — `{profile['bank_account']}`")
                
                st.markdown("---")
                st.subheader("Hierarchy Management")
                if profile.get("upline_locked"):
                    st.info("🔒 Your network sponsor tier is verified and permanently linked.")
                    st.write(f"**Sponsor ID:** {profile.get('upline_id', 'Direct Entry')}")
                    st.write(f"**Sponsor Name:** {profile.get('upline_name', 'N/A')}")
                else:
                    st.warning("⚠️ No upline linked. Link a sponsor before buying 6 bottles to qualify for your free reward.")
                    with st.form("link_upline_form"):
                        st.info("💡 **Instructions:** To claim your 1-time reward, you only need to fill in **either** the Upline ID **OR** the Upline Phone Number below.")
                        up_id = st.text_input("Sponsor Upline ID")
                        up_phone = st.text_input("Sponsor Upline Phone")
                        up_name = st.text_input("Sponsor Upline Name (Optional)")
                        save_up = st.form_submit_button("Verify & Link Sponsor")

                        if save_up:
                            from database import verify_upline
                            is_valid, conf_id = verify_upline(up_id, up_phone)
                            if is_valid:
                                user_ref.update({
                                    "upline_id": conf_id,
                                    "upline_phone": up_phone.strip(),
                                    "upline_name": up_name.strip(),
                                    "upline_locked": True
                                })
                                st.success("Sponsor linked successfully!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(conf_id)

                st.markdown("---")
                st.subheader("📅 Purchase Conversion Tracker")
                buy_status = profile.get("first_purchase_time", "No buy history")
                if buy_status == "No buy history":
                    st.warning("Status: 🛒 No buy history found on account.")
                else:
                    st.success(f"🗓️ **First Successful Purchase Date & Time:** {buy_status}")
            else:
                st.error("Profile parameters could not be found.")
        except Exception as e:
            st.error(f"Error connecting to directory: {str(e)}")
            
    st.markdown("---")
    if st.button("Log Out of Session", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.user_id = None
        st.success("Session logged out.")
        time.sleep(0.5)
        st.rerun()

# =====================================================================
# INTERFACE RUNTIME SELECTOR
# =====================================================================
if not st.session_state.get("logged_in", False):
    render_login_view()
else:
    render_profile_view()

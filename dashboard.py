import streamlit as st
import pandas as pd
import requests

# =====================================================================
# API CONNECTION LAYER
# =====================================================================
# Replace this string with your live active ngrok address from Step 1
API_URL = "https://ngrok-free.app" 

if "auth_session" not in st.session_state: st.session_state["auth_session"] = None

st.title("🏆 Flantech Asia 3MP Matrix Portal")
st.caption("Distributed Cloud Front-End Connected Securely to Local API Vault")
st.write("---")

if st.session_state["auth_session"] is None:
    tab_login, tab_register = st.tabs(["🔑 Member Sign In", "📝 Create New Account"])
    
    with tab_login:
        st.subheader("Login to Dashboard")
        phone_in = st.text_input("Mobile Phone Number ID", key="login_phone")
        pass_in = st.text_input("Secure Access Password", type="password", key="login_pass")
        
        if st.button("Access Portal Panel", use_container_width=True):
            try:
                res = requests.post(f"{API_URL}/login", json={"phone": phone_in, "password": pass_in})
                if res.status_code == 200:
                    st.session_state["auth_session"] = phone_in
                    st.success("Authentication verified successfully!")
                    st.rerun()
                else: st.error("Invalid mobile phone identifier credentials or password parameters.")
            except Exception: st.error("Database Connection Offline: Ensure local home bridge server is running.")
                
    with tab_register:
        st.subheader("Enroll as a Flantech 3MP Matrix转 Distributor")
        reg_name = st.text_input("Full Registered Name")
        reg_phone = st.text_input("Mobile Phone Number Configuration ID")
        reg_pass = st.text_input("Create Account Password", type="password")
        reg_ref = st.text_input("Sponsor / Recruiter Phone Number Reference")
        pkg_cv = st.slider("Package Commission Value (CV Points)", min_value=0, max_value=1500, value=500, step=50)
        
        if st.button("Complete Enrollment Verification", use_container_width=True):
            if not reg_name or not reg_phone or not reg_pass or not reg_ref:
                st.warning("All entry rows require values.")
            else:
                try:
                    payload = {"name": reg_name, "phone": reg_phone, "password": reg_pass, "sponsor": reg_ref, "pkg_cv": pkg_cv}
                    res = requests.post(f"{API_URL}/register", json=payload)
                    if res.status_code == 200: st.success("Enrollment successful! Proceed to the Sign In panel.")
                    else: st.error(res.json().get("detail", "Registration rejected by local database."))
                except Exception: st.error("Database Connection Offline: Ensure local home bridge server is running.")

else:
    current_phone = st.session_state["auth_session"]
    try:
        members = requests.get(f"{API_URL}/members").json()
        user = members[current_phone]
    except Exception:
        st.error("Lost communication links with database vault server.")
        st.stop()
        
    st.sidebar.markdown(f"### 👤 Active Account Details")
    st.sidebar.write(f"**Name:** {user['name']}")
    st.sidebar.write(f"**Distributor Rank:** {user['rank']}")
    st.sidebar.write(f"**Placement Upline Parent:** {members[user['upline']]['name'] if user['upline'] else 'None (Root Node)'}")
    
    if st.sidebar.button("Log Out of Session Link", use_container_width=True):
        st.session_state["auth_session"] = None
        st.rerun()
        
    m_col1, m_col2 = st.columns(2)
    with m_col1: st.metric("Total Account Payout Wallet Balance", f"${user['wallet']:,.2f}")
    with m_col2: st.metric("Matrix Group Volume (GSV Accumulation)", f"{user['team_sales_cv']:,.0f} CV")
        
    st.write("---")
    tab_sales, tab_tree, tab_debug = st.tabs(["📊 Submit New Group Sales Order", "👥 Your Matrix Downline Row (Max 3 Width)", "🔍 Master Genealogy Database"])
    
    with tab_sales:
        st.subheader("Process Team Order Commission Log")
        sale_cv = st.number_input("Enter Product Commission Value (CV)", min_value=0, max_value=5000, value=300, step=50)
        if st.button("Submit Sale Ledger Entry", use_container_width=True):
            if sale_cv > 0:
                try:
                    res = requests.post(f"{API_URL}/sale", json={"buyer_phone": current_phone, "cv_amount": sale_cv})
                    if res.status_code == 200: st.success("Sale order processed safely!")
                    st.rerun()
                except Exception: st.error("Database connection dropped.")
                
    with tab_tree:
        st.subheader("Direct Generation Matrix Slots (Level 1)")
        matrix_data = []
        for i, child_phone in enumerate(user["children"]):
            if child_phone in members:
                child = members[child_phone]
                matrix_data.append({
                    "Matrix Leg Position": f"Leg Row Position {i+1}", "Name Member": child["name"],
                    "Phone ID Link": child_phone, "Assigned Rank": child["rank"],
                    "Introduced By (Sponsor)": members[child["sponsor"]]["name"]
                })
        if matrix_data: st.dataframe(pd.DataFrame(matrix_data), hide_index=True, use_container_width=True)
        else: st.info("Your downline matrix positions are completely empty right now.")
            
    with tab_debug:
        st.subheader("Genealogy Visibility Grid Log (No Passwords Shared)")
        global_log = []
        for phone, info in members.items():
            global_log.append({
                "Member Phone Key": phone, "Entity Name": info["name"],
                "Sponsor Recruiter Link": info["sponsor"] if info["sponsor"] else "None",
                "Matrix Parent Upline Assigned": info["upline"] if info["upline"] else "ROOT ENGINE ADM",
                "Occupied Limbs Width": f"{len(info['children'])} / 3 Slots occupied",
                "Accrued Earnings Wallet": f"${info['wallet']:,.2f}",
                "Rolling Team Sales Volume": f"{info['team_sales_cv']} CV total value"
            })
        st.dataframe(pd.DataFrame(global_log), hide_index=True, use_container_width=True)

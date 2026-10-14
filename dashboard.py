import streamlit as st
import pandas as pd
from collections import deque

# =====================================================================
# SYSTEM PERSISTENT STORAGE LAYER
# =====================================================================
# Memory matrix structure maps nodes dynamically to persist across interface tabs
if "members_db" not in st.session_state:
    st.session_state["members_db"] = {
        "60164191861": {
            "name": "Admin Leader",
            "password": "admin",
            "sponsor": None,       # Direct recruiter indicator
            "upline": None,        # Dynamic 3MP matrix position placement node
            "children": [],        # Matrix limbs constraint list (Bounded maximum = 3)
            "rank": "Diamond",
            "wallet": 0.0,
            "team_sales_cv": 0.0
        }
    }

if "auth_session" not in st.session_state:
    st.session_state["auth_session"] = None

# Flantech Corporate Direct Sales Volume Bonus levels configuration
RANK_BONUS_RATES = {"Bronze": 0.25, "Silver": 0.30, "Gold": 0.35, "Diamond": 0.40}

# =====================================================================
# 3MP MATRIX SEARCH & PLACEMENT LOGIC ENGINE
# =====================================================================
def find_3mp_placement_slot(sponsor_phone):
    """
    Executes a high-efficiency Breadth-First Search (BFS) tracking down 
    the genealogy layout maps starting from the recruiter node downwards.
    Finds the first available vacant tree slot where children array < 3.
    """
    db = st.session_state["members_db"]
    queue = deque([sponsor_phone])
    
    while queue:
        current_node = queue.popleft()
        # If this leg index layout has vacant slots, position matches rules
        if len(db[current_node]["children"]) < 3:
            return current_node
        
        # Otherwise, push level components to evaluate deeper network slots
        queue.extend(db[current_node]["children"])
        
    return "60123456789"  # Ultimate fallback array index mapping path

def determine_rank_by_cv(cv_amount):
    """Maps purchase configuration values to internal Flantech Rank requirements."""
    if cv_amount >= 1000: return "Diamond"
    elif cv_amount >= 500: return "Gold"
    elif cv_amount >= 300: return "Silver"
    elif cv_amount >= 100: return "Bronze"
    return "Member"

def process_flantech_sale(buyer_phone, cv_amount):
    """
    Calculates direct sales commissions based on recruiter rank parameters.
    Simultaneously scales group volume updates upwards through the physical 3MP upline vector.
    """
    db = st.session_state["members_db"]
    sponsor_phone = db[buyer_phone]["sponsor"]
    
    if not sponsor_phone or sponsor_phone not in db:
        return None  
    
    sponsor = db[sponsor_phone]
    sponsor_rate = RANK_BONUS_RATES.get(sponsor["rank"], 0.25)
    commission_earned = round(cv_amount * sponsor_rate, 2)
    
    # Apply calculations instantly into target sponsor wallet arrays
    db[sponsor_phone]["wallet"] += commission_earned
    
    # Vertically scale the sales volume metrics through parent nodes step-by-step
    current_upline = db[buyer_phone]["upline"]
    while current_upline:
        if current_upline in db:
            db[current_upline]["team_sales_cv"] += cv_amount
            current_upline = db[current_upline]["upline"]  # Traverse structurally upward
        else:
            break
            
    return {
        "Sponsor Name": sponsor["name"],
        "Sponsor Current Rank": sponsor["rank"],
        "Bonus Percentage Applied": f"{int(sponsor_rate * 100)}%",
        "Payout Commission Credited ($)": commission_earned
    }

# =====================================================================
# DASHBOARD INTERFACE LAYOUT RENDER PORTAL
# =====================================================================
st.title("🏆 Flantech Asia 3MP Matrix Portal")
st.caption("Automated 3-Member Placement Genealogy and Commissions Engine")
st.write("---")

# Conditional workflow switching paths mapping dashboard screens based on session values
if st.session_state["auth_session"] is None:
    tab_login, tab_register = st.tabs(["🔑 Member Sign In", "📝 Create New Account"])
    
    # ------------------ MEMBER SIGN IN CONTROL ------------------
    with tab_login:
        st.subheader("Login to Dashboard")
        phone_in = st.text_input("Mobile Phone Number ID (Unique Key)", key="login_phone")
        pass_in = st.text_input("Secure Access Password", type="password", key="login_pass")
        
        if st.button("Access Portal Panel", use_container_width=True):
            db = st.session_state["members_db"]
            if phone_in in db and db[phone_in]["password"] == pass_in:
                st.session_state["auth_session"] = phone_in
                st.success(f"Authentication verified successfully! Welcome, {db[phone_in]['name']}.")
                st.rerun()
            else:
                st.error("Invalid mobile authentication credentials or password parameters.")
                
    # ------------------ EXTENDED TREE REGISTRATION ------------------
    with tab_register:
        st.subheader("Enroll as a Flantech 3MP Matrix Distributor")
        reg_name = st.text_input("Full Registered Name")
        reg_phone = st.text_input("Mobile Phone Number Configuration ID")
        reg_pass = st.text_input("Create Account Password", type="password")
        reg_ref = st.text_input("Sponsor / Recruiter Phone Number Reference")
        
        st.markdown("##### Matrix Activation Order Configuration Setup")
        pkg_cv = st.slider("Package Commission Value (CV Points)", min_value=0, max_value=1500, value=500, step=50)
        calculated_rank = determine_rank_by_cv(pkg_cv)
        st.info(f"Introductory purchase structure maps account tier to: **{calculated_rank}** Rank.")
        if st.button("Complete Enrollment Verification", use_container_width=True):
            db = st.session_state["members_db"]
            if not reg_name or not reg_phone or not reg_pass or not reg_ref:
                st.warning("All data fields are mandatory. A direct recruiter sponsor phone string is required for 3MP matrix calculations.")
            elif reg_phone in db:
                st.error("This mobile parameter code matches an active account nodes mapping row.")
            elif reg_ref not in db:
                st.error("The specified sponsor phone target node does not match any active network profile configuration paths.")
            else:
                # 1. SEARCH FOR THE NEXT OPEN VERTICAL PLACEMENT NODE USING 3MP ALGORITHM
                assigned_upline = find_3mp_placement_slot(reg_ref)
                
                # 2. COMMITTED SAVE NEW TREE RECORD LAYER INTO RUNTIME DICTIONARY
                db[reg_phone] = {
                    "name": reg_name,
                    "password": reg_pass,
                    "sponsor": reg_ref,
                    "upline": assigned_upline,
                    "children": [],
                    "rank": calculated_rank,
                    "wallet": 0.0,
                    "team_sales_cv": 0.0
                }
                
                # 3. Synchronize references to map physical limbs links bounds securely
                db[assigned_upline]["children"].append(reg_phone)
                
                # 4. Trigger commission payout distribution splits 
                process_flantech_sale(reg_phone, pkg_cv)
                
                st.success(f"Enrollment successful! Position automatically assigned under Upline Node: {db[assigned_upline]['name']} ({assigned_upline}) matching strict 3MP spillover rules.")

else:
    # ------------------ DISTRIBUTOR DASHBOARD VIEWS PORT ------------------
    current_phone = st.session_state["auth_session"]
    user = st.session_state["members_db"][current_phone]
    db = st.session_state["members_db"]
    
    # Sidebar Profile Card View Dashboard Elements
    st.sidebar.markdown(f"### 👤 Active Account Details")
    st.sidebar.write(f"**Name:** {user['name']}")
    st.sidebar.write(f"**Distributor Rank:** {user['rank']}")
    st.sidebar.write(f"**Placement Upline Parent:** {db[user['upline']]['name'] if user['upline'] else 'None (Root Matrix Head)'}")
    
    if st.sidebar.button("Log Out of Session Link", use_container_width=True):
        st.session_state["auth_session"] = None
        st.rerun()
        
    # Graphical Grid Displays Cards
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Total Account Payout Wallet Balance", f"${user['wallet']:,.2f}")
    with m_col2:
        st.metric("Matrix Group Volume (GSV Accumulation)", f"{user['team_sales_cv']:,.0f} CV")
        
    st.write("---")
    
    # Feature Modules Tab Navigation
    tab_sales, tab_tree, tab_debug = st.tabs(["📊 Submit New Group Sales Order", "👥 Your Matrix Downline Row (Max 3 Width)", "🔍 Master Genealogy Database"])
    
    with tab_sales:
        st.subheader("Process Team Order Commission Log")
        st.caption("Submitting order entries registers sales targets and pushes calculations upward immediately.")
        sale_cv = st.number_input("Enter Product Commission Value (CV)", min_value=0, max_value=5000, value=300, step=50)
        
        if st.button("Submit Sale Ledger Entry", use_container_width=True):
            if sale_cv > 0:
                payout_result = process_flantech_sale(current_phone, sale_cv)
                st.success("Sale order processed! Volume vectors synced successfully across upline nodes.")
                if payout_result:
                    st.write("##### Direct Sales Commission Distribution Split Receipt Detail:")
                    st.json(payout_result)
                st.rerun()
                
    with tab_tree:
        st.subheader("Direct Generation Matrix Slots (Level 1)")
        matrix_data = []
        for i, child_phone in enumerate(user["children"]):
            child_info = db[child_phone]
            matrix_data.append({
                "Matrix Leg Position": f"Leg Row Position {i+1}",
                "Name Member": child_info["name"],
                "Phone ID Link": child_phone,
                "Assigned Rank": child_info["rank"],
                "Introduced By (Sponsor)": db[child_info["sponsor"]]["name"]
            })
            
        if matrix_data:
            st.dataframe(pd.DataFrame(matrix_data), hide_index=True, use_container_width=True)
        else:
            st.info("Your immediate generation level 3-position matrix row contains no active nodes yet.")
            
    with tab_debug:
        st.subheader("Global Debug System Genealogy Node Tree Log")
        st.caption("Operational visibility map tracking live configuration states across the running session instance node variables.")
        global_log = []
        for phone, info in db.items():
            global_log.append({
                "Member Phone Key": phone,
                "Entity Name": info["name"],
                "Sponsor Recruiter Link": info["sponsor"] if info["sponsor"] else "None",
                "Matrix Parent Upline Assigned": info["upline"] if info["upline"] else "ROOT ENGINE ADM",
                "Occupied Limbs Width": f"{len(info['children'])} / 3 Slots occupied",
                "Accrued Earnings Wallet": f"${info['wallet']:,.2f}",
                "Rolling Team Sales Volume": f"{info['team_sales_cv']} CV total value"
            })
        st.dataframe(pd.DataFrame(global_log), hide_index=True, use_container_width=True)

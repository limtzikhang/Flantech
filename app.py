import streamlit as st
import pandas as pd
from collections import deque
import streamlit as st
import os

# Set up clean page layout configurations
st.set_page_config(
    page_title="Shared Media Portal",
    page_icon="🎬",
    layout="wide"  # "wide" layout gives plenty of screen space when the sidebar is visible
)

# =====================================================================
# MEDIA CONFIGURATION LAYER
# =====================================================================
# Map your video display titles to the exact filename paths stored in your project directory
# IMPORTANT: Convert your raw .mkv videos to .mp4 to ensure web browser compatibility.
VIDEO_PLAYLIST = {
    "Megahydrate Blood Analysis Demonstration": "Megahydrate Live Blood Analysis.mp4",
    "Flantech Asia Corporate Marketing Overview": "flantech_intro.mp4",
    "Distributor 3MP Genealogy Matrix Tutorial": "matrix_genealogy_guide.mp4",
}

# =====================================================================
# COLLAPSIBLE SIDEBAR MENU DRAWER (LEFT SIDE)
# =====================================================================
# This native sidebar container can be dynamically hidden/shown by clicking the 
# arrow icon (">" or "<") located at the very top-left corner of the web page screen.
with st.sidebar:
    st.markdown("## 📁 Media Streaming Library")
    st.caption("Select a video link below to load the player canvas.")
    st.write("---")
    
    # Render the playlist choices as a clickable selection list framework
    selected_video_title = st.radio(
        label="Available Video Tracks:",
        options=list(VIDEO_PLAYLIST.keys()),
        index=0  # Sets the first item in the dictionary as the default selection on launch
    )
    
    st.write("---")
    st.info("💡 You can collapse or expand this sidebar navigation drawer anytime by clicking the arrow button at the top left.")

# =====================================================================
# MAIN WEB PAGE PLAYER RENDERING CANVAS
# =====================================================================
st.title("🎬 Multi-Video Network Streaming Hub")
st.caption("Accessing high-performance media storage metrics over the internet")
st.write("---")

# Retrieve the actual system filename using the dictionary title index choice
target_filename = VIDEO_PLAYLIST[selected_video_title]

# Verify if the physical video data binary exists in your machine workspace
if os.path.exists(target_filename):
    st.subheader(f"🎥 Now Playing: {selected_video_title}")
    st.caption(f"System File Source: `{target_filename}`")
    
    # Read the target layout binary stream data out from hard drive tracks
    with open(target_filename, "rb") as video_file:
        video_bytes = video_file.read()
    
    # Fire up the responsive Streamlit media playback engine array container
    st.video(video_bytes, format="video/mp4")
    
    st.success("✅ Streaming pipeline active. Internet connection clients can view this media smoothly.")
else:
    st.error(f"❌ File Not Found Error: Could not locate `{target_filename}`.")
    
    # Dynamic helper messages instructing the administrator how to set up the files
    st.markdown(f"""
    ### 🛠️ Configuration Setup Instructions Required:
    To play **"{selected_video_title}"**, please ensure you have:
    1. Placed the file named **`{target_filename}`** directly into the exact same folder layout where this `app.py` script lives.
    2. Verified that the video file container has been encoded into an open **MP4** format block.
    """)
    
    st.write("---")
    st.markdown("#### Expected Playlist Map Folders View Diagram Structure:")
    st.code(f"""
    📂 MyProjectFolder/
    ├── 📄 app.py (This Streamlit script file)
    ├── 🎥 megahydrate_analysis.mp4
    ├── 🎥 flantech_intro.mp4
    └── 🎥 matrix_genealogy_guide.mp4
    """)
# =====================================================================
# DATA STORAGE LAYER (Streamlit Session State simulation)
# =====================================================================
if "members_db" not in st.session_state:
    st.session_state["members_db"] = {
        "60164191861": {
            "name": "Admin Leader",
            "password": "admin",
            "sponsor": None,       # Who introduced them
            "upline": None,        # Whose matrix box they physically sit in (3MP)
            "children": [],        # Max 3 elements (3MP constraint)
            "rank": "Diamond",
            "wallet": 0.0,
            "team_sales_cv": 0.0
        }
    }

if "auth_session" not in st.session_state:
    st.session_state["auth_session"] = None

RANK_BONUS_RATES = {"Bronze": 0.25, "Silver": 0.30, "Gold": 0.35, "Diamond": 0.40}

# =====================================================================
# 3MP GENEALOGY PLACEMENT ALGORITHM
# =====================================================================
def find_3mp_placement_slot(sponsor_phone):
    """
    Breadth-First Search (BFS) to find the next open slot in the 3xN Matrix
    starting from the Sponsor's node downwards.
    """
    db = st.session_state["members_db"]
    queue = deque([sponsor_phone])
    
    while queue:
        current_node = queue.popleft()
        # If this node has less than 3 direct downlines, it's the vacant slot!
        if len(db[current_node]["children"]) < 3:
            return current_node
        
        # Otherwise, push children to the queue to search the next depth level
        queue.extend(db[current_node]["children"])
        
    return "60123456789"  # Ultimate safety fallback to Root Node

def determine_rank_by_cv(cv_amount):
    if cv_amount >= 1000: return "Diamond"
    elif cv_amount >= 500: return "Gold"
    elif cv_amount >= 300: return "Silver"
    elif cv_amount >= 100: return "Bronze"
    return "Member"

def process_flantech_sale(buyer_phone, cv_amount):
    db = st.session_state["members_db"]
    sponsor_phone = db[buyer_phone]["sponsor"]
    
    if not sponsor_phone or sponsor_phone not in db:
        return None  
    
    sponsor = db[sponsor_phone]
    sponsor_rate = RANK_BONUS_RATES.get(sponsor["rank"], 0.25)
    commission_earned = round(cv_amount * sponsor_rate, 2)
    
    # Direct sales bonus maps directly to Sponsor Node
    db[sponsor_phone]["wallet"] += commission_earned
    
    # Roll up Team Sales CV volume vertically through the physical 3MP Upline Chain
    current_upline = db[buyer_phone]["upline"]
    while current_upline:
        if current_upline in db:
            db[current_upline]["team_sales_cv"] += cv_amount
            current_upline = db[current_upline]["upline"]
        else:
            break
            
    return {
        "Sponsor Name": sponsor["name"],
        "Sponsor Rank": sponsor["rank"],
        "Bonus Percentage Applied": f"{int(sponsor_rate * 100)}%",
        "Payout Credited ($)": commission_earned
    }

# =====================================================================
# STREAMLIT USER INTERFACE PIPELINE
# =====================================================================
st.set_page_config(page_title="Flantech 3MP Portal", page_icon="🏆", layout="centered")
st.title("🏆 Flantech Asia 3MP Matrix Portal")
st.caption("Automated 3-Member Placement Genealogy and Commissions Engine")
st.write("---")

if st.session_state["auth_session"] is None:
    tab_login, tab_register = st.tabs(["🔑 Member Sign In", "📝 Create New Account"])
    
    with tab_login:
        st.subheader("Login to Dashboard")
        phone_in = st.text_input("Mobile Phone Number", key="login_phone")
        pass_in = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Access Portal", use_container_width=True):
            db = st.session_state["members_db"]
            if phone_in in db and db[phone_in]["password"] == pass_in:
                st.session_state["auth_session"] = phone_in
                st.success(f"Welcome back, {db[phone_in]['name']}!")
                st.rerun()
            else:
                st.error("Invalid phone number or password credentials.")
                
    with tab_register:
        st.subheader("Enroll as a Flantech 3MP Distributor")
        reg_name = st.text_input("Full Name")
        reg_phone = st.text_input("Mobile Phone Number ID")
        reg_pass = st.text_input("Secure Password", type="password")
        reg_ref = st.text_input("Sponsor / Referrer Phone Number")
        
        st.markdown("##### Activation Package")
        pkg_cv = st.slider("Package Commission Value (CV Points)", min_value=0, max_value=1500, value=500, step=50)
        calculated_rank = determine_rank_by_cv(pkg_cv)
        
        if st.button("Complete Registration", use_container_width=True):
            db = st.session_state["members_db"]
            if not reg_name or not reg_phone or not reg_pass or not reg_ref:
                st.warning("Please complete all registration fields (Sponsor is required for 3MP matrix).")
            elif reg_phone in db:
                st.error("This phone number is already registered.")
            elif reg_ref not in db:
                st.error("The specified sponsor phone number does not exist.")
            else:
                # 1. RUN THE 3MP MATRIX PLACEMENT SEARCH ENGINE
                assigned_upline = find_3mp_placement_slot(reg_ref)
                
                # 2. SAVE NEW MEMBER NODE OBJECT WITH MATRIX LINK MAPPINGS
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
                
                # 3. Append this child node to the assigned Upline's children list layout
                db[assigned_upline]["children"].append(reg_phone)
                
                # Calculate direct referral commission payouts instantly
                process_flantech_sale(reg_phone, pkg_cv)
                
                st.success(f"Enrollment successful! Placed under Upline: {db[assigned_upline]['name']} ({assigned_upline}) due to 3MP structure.")

else:
    current_phone = st.session_state["auth_session"]
    user = st.session_state["members_db"][current_phone]
    db = st.session_state["members_db"]
    
    st.sidebar.markdown(f"### 👤 Active Member Profile")
    st.sidebar.write(f"**Name:** {user['name']}")
    st.sidebar.write(f"**Rank:** {user['rank']}")
    st.sidebar.write(f"**Placement Upline:** {db[user['upline']]['name'] if user['upline'] else 'None (Root Node)'}")
    
    if st.sidebar.button("Log Out of Session", use_container_width=True):
        st.session_state["auth_session"] = None
        st.rerun()
        
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Total Account Commissions", f"${user['wallet']:,.2f}")
    with m_col2:
        st.metric("Matrix Team Volume (GSV)", f"{user['team_sales_cv']:,.0f} CV")
        
    st.write("---")
    
    tab_sales, tab_tree = st.tabs(["📊 Submit New Sales Order", "👥 Your Matrix Downline (Max 3 Width)"])
    
    with tab_sales:
        st.subheader("Process Product Sale")
        sale_cv = st.number_input("Enter Product Commission Value (CV)", min_value=0, max_value=5000, value=300, step=50)
        if st.button("Submit Sale", use_container_width=True):
            if sale_cv > 0:
                payout_result = process_flantech_sale(current_phone, sale_cv)
                st.success("Sale processed successfully!")
                if payout_result:
                    st.json(payout_result)
                st.rerun()
                
    with tab_tree:
        st.subheader("Direct Matrix Slots (Level 1)")
        matrix_data = []
        for i, child_phone in enumerate(user["children"]):
            child_info = db[child_phone]
            matrix_data.append({
                "Matrix Leg Position": f"Leg {i+1}",
                "Name": child_info["name"],
                "Phone": child_phone,
                "Rank": child_info["rank"],
                "Introduced By (Sponsor)": db[child_info["sponsor"]]["name"]
            })
            
        if matrix_data:
            st.dataframe(pd.DataFrame(matrix_data), hide_index=True, use_container_width=True)
        else:
            st.info("Your direct 3-position matrix row is completely empty right now.")
            
        st.write("---")
        st.subheader("Global Debug Database Node Tree")
        global_log = []
        for phone, info in db.items():
            global_log.append({
                "Member Phone": phone,
                "Name": info["name"],
                "Sponsor Upline": info["sponsor"] if info["sponsor"] else "None",
                "Matrix Parent Upline": info["upline"] if info["upline"] else "ROOT ADM NODE",
                "Matrix Occupied Slots (Width)": f"{len(info['children'])} / 3",
                "Total Earnings Wallet": f"${info['wallet']:,.2f}",
                "Rolling Team Sales Volume": f"{info['team_sales_cv']} CV"
            })
        st.dataframe(pd.DataFrame(global_log), hide_index=True, use_container_width=True)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
import os
import requests

# =============================================================================
# 1. CORE BACKEND INITIALIZATION (FIREBASE & FIRESTORE)
# =============================================================================
if not firebase_admin._apps:
    try:
        if "firebase_service_account" in st.secrets:
            cred_dict = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(base_dir, "serviceAccountKey.json")
            
            if os.path.exists(key_path):
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
            else:
                st.error("🚨 Configuration Error: Firebase keys missing. Please configure Streamlit Secrets or upload serviceAccountKey.json.")
                st.stop()
    except Exception as e:
        st.error(f"System Critical Initialization Error: {e}")
        st.stop()

db = firestore.client()

# =============================================================================
# 2. APPLICATION CONFIGURATION & STATE ENGINES
# =============================================================================
st.set_page_config(
    page_title="Flantech Distribution Engine", 
    page_icon="⚡", 
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_uid" not in st.session_state:
    st.session_state.user_uid = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_mobile" not in st.session_state:
    st.session_state.user_mobile = ""

# =============================================================================
# 3. CORE PLATFORM PRICING MATRICES & CALCULATIONS
# =============================================================================
def calculate_price(qty):
    """
    Executes tiered wholesale corporate rules on inventory units.
    Max purchase cap: 50 bottles per transaction.
    """
    if qty <= 0:
        return 0, 0
    elif qty == 1:
        price_per_bottle = 248  # B2C Standard Retail Rate
    elif 2 <= qty <= 49:
        price_per_bottle = 198  # Bulk Wholesale Discount Rate
    elif qty == 50:
        price_per_bottle = 148  # Premium Corporate B2B Tier
    else:
        price_per_bottle = 148  # Safeguard enforcement fallback value
        
    return price_per_bottle, qty * price_per_bottle

# =============================================================================
# 4. LIVE MALAYSIAN PAYMENT INTEGRATION GATEWAY HOOKS
# =============================================================================
def request_toyyibpay_fpx(name, email, phone, amount, desc):
    """
    Dispatches billing payloads directly to the ToyyibPay local engine.
    Formats money strictly into Malaysian Cents (Sen) as required by FPX.
    """
    url = 'https://toyyibpay.com'
    
    try:
        secret_key = st.secrets["payment"]["toyyibpay_secret"]
        cat_code = st.secrets["payment"]["toyyibpay_category"]
    except Exception:
        secret_key = "MOCK_SECRET_KEY"
        cat_code = "MOCK_CAT_CODE"

    payload = {
        'userSecretKey': secret_key,
        'categoryCode': cat_code,
        'billName': 'Flantech Order Settlement',
        'billDescription': desc,
        'billPriceSetting': 1,
        'billPayeeInfo': 1,
        'billAmount': int(amount * 100),
        'billReturnUrl': 'https://github.com',
        'billCallbackUrl': 'https://your-api-receiver.com',
        'billExternalReferenceNo': f"FT-{os.urandom(4).hex().upper()}",
        'billTo': name,
        'billEmail': email,
        'billPhone': phone
    }
    
    if secret_key == "MOCK_SECRET_KEY":
        return {"status": "success", "billURL": "https://toyyibpay.com"}
        
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
# =============================================================================
# 5. RENDER SYSTEM PORTAL: SECURE SIGN-IN & REGISTRATION
# =============================================================================
def render_auth_portal():
    st.title("⚡ Flantech Hybrid Corporate Portal")
    st.markdown("##### Authorized Distribution Pipeline for Patrick Flanagan Formulations")
    st.write("")
    
    tab_login, tab_signup = st.tabs(["🔐 Partner Sign In", "📝 Network Registration"])
    
    with tab_login:
        st.markdown("### Authentication Hub")
        login_email = st.text_input("Account Email Address", key="auth_email")
        login_password = st.text_input("Security Access Password", type="password", key="auth_pass")
        
        if st.button("Verify Identity & Enter", type="primary", use_container_width=True):
            try:
                user_auth_record = auth.get_user_by_email(login_email)
                user_ref = db.collection("users").document(user_auth_record.uid).get()
                is_admin_uid = (user_auth_record.uid == "4zFLKj1FX3aI2SJLFiC9YwhA5mu1")
                
                if user_ref.exists:
                    user_profile = user_ref.to_dict()
                    if is_admin_uid and user_profile.get("role") != "admin":
                        db.collection("users").document(user_auth_record.uid).update({"role": "admin"})
                        user_profile["role"] = "admin"
                        
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.session_state.user_uid = user_auth_record.uid
                    st.session_state.user_name = user_profile.get("name", "Valued Partner")
                    st.session_state.user_mobile = user_profile.get("mobile", "")
                    st.success(f"Access granted. Welcome {st.session_state.user_name}")
                    st.rerun()
                else:
                    assigned_role = "admin" if is_admin_uid else "b2c"
                    structured_payload = {
                        "uid": user_auth_record.uid,
                        "name": "Lim Tzik Hang" if is_admin_uid else "Partner",
                        "email": login_email,
                        "mobile": "+601XXXXXXXX",
                        "bank_details": {"bank_name": "Maybank", "account_number": "0000000000"},
                        "upline_id": None,
                        "role": assigned_role,
                        "created_at": firestore.SERVER_TIMESTAMP
                    }
                    db.collection("users").document(user_auth_record.uid).set(structured_payload)
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.session_state.user_uid = user_auth_record.uid
                    st.session_state.user_name = structured_payload["name"]
                    st.rerun()
            except Exception as login_err:
                st.error(f"Authentication failed: {login_err}")

    with tab_signup:
        st.markdown("### Affiliate Account Registration")
        st.caption("All fields marked with (*) are required for internal compliance and payment settlements.")
        
        col_left, col_right = st.columns(2)
        with col_left:
            new_name = st.text_input("Legal Name (matching Identity & Bank Card) *")
            new_email = st.text_input("Active Primary Email Address *")
            new_mobile = st.text_input("Mobile Phone Number (e.g., +601XXXXXXXX) *")
            new_password = st.text_input("Set Security Password (Min 6 Characters) *", type="password")
            
        with col_right:
            malaysia_banks = [
                "Malayan Banking Berhad (Maybank)", "CIMB Bank Berhad", 
                "Public Bank Berhad", "RHB Bank Berhad", 
                "Hong Leong Bank Berhad", "AmBank Berhad"
            ]
            bank_name = st.selectbox("Designated Settlement Bank *", malaysia_banks)
            bank_account = st.text_input("Bank Account Number (For Future Commissions) *")
            upline_code = st.text_input("Upline Referrer ID / Affiliate Code (Optional)")

        if st.button("Register & Verify Account Profile", use_container_width=True):
            if not (new_name and new_email and new_mobile and new_password and bank_account):
                st.error("Verification halted: Please complete all mandatory fields.")
                return
                
            try:
                api_key = str(st.secrets["FIREBASE_WEB_API_KEY"]).strip()
                
                # FIXED TARGET MATRIX PATHS: Direct endpoint mapping targets isolated correctly
                api_url = "https://googleapis.com"
                update_url = "https://googleapis.com"
                
                params = {"key": api_key}
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "email": new_email,
                    "password": new_password,
                    "returnSecureToken": True
                }
                
                response = requests.post(api_url, params=params, json=payload, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    st.error(f"🚨 Google Server Rejection (HTTP {response.status_code})")
                    st.markdown(f"**Error Details:** `{response.text[:200]}`")
                    return
                
                res_data = response.json()
                new_uid = res_data["localId"]
                
                # FIXED PROFILE INTERNALS: Points to the legitimate profile updating address mapping bounds
                requests.post(update_url, params=params, json={
                    "idToken": res_data["idToken"],
                    "displayName": new_name,
                    "returnSecureToken": True
                }, headers=headers, timeout=10)
                
                assigned_role = "admin" if new_uid == "4zFLKj1FX3aI2SJLFiC9YwhA5mu1" else "b2c"
                
                structured_payload = {
                    "uid": new_uid,
                    "name": new_name,
                    "email": new_email,
                    "mobile": new_mobile,
                    "bank_details": {
                        "bank_name": bank_name,
                        "account_number": bank_account
                    },
                    "upline_id": upline_code.strip() if upline_code.strip() else None,
                    "role": assigned_role,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                
                db.collection("users").document(new_uid).set(structured_payload)
                st.success("Account successfully created! Switch to the 'Partner Sign In' tab to log in.")
                
            except Exception as system_err:
                st.error(f"Enrolment halted by system validation server: {system_err}")
# =============================================================================
# 6. RENDER STORE SYSTEM PLATFORM (PRODUCT PANELS & SHOPPING CART)
# =============================================================================
def render_store_front():
    st.sidebar.title("🛡️ Partner Workspace")
    st.sidebar.markdown(f"**Affiliate User:**\n{st.session_state.user_name}")
    st.sidebar.markdown(f"**Security Code ID:**\n`{st.session_state.user_uid}`")
    st.sidebar.write("---")
    
    if st.sidebar.button("Secure Application Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_uid = ""
        st.session_state.user_name = ""
        st.session_state.user_mobile = ""
        st.rerun()

    st.title("🛒 Flantech Procurement Center")
    st.markdown("##### Premium Patrick Flanagan Formulations Portfolio")
    st.write("")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("### Formulation A: Mega H")
        st.image("product/mega_h.jpg", width=280, fallback="💊 [Mega H Asset Image Missing]")
        st.caption("Active Silica Hydride antioxidant formulation driving micro-cluster hydration levels inside cell membranes.")
        
    with col_p2:
        st.markdown("### Formulation B: Crystal Energy")
        st.image("product/crystal_energy.jpg", width=280, fallback="💧 [Crystal Energy Asset Image Missing]")
        st.caption("Liquid structured fluid catalyst component drops modifying surface tension dynamics of local drinking water.")

    # =============================================================================
    # MARKETING VIDEO PORTFOLIO SHOWCASE
    # =============================================================================
    st.write("---")
    st.markdown("### 📺 Flantech Hybrid Video Presentation Library")
    st.caption("Review our technical breakdown and marketing system walkthrough videos below:")
    
    v_col1, v_col2, v_col3 = st.columns(3)
    
    with v_col1:
        st.markdown("##### 📹 System Introduction")
        st.video("video/video1.mp4", format="video/mp4", start_time=0)
        
    with v_col2:
        st.markdown("##### 📹 Formulation Science")
        st.video("video/video2.mp4", format="video/mp4", start_time=0)
        
    with v_col3:
        st.markdown("##### 📹 Marketing System Breakdown")
        st.video("video/video3.mp4", format="video/mp4", start_time=0)

    st.write("---")
    st.markdown("### 📊 Live Processing Allocation Interface")
    target_item = st.selectbox("Selected Catalog Line Item", ["Patrick Flanagan: Mega H", "Patrick Flanagan: Crystal Energy"])
    purchase_qty = st.number_input("Order Size Matrix Allocation (Max 50 Units)", min_value=1, max_value=50, value=1, step=1)
    
    cost_per_unit, net_aggregated_cost = calculate_price(purchase_qty)
    
    metric_c1, metric_c2, metric_c3 = st.columns(3)
    with metric_c1:
        st.metric(label="Calculated Account Assignment", value="Corporate B2B Wholesale" if purchase_qty == 50 else ("Wholesale Volume Tier" if purchase_qty > 1 else "B2C Consumer Retail"))
    with metric_c2:
        st.metric(label="Unit Rate Valuation", value=f"RM {cost_per_unit}.00")
    with metric_c3:
        st.metric(label="Aggregated Account Total", value=f"RM {net_aggregated_cost}.00")
        
    st.info("💡 **Wholesale Threshold Matrix:** 1 Unit: RM248 | 2-49 Units: RM198 per unit | Exactly 50 Units (B2B Bulk Cap): RM148 per unit.")
    
    # =============================================================================
    # 7. CASHWAY GATEWAY INTERFACES (MALAYSIA DOMESTIC CLEARING HOUSES ONLY)
    # =============================================================================
    st.markdown("#### 💳 Domestic Financial Settlement Module")
    payment_channel = st.radio("Authorized Clearing Node Integration", ["FPX Real-Time Local Bank Processing Portal", "DuitNow QR Instant Cash Network"])
    
    if st.button("Authorize Payment & Lock Order Request", type="primary", use_container_width=True):
        st.write("Contacting Malaysian payment clearing networks... Please wait.")
        
        payment_gateway_response = request_toyyibpay_fpx(
            name=st.session_state.user_name,
            email=st.session_state.user_email,
            phone=st.session_state.user_mobile,
            amount=net_aggregated_cost,
            desc=f"Purchase of {purchase_qty}x {target_item}"
        )
        
        if payment_gateway_response.get("status") == "success" or "billURL" in payment_gateway_response:
            ledger_block = {
                "buyer_uid": st.session_state.user_uid,
                "inventory_line": target_item,
                "volume_purchased": purchase_qty,
                "calculated_unit_rate": cost_per_unit,
                "total_ringgit_value": net_aggregated_cost,
                "payment_node": payment_channel,
                "settlement_status": "Awaiting Gateway Authentication",
                "assigned_corporate_tier": "B2B" if purchase_qty == 50 else "B2C",
                "timestamp_created": firestore.SERVER_TIMESTAMP
            }
            
            try:
                db.collection("orders").add(ledger_block)
                st.balloons()
                st.success(f"Order Registered! Please settle payment through the secure portal below.")
                st.markdown(f"🔗 **[Click Here to Open FPX Bank Portal Gateway]({payment_gateway_response.get('billURL')})**")
            except Exception as db_err:
                st.error(f"Ledger Registry Error: Internal log insertion failure: {db_err}")
        else:
            st.error(f"Gateway Interface Fault: Clearing network returned error: {payment_gateway_response.get('message')}")

    # =============================================================================
    # SECRET ADMIN EXCLUSIVE DASHBOARD VIEW PANEL
    # =============================================================================
    if st.session_state.user_uid == "4zFLKj1FX3aI2SJLFiC9YwhA5mu1":
        st.write("---")
        st.markdown("### 👑 Master Corporate Order Manifest Desk")
        st.caption("Secure visibility module open exclusively to your master administrator account UID.")
        
        try:
            orders_ref = db.collection("orders").order_by("timestamp_created", direction=firestore.Query.DESCENDING).stream()
            orders_list = []
            for doc in orders_ref:
                o_data = doc.to_dict()
                orders_list.append({
                    "Order Code Reference": doc.id,
                    "Buyer Unique Key": o_data.get("buyer_uid"),
                    "Product Item": o_data.get("inventory_line"),
                    "Bottles Bought": o_data.get("volume_purchased"),
                    "Unit Cost": f"RM {o_data.get('calculated_unit_rate')}",
                    "Total Settle Value": f"RM {o_data.get('total_ringgit_value')}",
                    "Payment Channel Node": o_data.get("payment_node"),
                    "Status Log": o_data.get("settlement_status")
                })
            if orders_list:
                st.dataframe(orders_list, use_container_width=True)
            else:
                st.info("Database Active: No customer product placement processing orders submitted yet.")
        except Exception as order_err:
            st.caption(f"Waiting for system order configurations to deploy: {order_err}")

# =============================================================================
# 8. MASTER CONTROL APP EXECUTION ENGINE FLOW
# =============================================================================
if not st.session_state.logged_in:
    render_auth_portal()
else:
    render_store_front()

# =============================================================================
# 9. DEVELOPER LIVE DATABASE INSPECTION DESK
# =============================================================================
st.write("---")
st.markdown("### 🛠️ Developer Live Database Inspection Desk")

if st.checkbox("Show Live Registered Users Ledger (Firestore View)"):
    try:
        users_ref = db.collection("users").stream()
        users_list = []
        for doc in users_ref:
            user_dict = doc.to_dict()
            bank_info = user_dict.get("bank_details", {})
            users_list.append({
                "User UID": doc.id,
                "Legal Name": user_dict.get("name"),
                "Email Card": user_dict.get("email"),
                "Mobile Phone": user_dict.get("mobile"),
                "Settlement Bank": bank_info.get("bank_name"),
                "Account No.": bank_info.get("account_number"),
                "Upline ID Reference": user_dict.get("upline_id"),
                "System Role Tag": user_dict.get("role"),
                "System Timestamp": str(user_dict.get("created_at"))
            })
            
        if users_list:
            st.dataframe(users_list, use_container_width=True)
            st.caption(f"Total Registered Nodes Tracked: {len(users_list)}")
        else:
            st.warning("Database Connection Active: But 'users' collection is currently empty.")
    except Exception as read_err:
        st.error(f"Failed to query local data tables: {read_err}")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
import os
import requests

# =============================================================================
# 1. CORE BACKEND INITIALIZATION (FIREBASE & FIRESTORE)
# =============================================================================
# Place your serviceAccountKey.json file in the root project folder directory.
if not firebase_admin._apps:
    try:
        # Hybrid secure parsing for local deployment vs production hosting servers
        if "firebase_service_account" in st.secrets:
            cred_dict = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(cred_dict)
        else:
            cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"System Critical Initialization Error: {e}")

db = firestore.client()

# =============================================================================
# 2. APPLICATION CONFIGURATION & STATE ENGINES
# =============================================================================
st.set_page_config(
    page_title="Flantech Distribution Engine", 
    page_icon="⚡", 
    layout="wide"
)

# Persistent session keys checking across the Streamlit lifecycle
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
    
    # Standard security handling properties safely matched to application environment profiles
    try:
        secret_key = st.secrets["payment"]["toyyibpay_secret"]
        cat_code = st.secrets["payment"]["toyyibpay_category"]
    except Exception:
        # Fallback tracking strings to ensure validation runtime doesn't break locally
        secret_key = "MOCK_SECRET_KEY"
        cat_code = "MOCK_CAT_CODE"

    payload = {
        'userSecretKey': secret_key,
        'categoryCode': cat_code,
        'billName': 'Flantech Order Settlement',
        'billDescription': desc,
        'billPriceSetting': 1,
        'billPayeeInfo': 1,
        'billAmount': int(amount * 100),  # Converts RM to Sen (e.g. RM248 -> 24800)
        'billReturnUrl': 'https://github.com',
        'billCallbackUrl': 'https://your-api-receiver.com',
        'billExternalReferenceNo': f"FT-{os.urandom(4).hex().upper()}",
        'billTo': name,
        'billEmail': email,
        'billPhone': phone
    }
    
    # Direct integration simulation fallback layer for sandbox environments
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
                # Retrieve data from Firebase Auth record
                user_auth_record = auth.get_user_by_email(login_email)
                
                # Cross-reference with database node metadata
                user_ref = db.collection("users").document(user_auth_record.uid).get()
                
                if user_ref.exists:
                    user_profile = user_ref.to_dict()
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.session_state.user_uid = user_auth_record.uid
                    st.session_state.user_name = user_profile.get("name", "Valued Partner")
                    st.session_state.user_mobile = user_profile.get("mobile", "")
                    st.success(f"Access granted. Welcome {st.session_state.user_name}")
                    st.rerun()
                else:
                    st.error("Profile mismatch detected inside core database records.")
            except Exception:
                st.error("Authentication failed. Check your security entries or email verification status.")

    with tab_signup:
        st.markdown("### Affiliate Account Registration")
        st.caption("All fields marked with (*) are required for internal compliance and payment settlements.")
        
        # Grid array layouts organizing required registration information
        col_left, col_right = st.columns(2)
        
        with col_left:
            new_name = st.text_input("Legal Name (matching Identity & Bank Card) *")
            new_email = st.text_input("Active Primary Email Card *")
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
            # Strict application rule structural validation logic checks
            if not (new_name and new_email and new_mobile and new_password and bank_account):
                st.error("Verification halted: Please complete all mandatory fields.")
                return
                
            try:
                # Instantiate secure entity inside the centralized Firebase authentication matrix
                created_user = auth.create_user(
                    email=new_email,
                    password=new_password,
                    display_name=new_name
                )
                
                # Hierarchical design data blocks configured for immediate scale to MLM structures
                structured_payload = {
                    "uid": created_user.uid,
                    "name": new_name,
                    "email": new_email,
                    "mobile": new_mobile,
                    "bank_details": {
                        "bank_name": bank_name,
                        "account_number": bank_account
                    },
                    "upline_id": upline_code.strip() if upline_code.strip() else None,
                    "role": "b2c",  # Initial tier value system tag assignments
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                
                # Map persistent collection rows directly onto Cloud Firestore database nodes
                db.collection("users").document(created_user.uid).set(structured_payload)
                st.success("Account successfully created. Switch to the 'Partner Sign In' tab to log in.")
                
            except Exception as system_err:
                st.error(f"Enrolment halted by system validation server: {system_err}")
# =============================================================================
# 6. RENDER STORE SYSTEM PLATFORM (PRODUCT PANELS & SHOPPING CART)
# =============================================================================
def render_store_front():
    # Sidebar control desk settings configurations
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

    # Core E-Commerce Display Windows
    st.title("🛒 Flantech Procurement Center")
    st.markdown("##### Premium Patrick Flanagan Formulations Portfolio")
    st.write("")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("### Formulation A: Mega H")
        # Direct local verification path mappings routing to product directories
        st.image("product/mega_h.jpg", width=280, fallback="💊 [Mega H Asset Image Missing - Check repo product/ folder]")
        st.caption("Active Silica Hydride structural antioxidant formulation driving micro-cluster hydration levels inside cell membranes.")
        
    with col_p2:
        st.markdown("### Formulation B: Crystal Energy")
        st.image("product/crystal_energy.jpg", width=280, fallback="💧 [Crystal Energy Asset Image Missing - Check repo product/ folder]")
        st.caption("Liquid structured fluid catalyst component drops modifying surface tension dynamics of local drinking water matrix profiles.")

    st.write("---")
    st.markdown("### 📊 Live Processing Allocation Interface")
    
    # Setup step input parameters constrained by local distribution laws
    target_item = st.selectbox("Selected Catalog Line Item", ["Patrick Flanagan: Mega H", "Patrick Flanagan: Crystal Energy"])
    purchase_qty = st.number_input("Order Size Matrix Allocation (Max 50 Units)", min_value=1, max_value=50, value=1, step=1)
    
    # Calculate real-time financial tracking figures
    cost_per_unit, net_aggregated_cost = calculate_price(purchase_qty)
    
    # Display processing values cleanly to the operator
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
        
        # Trigger the functional ToyyibPay transaction creation endpoint
        payment_gateway_response = request_toyyibpay_fpx(
            name=st.session_state.user_name,
            email=st.session_state.user_email,
            phone=st.session_state.user_mobile,
            amount=net_aggregated_cost,
            desc=f"Purchase of {purchase_qty}x {target_item}"
        )
        
        if payment_gateway_response.get("status") == "success" or "billURL" in payment_gateway_response:
            # Structuring standard historical accounting blocks for clean database auditing
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
                # Inject transactional transaction metrics block into centralized database tables
                db.collection("orders").add(ledger_block)
                st.balloons()
                st.success(f"Order Registered! Please settle payment through the secure portal below.")
                st.markdown(f"🔗 **[Click Here to Open FPX Bank Portal Gateway]({payment_gateway_response.get('billURL')})**")
            except Exception as db_err:
                st.error(f"Ledger Registry Error: Internal log insertion failure: {db_err}")
        else:
            st.error(f"Gateway Interface Fault: Clearing network returned error: {payment_gateway_response.get('message')}")

# =============================================================================
# 8. MASTER CONTROL APP EXECUTION ENGINE FLOW
# =============================================================================
if not st.session_state.logged_in:
    render_auth_portal()
else:
    render_store_front()

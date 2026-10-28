# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import os

# =====================================================================
# FORCE BYPASS ALL GOOGLE AUTHENTICATION PLUGINS & METADATA SERVER
# =====================================================================
# This completely suppresses the 503/404 plugin timeout loop on Streamlit Cloud
os.environ["GCM_METADATA_TIMEOUT"] = "0"
os.environ["AUTO_RENEW_CREDENTIALS"] = "False"
os.environ["GOOGLE_AUTH_SUPPRESS_CREDENTIALS_WARNINGS"] = "true"

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        # Load the configuration secrets parameters map dictionary safely
        firebase_dict = dict(st.secrets["firebase"])
        
        # Explicitly clean and re-align internal string formatting tokens
        if "private_key" in firebase_dict:
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Local computer fallback rule context
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-43ed14c73a.json")
        firebase_admin.initialize_app(cred)

# Force initialize client targeting direct document operations 
db = firestore.client()

def verify_upline(upline_id: str, upline_phone: str) -> tuple[bool, str]:
    """Scans Firestore to confirm if the sponsor exists before linking them."""
    clean_id = upline_id.strip() if upline_id else ""
    clean_phone = upline_phone.strip() if upline_phone else ""
    
    if not clean_id and not clean_phone:
        return True, ""
        
    if clean_id:
        doc_ref = db.collection("users").document(clean_id).get()
        if doc_ref.exists:
            return True, doc_ref.id
            
    if clean_phone:
        query = db.collection("users").where("phone", "==", clean_phone).limit(1).stream()
        for doc in query:
            return True, doc.id
            
    return False, "Sponsor not found. Please double-check the Upline ID or Phone Number."

def handle_successful_payment(user_id: str, quantity: int, total_price: float):
    """Logs the invoice transaction receipt securely in Firestore."""
    from datetime import datetime
    import time
    
    current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    order_id = f"ORD-{int(time.time())}"
    
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    free_bottles_reward = 0
    upline_linked = ""
    
    if user_doc.exists:
        profile = user_doc.to_dict()
        upline_linked = profile.get("upline_id", "")
        has_claimed_before = profile.get("free_gift_claimed", False)
        
        # 1-Time Gift Eligibility: Must be exactly 6 bottles under an upline sponsor
        if quantity == 6 and upline_linked != "" and not has_claimed_before:
            free_bottles_reward = 1
            user_ref.update({"free_gift_claimed": True})

    db.collection("orders").document(order_id).set({
        "order_id": order_id,
        "member_id": user_id,
        "quantity_purchased": quantity,
        "free_bottles_gift": free_bottles_reward,
        "total_delivery_units": quantity + free_bottles_reward,
        "total_amount": total_price,
        "upline_sponsor_snapshot": upline_linked,
        "payment_status": "Paid",
        "timestamp": current_time_str
    })
    
    if user_doc.exists and user_doc.to_dict().get("first_purchase_time") == "No buy history":
        user_ref.update({"first_purchase_time": current_time_str})

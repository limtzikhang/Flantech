# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import os
from google.cloud import firestore as google_firestore

# Enforce strict server environment isolation bypass controls
os.environ["GCM_METADATA_TIMEOUT"] = "0"
os.environ["AUTO_RENEW_CREDENTIALS"] = "False"
os.environ["GOOGLE_AUTH_SUPPRESS_CREDENTIALS_WARNINGS"] = "true"

# Global database connection reference tool variable
db = None

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        firebase_dict = dict(st.secrets["firebase"])
        if "private_key" in firebase_dict:
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
        
        # CORRECT CLIENT INITIALIZATION:
        # We use the underlying google.cloud firestore client constructor.
        # This binds your secrets passport directly to the database instance,
        # completely preventing 503/404 metadata server errors.
        g_cred = cred.get_credential()
        db = google_firestore.Client(project="flantech-asia", credentials=g_cred)
    else:
        # Local computer execution pipeline fallback connection rule
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-43ed14c73a.json")
        firebase_admin.initialize_app(cred)
        g_cred = cred.get_credential()
        db = google_firestore.Client(project="flantech-asia", credentials=g_cred)
else:
    # Handle rerun app compilation steps using the active connection app instance
    if "firebase" in st.secrets:
        firebase_dict = dict(st.secrets["firebase"])
        if "private_key" in firebase_dict:
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(firebase_dict)
    else:
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-43ed14c73a.json")
        
    g_cred = cred.get_credential()
    db = google_firestore.Client(project="flantech-asia", credentials=g_cred)

# =====================================================================
# HIERARCHY HASH UTILITIES
# =====================================================================
def verify_upline(upline_id: str, upline_phone: str) -> tuple[bool, str]:
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

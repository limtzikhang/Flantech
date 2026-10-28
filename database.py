# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import os
from google.cloud import firestore as google_firestore

# Direct environment variable bypass mappings
os.environ["GCM_METADATA_TIMEOUT"] = "0"
os.environ["AUTO_RENEW_CREDENTIALS"] = "False"

db = None

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        firebase_dict = dict(st.secrets["firebase"])
        if "private_key" in firebase_dict:
            # Clean string conversions automatically
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n").strip()
            
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
        db = google_firestore.Client(project="flantech-asia", credentials=cred.get_credential())
    else:
        # Local computer developer execution fallback route
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-43ed14c73a.json")
        firebase_admin.initialize_app(cred)
        db = google_firestore.Client(project="flantech-asia", credentials=cred.get_credential())
else:
    # Rerun logic mapping alignment
    firebase_dict = dict(st.secrets["firebase"]) if "firebase" in st.secrets else None
    if firebase_dict and "private_key" in firebase_dict:
        firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n").strip()
        cred = credentials.Certificate(firebase_dict)
    else:
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-43ed14c73a.json")
    db = google_firestore.Client(project="flantech-asia", credentials=cred.get_credential())

def verify_upline(upline_id: str, upline_phone: str) -> tuple[bool, str]:
    clean_id = upline_id.strip() if upline_id else ""
    clean_phone = upline_phone.strip() if upline_phone else ""
    if not clean_id and not clean_phone: return True, ""
    if clean_id:
        doc = db.collection("users").document(clean_id).get()
        if doc.exists: return True, doc.id
    if clean_phone:
        query = db.collection("users").where("phone", "==", clean_phone).limit(1).stream()
        for doc in query: return True, doc.id
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
        if quantity == 6 and upline_linked != "" and not profile.get("free_gift_claimed", False):
            free_bottles_reward = 1
            user_ref.update({"free_gift_claimed": True})
    db.collection("orders").document(order_id).set({
        "order_id": order_id, "member_id": user_id, "quantity_purchased": quantity,
        "free_bottles_gift": free_bottles_reward, "total_delivery_units": quantity + free_bottles_reward,
        "total_amount": total_price, "upline_sponsor_snapshot": upline_linked, "payment_status": "Paid", "timestamp": current_time_str
    })
    if user_doc.exists and user_doc.to_dict().get("first_purchase_time") == "No buy history":
        user_ref.update({"first_purchase_time": current_time_str})

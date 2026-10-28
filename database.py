# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import os

# =====================================================================
# FORCE BYPASS GOOGLE METADATA PLUGIN LOOKUP (CRITICAL SERVER FIX)
# =====================================================================
# This tells the Python system to skip looking for Google internal plug-ins,
# instantly clearing the 60s timeout error on Streamlit Cloud.
os.environ["GCM_METADATA_TIMEOUT"] = "0"
os.environ["AUTO_RENEW_CREDENTIALS"] = "False"

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        # Load the configuration secrets parameters map dictionary
        firebase_dict = dict(st.secrets["firebase"])
        
        # Explicitly convert the text characters back into system line markers
        if "private_key" in firebase_dict:
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Local computer execution pipeline fallback connection rule
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-43ed14c73a.json")
        firebase_admin.initialize_app(cred)

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

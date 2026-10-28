# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        # Convert TOML structure parameters safely into local storage dict
        firebase_dict = dict(st.secrets["firebase"])
        
        if "private_key" in firebase_dict:
            # Wipe away any trailing noise spaces or double slashes
            pk = firebase_dict["private_key"].replace("\\n", "\n").strip()
            
            # Formulate the explicit pristine layout block text
            if "-----BEGIN PRIVATE KEY-----" in pk and "-----END PRIVATE KEY-----" in pk:
                body = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").strip()
                cleaned_body = "\n".join([line.strip() for line in body.splitlines() if line.strip()])
                firebase_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{cleaned_body}\n-----END PRIVATE KEY-----\n"
        
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Local computer sandbox development execution environment fallback
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-43ed14c73a.json")
        firebase_admin.initialize_app(cred)

db = firestore.client()

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

# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        # 1. Pull the secret data into a dictionary structure
        firebase_dict = dict(st.secrets["firebase"])
        
        # 2. CRITICAL FIX: Clean and re-align the RSA key format parameters
        if "private_key" in firebase_dict:
            pk = firebase_dict["private_key"]
            
            # Remove any accidental literal "\n" text strings or duplicate escapes
            pk = pk.replace("\\n", "\n")
            
            # Standardize the headers and cleanly join internal chunks with true newlines
            if "-----BEGIN PRIVATE KEY-----" in pk and "-----END PRIVATE KEY-----" in pk:
                # Strip out headers to isolate the raw cryptographic base64 text block
                raw_body = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").strip()
                # Remove any accidental spaces injected by string copy operations
                raw_body_cleaned = "\n".join([line.strip() for line in raw_body.splitlines() if line.strip()])
                
                # Reconstruct the pristine, perfectly line-broken PEM structure
                firebase_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{raw_body_cleaned}\n-----END PRIVATE KEY-----\n"

        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Local computer fallback connection rule
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-078f0e696c.json")
        firebase_admin.initialize_app(cred)

db = firestore.client()

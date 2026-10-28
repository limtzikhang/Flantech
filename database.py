# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

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
        cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-078f0e696c.json")
        firebase_admin.initialize_app(cred)

db = firestore.client()

# database.py
import streamlit as st
import requests
import json
import time
from datetime import datetime

# database.py - Update the absolute URL configuration at the top
PROJECT_ID = "flantech-asia"

# FIXED BASE_URL PATH STRUCTURE:
BASE_URL = f"https://googleapis.com{PROJECT_ID}/databases/(default)/documents"


class SimpleFirestoreRESTClient:
    """
    A lightweight, high-performance Firestore connection engine using plain HTTP REST requests.
    Completely bypasses all Google authentication plugins and metadata timeouts on Streamlit Cloud.
    """
    def __init__(self):
        pass

    def collection(self, collection_name):
        self.active_collection = collection_name
        return self

    def document(self, doc_id):
        self.active_doc_id = doc_id
        return self

    def set(self, data_dict):
        """Writes or overwrites a document using the Firestore REST API."""
        url = f"{BASE_URL}/{self.active_collection}/{self.active_doc_id}"
        
        # Transform flat dictionary parameters to Firestore REST value mappings
        fields = {}
        for k, v in data_dict.items():
            if isinstance(v, bool):
                fields[k] = {"booleanValue": v}
            elif isinstance(v, (int, float)):
                fields[k] = {"doubleValue": float(v)}
            else:
                fields[k] = {"stringValue": str(v)}
                
        payload = {"fields": fields}
        response = requests.patch(url, json=payload)
        return response.ok

    def get(self):
        """Fetches a document from Firestore REST API."""
        url = f"{BASE_URL}/{self.active_collection}/{self.active_doc_id}"
        response = requests.get(url)
        
        class DocumentSnapshot:
            def __init__(self, res):
                self.exists = res.status_code == 200
                self._raw = res.json() if self.exists else {}
            
            def to_dict(self):
                if not self.exists:
                    return {}
                fields = self._raw.get("fields", {})
                flat_dict = {}
                for k, v in fields.items():
                    if "stringValue" in v:
                        flat_dict[k] = v["stringValue"]
                    elif "booleanValue" in v:
                        flat_dict[k] = v["booleanValue"]
                    elif "doubleValue" in v:
                        flat_dict[k] = float(v["doubleValue"])
                    elif "integerValue" in v:
                        flat_dict[k] = int(v["integerValue"])
                return flat_dict
                
        return DocumentSnapshot(response)

    def update(self, data_dict):
        """Updates specific fields in a document using Firestore REST API patch rules."""
        url = f"{BASE_URL}/{self.active_collection}/{self.active_doc_id}"
        
        # Format document field modifiers 
        fields = {}
        update_masks = []
        for k, v in data_dict.items():
            update_masks.append(f"updateMask.fieldPaths={k}")
            if isinstance(v, bool):
                fields[k] = {"booleanValue": v}
            elif isinstance(v, (int, float)):
                fields[k] = {"doubleValue": float(v)}
            else:
                fields[k] = {"stringValue": str(v)}
                
        url = f"{url}?{'&'.join(update_masks)}"
        payload = {"fields": fields}
        response = requests.patch(url, json=payload)
        return response.ok

    def delete(self):
        """Deletes a document from the Firestore collection ledger."""
        url = f"{BASE_URL}/{self.active_collection}/{self.active_doc_id}"
        response = requests.delete(url)
        return response.ok

    def stream(self):
        """Streams all documents in a collection using the Firestore REST API list operation."""
        url = f"{BASE_URL}/{self.active_collection}"
        response = requests.get(url)
        if response.status_code != 200:
            return []
            
        documents = response.json().get("documents", [])
        class DocWrapper:
            def __init__(self, raw_doc):
                self.id = raw_doc.get("name", "").split("/")[-1]
                self._raw = raw_doc
            def to_dict(self):
                fields = self._raw.get("fields", {})
                flat_dict = {}
                for k, v in fields.items():
                    if "stringValue" in v:
                        flat_dict[k] = v["stringValue"]
                    elif "booleanValue" in v:
                        flat_dict[k] = v["booleanValue"]
                    elif "doubleValue" in v:
                        flat_dict[k] = float(v["doubleValue"])
                    elif "integerValue" in v:
                        flat_dict[k] = int(v["integerValue"])
                return flat_dict
                
        return [DocWrapper(d) for d in documents]

    def where(self, field, op, value):
        """REST query filter mapping layer."""
        self.filter_field = field
        self.filter_value = value
        return self

    def limit(self, num):
        return self

    def execute_query(self):
        """Scans the collection documents matching specific string filters."""
        all_docs = self.stream()
        matched = []
        for doc in all_docs:
            d = doc.to_dict()
            if d.get(self.filter_field) == self.filter_value:
                matched.append(doc)
        return matched

# Instantiate the self-contained database wrapper globally
db = SimpleFirestoreRESTClient()

# =====================================================================
# SYSTEM OPERATIONAL UTILITIES
# =====================================================================
def verify_upline(upline_id: str, upline_phone: str) -> tuple[bool, str]:
    clean_id = upline_id.strip() if upline_id else ""
    clean_phone = upline_phone.strip() if upline_phone else ""
    
    if not clean_id and not clean_phone:
        return True, ""
        
    if clean_id:
        doc = db.collection("users").document(clean_id).get()
        if doc.exists:
            return True, doc.id
            
    if clean_phone:
        db.where("phone", "==", clean_phone)
        query = db.execute_query()
        for doc in query:
            return True, doc.id
            
    return False, "Sponsor not found. Please double-check the Upline ID or Phone Number."

def handle_successful_payment(user_id: str, quantity: int, total_price: float):
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

# database.py
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time

# Initialize Firebase safely
if not firebase_admin._apps:
    cred = credentials.Certificate("flantech-asia-firebase-adminsdk-fbsvc-078f0e696c.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def verify_upline(upline_id: str, upline_phone: str) -> tuple[bool, str]:
    """Scans Firestore to confirm if the sponsor exists before linking them."""
    if not upline_id and not upline_phone:
        return True, ""
    if upline_id:
        doc_ref = db.collection("users").document(upline_id.strip()).get()
        if doc_ref.exists:
            return True, doc_ref.id
    if upline_phone:
        query = db.collection("users").where("phone", "==", upline_phone.strip()).limit(1).stream()
        for doc in query:
            return True, doc.id
    return False, "Sponsor not found. Please check Upline ID or Phone."

def handle_successful_payment(user_id: str, quantity: int, total_price: float):
    """
    Triggers ONLY when payment gateway confirms payment.
    Creates an order history document and locks profile first_purchase_time forever.
    """
    current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    order_id = f"ORD-{int(time.time())}"
    
    # 1. Log the receipt into a separate collection
    db.collection("orders").document(order_id).set({
        "order_id": order_id,
        "member_id": user_id,
        "quantity": quantity,
        "total_amount": total_price,
        "payment_status": "Paid", # This updates to "Returned" if they refund
        "timestamp": current_time_str
    })
    
    # 2. Safely check and permanently stamp profile timestamp if empty
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        user_profile = user_doc.to_dict()
        if user_profile.get("first_purchase_time") == "No buy history":
            user_ref.update({"first_purchase_time": current_time_str})

# database.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        # Pull secret parameters dynamically
        firebase_dict = dict(st.secrets["firebase"])
        
        # FIX FOR NEWLINE CONFLICTS:
        # Ensures internal string data transforms escape codes cleanly
        if "private_key" in firebase_dict:
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
    else:
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

# database.py

def handle_successful_payment(user_id: str, quantity: int, total_price: float):
    """
    Triggers ONLY when payment gateway confirms success.
    Enforces a strict ONE-TIME reward cap for the 6-bottle free gift.
    """
    current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    order_id = f"ORD-{int(time.time())}"
    
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    free_bottles_reward = 0
    upline_linked = ""
    sponsor_phone = ""
    sponsor_name = ""
    buyer_name = "New Customer"
    
    if user_doc.exists:
        profile = user_doc.to_dict()
        upline_linked = profile.get("upline_id", "")
        buyer_name = profile.get("full_name", "Customer")
        
        # ====================================================================
        # ONE-TIME REWARD CHECK BLOCK
        # ====================================================================
        has_claimed_before = profile.get("free_gift_claimed", False)
        
        if quantity == 6 and upline_linked != "" and not has_claimed_before:
            free_bottles_reward = 1
            # Permanently update the flag so they can never abuse the promo slot
            user_ref.update({"free_gift_claimed": True})
            
            # Retrieve sponsor's profile numbers for network notifications
            sponsor_doc = db.collection("users").document(upline_linked).get()
            if sponsor_doc.exists:
                s_prof = sponsor_doc.to_dict()
                sponsor_phone = s_prof.get("phone", "")
                sponsor_name = s_prof.get("full_name", "")

    # 1. Log receipt manifest metadata down into Firestore
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
    
    # 2. Lock their conversion milestone timestamp if empty
    if user_doc.exists and user_doc.to_dict().get("first_purchase_time") == "No buy history":
        user_ref.update({"first_purchase_time": current_time_str})
        
    # ====================================================================
    # TRIGGER SYSTEM NOTIFICATION TRACKER
    # ====================================================================
    if upline_linked != "":
        trigger_sponsor_alert_notification(
            sponsor_name=sponsor_name,
            sponsor_phone=sponsor_phone,
            buyer_name=buyer_name,
            quantity=quantity,
            gift_awarded=free_bottles_reward
        )


def trigger_sponsor_alert_notification(sponsor_name: str, sponsor_phone: str, buyer_name: str, quantity: int, gift_awarded: int):
    """
    Simulates sending local Malaysian network server alerts via API (like Infobip or SMS Gateway).
    """
    st.markdown("---")
    st.subheader("📡 Central Notification Tracker System")
    
    sms_message = (
        f"Flantech Alert: Hello {sponsor_name}! Your sponsored customer {buyer_name} "
        f"has just placed a successful order of {quantity} bottles. "
    )
    if gift_awarded > 0:
        sms_message += "🎁 1 Introductory Free Bottle reward has been auto-dispatched to them!"
    else:
        sms_message += "Thank you for building your network distribution footprint."
        
    # Visual simulation container display on front-end
    st.info(f"📱 **Mock SMS sent to Sponsor ({sponsor_phone}):**\n\n*{sms_message}*")

# =====================================================================
# BOTTOM OF DATABASE.PY: CENTRAL NOTIFICATION TRACKER SYSTEM
# =====================================================================
def trigger_sponsor_alert_notification(sponsor_name: str, sponsor_phone: str, buyer_name: str, quantity: int, gift_awarded: int):
    """
    Simulates sending local Malaysian network server alerts via API (like Infobip or Gateway).
    """
    import streamlit as st
    st.markdown("---")
    st.subheader("📡 Central Notification Tracker System")
    
    sms_message = (
        f"Flantech Alert: Hello {sponsor_name}! Your sponsored customer {buyer_name} "
        f"has just placed a successful order of {quantity} bottles. "
    )
    if gift_awarded > 0:
        sms_message += "🎁 1 Introductory Free Bottle reward has been auto-dispatched to them!"
    else:
        sms_message += "Thank you for building your network distribution footprint."
        
    st.info(f"📱 **Mock SMS sent to Sponsor ({sponsor_phone}):**\n\n*{sms_message}*")

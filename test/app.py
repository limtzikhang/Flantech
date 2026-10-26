import streamlit as st
import urllib.parse

st.title("📦 Free WhatsApp Order Dispatcher")

# 1. Collect Customer Details
name = st.text_input("Customer Name")
phone = st.text_input("Customer Phone")
address = st.text_area("Delivery Address")
admin_phone = "60164191861" # <-- Put YOUR phone number here (Must start with 60, no + symbol, no spaces)

if st.button("Generate WhatsApp Shipping Alert"):
    if not name or not address:
        st.error("Please fill in the name and address.")
    else:
        # 2. Format the message text
        raw_message = (
            f"🚨 *NEW ORDER RECEIVED* 🚨\n\n"
            f"👤 *Customer:* {name}\n"
            f"📞 *Contact:* {phone}\n\n"
            f"📍 *Shipping Address:* \n{address}"
        )
        
        # 3. Convert spaces and characters into a safe web URL format
        encoded_message = urllib.parse.quote(raw_message)
        whatsapp_url = f"https://wa.me/{admin_phone}?text={encoded_message}"
        
        # 4. Display a clickable link button
        st.success("✨ Click the button below to send the details directly to your WhatsApp app!")
        st.link_button("📲 Click to Send to WhatsApp", whatsapp_url)

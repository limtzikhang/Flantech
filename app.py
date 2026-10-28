# app.py
import streamlit as st

# app.py - Add these inside your global session tracking section
if "cart" not in st.session_state:
    st.session_state.cart = {}  # Tracks product quantities selected by the user


# 1. Initialize persistent session memories
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# 2. Map file targets using the official st.Page architecture
login_page = st.Page("home_view.py", title="🔐 Sign In", icon="🔑", default=True)
signup_page = st.Page("signup_view.py", title="📝 Sign Up Form", icon="📋")
product_page = st.Page("product_view.py", title="🛍️ Product Showcase", icon="📦")
checkout_page = st.Page("checkout_view.py", title="🛒 Checkout Store", icon="💳")
admin_page = st.Page("admin_view.py", title="🛡️ Admin Control Center", icon="📊")

# 3. Dynamic logic configuration for the left pane sidebar links
if not st.session_state.logged_in:
    pages_to_display = [login_page, signup_page]
else:
    # Build list for authenticated profiles
    pages_to_display = [login_page, product_page, checkout_page]
    
    # Inject the Admin Dashboard into the top spot if verified
    if st.session_state.is_admin:
        pages_to_display.insert(0, admin_page)

# 4. Run the centralized navigation engine
selected_page = st.navigation(pages_to_display)
selected_page.run()

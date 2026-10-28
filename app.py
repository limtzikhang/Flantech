import streamlit as st

# Initialize Global Application Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =====================================================================
# 1. DEFINE YOUR SITE PAGES AS COMPONENT INSTANCES
# =====================================================================
login_page = st.Page("home_view.py", title="🔐 Sign In", icon="🔑", default=(not st.session_state.logged_in))
signup_page = st.Page("signup_view.py", title="📝 Sign Up Form", icon="📋")

profile_page = st.Page("home_view.py", title="👤 My Profile View", icon="👤", default=st.session_state.logged_in)
product_page = st.Page("product_view.py", title="🛍️ Product Showcase", icon="📦")
checkout_page = st.Page("checkout_view.py", title="🛒 Checkout Store", icon="💳")

# Secure Admin Page Instance
admin_page = st.Page("admin_view.py", title="🛡️ Admin Control Center", icon="📊")

# =====================================================================
# 2. DYNAMIC SIDEBAR GENERATION TREE
# =====================================================================
if not st.session_state.logged_in:
    # Public views visible before signing in
    pages_to_display = [login_page, signup_page]
else:
    # Build list dynamically for logged-in accounts
    pages_to_display = [profile_page, product_page, checkout_page]
    
    # SYSTEM AUDIT: Inject the Admin link only if the user is authenticated as an admin
    if st.session_state.is_admin:
        pages_to_display.insert(0, admin_page) # Pushes the Admin Panel to the top spot

# =====================================================================
# 3. EXECUTE STREAMLIT NAVIGATION CONTROLLER
# =====================================================================
# This one line handles the entire left pane automatically!
selected_page = st.navigation(pages_to_display)
selected_page.run()

# product_view.py
import streamlit as st

st.title("🛍️ Flantech Product Showcase")
st.markdown("Select your health optimization inventory below to load your checkout basket.")

# 1. Define the 2 primary products with baseline business context descriptions
PRODUCTS = {
    "PROD_001": {
        "name": "MegaHydrate Capsule Edition",
        "description": "Powerful antioxidant hydrator designed to boost cellular energy and optimize live blood profile parameters.",
        "image_placeholder": "🧪"
    },
    "PROD_002": {
        "name": "Flanagan Crystal Energy Drops",
        "description": "Elixir formulation engineered to lower the surface tension of drinking water for maximized nutrient absorption.",
        "image_placeholder": "💧"
    }
}

# Ensure cart states are available locally
if "cart" not in st.session_state:
    st.session_state.cart = {}

# 2. Render Products Side-by-Side in Grid Columns
col1, col2 = st.columns(2)

with col1:
    p1 = PRODUCTS["PROD_001"]
    st.subheader(f"{p1['image_placeholder']} {p1['name']}")
    st.write(p1['description'])
    st.caption("Standard Price: RM 248.00 / bottle (Wholesale bulk price available at checkout)")
    
    qty1 = st.number_input("Select Quantity", min_value=0, max_value=100, value=0, key="qty_prod_1")
    if st.button("Add to Checkout Basket", key="btn_prod_1"):
        st.session_state.cart["PROD_001"] = qty1
        st.success(f"Added {qty1} units of {p1['name']} to basket!")

with col2:
    p2 = PRODUCTS["PROD_002"]
    st.subheader(f"{p2['image_placeholder']} {p2['name']}")
    st.write(p2['description'])
    st.caption("Standard Price: RM 248.00 / bottle (Wholesale bulk price available at checkout)")
    
    qty2 = st.number_input("Select Quantity", min_value=0, max_value=100, value=0, key="qty_prod_2")
    if st.button("Add to Checkout Basket", key="btn_prod_2"):
        st.session_state.cart["PROD_002"] = qty2
        st.success(f"Added {qty2} units of {p2['name']} to basket!")

# 3. Dynamic Summary Alert Banner
total_items = sum(st.session_state.cart.values())
if total_items > 0:
    st.info(f"🛒 Your cart currently holds a total of **{total_items} bottles**. Head over to the **Checkout Store** in the left sidebar menu to process payment transactions.")

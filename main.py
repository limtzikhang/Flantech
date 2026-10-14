import streamlit as st

# Explicit multi-page definition mapping routing paths cleanly
pages = {
    "Flantech Network Menu": [
        st.Page("dashboard.py", title="🏠 Main Dashboard", default=True),
        st.Page("video_library.py", title="🎦 Video Library Portal")
    ]
}

# Run the navigation controller on a clean independent scope layer
pg = st.navigation(pages)
pg.run()

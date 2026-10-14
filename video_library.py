import streamlit as st
import os

# Set up wide page layout layout adjustments
st.set_page_config(
    page_title="Flantech Video Library",
    page_icon="🎦",
    layout="wide"
)

# =====================================================================
# MEDIA CONFIGURATION LAYER
# =====================================================================
# Maps your video display titles to the file paths stored back in the parent folder
# IMPORTANT: Since this script runs inside the 'pages' subfolder, we use '../filename'
# or let os.path find it in the parent workspace.
VIDEO_PLAYLIST = {
    "Megahydrate Blood Analysis Demonstration": "Megahydrate Live Blood Analysis.mp4",
    "Laboratory": "Dr Patrick Flanagan in his Laboratory.mp4",
    "Live Blood": "Use and Abuse of Live Blood Analysis.mp4",
}

# =====================================================================
# SIDEBAR PLAYLIST SELECTION DRAWER
# =====================================================================
with st.sidebar:
    st.markdown("## 📁 Media Playlist")
    st.caption("Select a video link below to load the player canvas.")
    st.write("---")
    
    selected_video_title = st.radio(
        label="Available Video Tracks:",
        options=list(VIDEO_PLAYLIST.keys()),
        index=0
    )
    st.write("---")

# =====================================================================
# MAIN VIDEO PLAYER CANVAS
# =====================================================================
st.title("🎦 Corporate Video Library Hub")
st.caption("Stream training tutorials and product demonstrations over the internet")
st.write("---")

target_filename = VIDEO_PLAYLIST[selected_video_title]

# Verify if the physical video data binary exists in your machine workspace
if os.path.exists(target_filename):
    st.subheader(f"🎥 Now Playing: {selected_video_title}")
    
    # Read the target layout binary stream data out from hard drive tracks
    with open(target_filename, "rb") as video_file:
        video_bytes = video_file.read()
    
    # Fire up the responsive Streamlit media playback engine array container
    st.video(video_bytes, format="video/mp4")
    st.success("✅ Streaming pipeline active. 5G internet connection clients can view this media smoothly.")
else:
    st.error(f"❌ File Not Found Error: Could not locate `{target_filename}`.")
    st.markdown(f"Please ensure the video file **`{target_filename}`** is placed directly in the main project folder.")

"""
Settings and preferences page.
"""

import streamlit as st
from app.frontend.styles import apply_custom_styling, create_header

# Apply styling
apply_custom_styling()

# Header
create_header(
    "Settings & Preferences",
    "Customize Your AyushEquityAI Experience",
    "⚙️"
)

st.markdown("### Display Preferences")

col1, col2 = st.columns(2)

with col1:
    theme = st.selectbox(
        "Theme",
        options=["Hospital Blue", "Light Mode", "Dark Mode"],
        key="theme_select"
    )
    
    st.info(f"✓ Current Theme: {theme}")

with col2:
    language = st.selectbox(
        "Language",
        options=["English", "Hindi", "Marathi"],
        key="lang_select"
    )
    
    st.info(f"✓ Current Language: {language}")

st.markdown("---")

st.markdown("### Notification Settings")

notify_claims = st.checkbox("High-priority claims notifications", value=True)
notify_fraud = st.checkbox("Fraud detection alerts", value=True)
notify_enrollment = st.checkbox("Enrollment drive updates", value=True)

st.markdown("---")

st.markdown("### System Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("App Version", "1.0.0")

with col2:
    st.metric("Last Updated", "Today")

with col3:
    st.metric("Status", "✓ Healthy")

st.markdown("---")

if st.button("Save Settings", use_container_width=True):
    st.success("✓ Settings saved successfully!")
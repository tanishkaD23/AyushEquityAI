"""
Main Hospital-Themed AyushEquityAI Application.
Premium, attractive, professional healthcare interface.
"""

import streamlit as st
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.frontend.app_hospital_theme import show_officer_dashboard, show_citizen_portal, show_analytics_dashboard
from app.frontend.styles import apply_custom_styling
from app.frontend.theme_config import COLORS

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="AyushEquityAI - Healthcare Excellence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "AyushEquityAI - AI-Powered Healthcare Inclusion & Fraud Detection Platform for Ayushman Bharat (PM-JAY). Version 1.0.0"
    }
)

# Apply custom styling
apply_custom_styling()

# === SIDEBAR ===
with st.sidebar:
    # Logo and branding with styling
    st.markdown(f"""
    <div style='text-align: center; padding: 20px 0; background: linear-gradient(180deg, {COLORS["primary_dark"]} 0%, {COLORS["primary"]} 100%); 
                border-radius: 12px; margin: -15px -15px 20px -15px; padding: 30px 15px;'>
        <h2 style='color: white; font-size: 2.5em; margin: 0;'>🏥</h2>
        <h3 style='color: white; margin: 10px 0 0 0; font-family: Poppins, sans-serif;'>AyushEquityAI</h3>
        <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 0.95em;'>Healthcare Excellence</p>
        <p style='color: rgba(255,255,255,0.7); margin: 10px 0 0 0; font-size: 0.85em;'>Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(0,0,0,0.1); margin: 15px 0;'>", unsafe_allow_html=True)
    
    # Role selection
    st.markdown("<p style='color: #0D47A1; font-weight: 700; margin-bottom: 15px; margin-top: 0;'>SELECT YOUR ROLE</p>", unsafe_allow_html=True)
    
    selected_role = st.radio(
        "Choose Dashboard",
        options=[
            "🏥 Officer Dashboard",
            "👨‍👩‍👧‍👦 Citizen Portal",
            "📊 Analytics & Compliance"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border: 1px solid rgba(0,0,0,0.1); margin: 15px 0;'>", unsafe_allow_html=True)
    
    # System info
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {COLORS["primary_lighter"]} 0%, {COLORS["secondary_lighter"]} 100%);
                padding: 15px; border-radius: 12px; margin-top: 20px; border-left: 4px solid {COLORS["primary"]};'>
        <p style='color: {COLORS["primary"]}; font-size: 0.85em; margin: 0; font-weight: 600;'>
            🟢 <strong>SYSTEM STATUS</strong>
        </p>
        <p style='color: {COLORS["dark"]}; font-size: 0.8em; margin: 8px 0 0 0;'>
            <strong>Health:</strong> Operational
        </p>
        <p style='color: {COLORS["dark"]}; font-size: 0.8em; margin: 5px 0;'>
            <strong>Version:</strong> 1.0.0
        </p>
        <p style='color: {COLORS["dark"]}; font-size: 0.8em; margin: 5px 0 0 0;'>
            <strong>Updated:</strong> Today
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(0,0,0,0.1); margin: 15px 0;'>", unsafe_allow_html=True)
    
    # Quick links
    st.markdown("<p style='color: #0D47A1; font-weight: 700; margin-bottom: 10px;'>QUICK LINKS</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔗 API Docs", use_container_width=True):
            st.info("API Documentation available at http://localhost:8000/docs")
    with col2:
        if st.button("📞 Support", use_container_width=True):
            st.info("Call 1800-AYUSH-1 for support")
    
    st.markdown("<hr style='border: 1px solid rgba(0,0,0,0.1); margin: 15px 0;'>", unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style='text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid rgba(0,0,0,0.1);'>
        <p style='color: {COLORS["gray"]}; font-size: 0.75em; margin: 0;'>
            <strong>AyushEquityAI v1.0.0</strong><br/>
            Healthcare Innovation<br/>
            2024
        </p>
    </div>
    """, unsafe_allow_html=True)


# === MAIN CONTENT ROUTING ===
if "🏥 Officer Dashboard" in selected_role:
    show_officer_dashboard()
elif "👨‍👩‍👧‍👦 Citizen Portal" in selected_role:
    show_citizen_portal()
else:
    show_analytics_dashboard()
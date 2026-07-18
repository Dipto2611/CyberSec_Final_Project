import sys
from pathlib import Path

import streamlit as st

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# Imports
# ==========================================================

from src.predictor import Predictor

from app.styles import load_css

from app.ui_helpers import (
    show_header,
    show_sidebar,
    show_enterprise_assessment,
    show_metric_cards,
    show_threat_indicators,
    show_recommendations,
    show_summary,
    show_download_button,
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Enterprise AI Security Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================================
# Load Theme
# ==========================================================

load_css()

# ==========================================================
# Predictor
# ==========================================================

predictor = Predictor()

# ==========================================================
# Sidebar
# ==========================================================

show_sidebar()

# ==========================================================
# Header
# ==========================================================

show_header()

# ==========================================================
# Input Section
# ==========================================================

st.subheader("📧 Email / Message Analysis")

user_input = st.text_area(
    "Paste the email or message below",
    height=240,
    placeholder="""
Example:

URGENT!

Your SBI account has been temporarily locked.

Verify immediately.

https://fake-bank.xyz
""",
)

analyze = st.button(
    "🔍 Analyze Message",
    type="primary",
    use_container_width=True,
)

st.divider()

# ==========================================================
# Main Logic
# ==========================================================

if analyze:

    if not user_input.strip():

        st.warning("⚠ Please enter a message first.")

    else:

        with st.spinner("Analyzing message..."):

            report = predictor.predict(user_input)

        st.success("✅ Analysis Completed")

        # ==========================================
        # Enterprise Assessment
        # ==========================================

        show_enterprise_assessment(report)

        st.divider()

        # ==========================================
        # Dashboard
        # ==========================================

        st.subheader("📊 Analysis Dashboard")

        show_metric_cards(report)

        st.divider()

        # ==========================================
        # Threat Intelligence
        # ==========================================

        left, right = st.columns(2)

        with left:

            show_threat_indicators(report)

        with right:

            show_recommendations(report)

        st.divider()

        # ==========================================
        # Executive Summary
        # ==========================================

        show_summary(report)

        st.divider()

        # ==========================================
        # Download Report
        # ==========================================

        show_download_button(report)

else:

    st.info(
        """
### 👋 Welcome

This platform uses Machine Learning and Explainable AI
to classify emails/messages into:

✅ Safe

⚠ Spam

🚨 Phishing

---

### Features

• Enterprise Risk Assessment

• Threat Intelligence

• Explainable AI

• Security Recommendations

• Executive Summary

• Downloadable Report

Paste a message above and click **Analyze Message**.
"""
    )
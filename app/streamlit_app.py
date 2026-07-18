import sys
from pathlib import Path

import streamlit as st

# =====================================================
# Add Project Root to Python Path
# =====================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predictor import Predictor

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="Enterprise AI Security Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# Hide Streamlit Branding
# =====================================================
hide_streamlit_style = """
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# =====================================================
# Load Predictor
# =====================================================
predictor = Predictor()

# =====================================================
# Sidebar
# =====================================================
with st.sidebar:

    st.title("🛡 Enterprise AI")

    st.markdown("---")

    st.success("System Status\n\nOnline")

    st.metric("Model", "Logistic Regression")
    st.metric("Classes", "3")
    st.metric("Threat Engine", "Active")
    st.metric("Version", "3.0")

    st.markdown("---")

    st.caption("Built With")

    st.write("• Python")
    st.write("• Scikit-Learn")
    st.write("• Streamlit")
    st.write("• NLP")
    st.write("• Explainable AI")

# =====================================================
# Header
# =====================================================
st.title("🛡️ Enterprise AI Security Center")

st.caption(
    "AI-Powered Phishing & Spam Detection Platform | "
    "Machine Learning + Explainable Threat Analysis"
)

st.divider()

# =====================================================
# Input Section
# =====================================================
st.subheader("📧 Email / Message Analysis")

user_input = st.text_area(
    "Paste the email or message below",
    height=240,
    placeholder="""
Example:

URGENT!

Verify your SBI account immediately.

https://fake-bank.xyz
"""
)

analyze = st.button(
    "🔍 Analyze Message",
    use_container_width=True,
    type="primary"
)

st.divider()

# =====================================================
# Main Logic
# =====================================================
if analyze:

    if not user_input.strip():

        st.warning("⚠ Please enter a message first.")

    else:

        with st.spinner("Analyzing message..."):

            report = predictor.predict(user_input)

        prediction = report["prediction"]
        confidence = report["confidence"]
        risk_score = report["risk_score"]
        threat_level = report["threat_level"]
        indicators = report["detected_indicators"]
        recommendations = report["recommendations"]
        summary = report["summary"]

        st.success("✅ Analysis Completed")

        # =====================================================
        # Dashboard
        # =====================================================
        st.markdown("## 📊 Analysis Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        # Prediction
        with col1:
            st.metric(
                label="Prediction",
                value=prediction
            )

        # Confidence
        with col2:
            st.metric(
                label="Confidence",
                value=f"{confidence:.2f}%"
            )

        # Threat Level
        with col3:

            color = {
                "LOW": "🟢",
                "MEDIUM": "🟡",
                "HIGH": "🔴",
                "CRITICAL": "🚨"
            }.get(threat_level, "⚪")

            st.metric(
                label="Threat Level",
                value=f"{color} {threat_level}"
            )

        # Risk Score
        with col4:
            st.metric(
                label="Risk Score",
                value=f"{risk_score}/100"
            )

        st.divider()

        # =====================================================
        # Threat Intelligence
        # =====================================================
        left, right = st.columns(2)

        # Threat Indicators
        with left:

            st.subheader("🚨 Threat Indicators")

            if indicators:

                for item in indicators:
                    st.markdown(f"✅ {item}")

            else:
                st.success("No suspicious indicators detected.")

        # Recommendations
        with right:

            st.subheader("🛡️ Security Recommendations")

            for item in recommendations:
                st.markdown(f"• {item}")

        st.divider()

        # =====================================================
        # Executive Summary
        # =====================================================
        st.subheader("📄 Executive Summary")

        st.success(summary)

        st.download_button(
            label="📄 Download Analysis Report",
            data=str(report),
            file_name="analysis_report.txt",
            mime="text/plain",
            use_container_width=True
        )

else:

    st.info("Enter a message above and click **Analyze Message**.")
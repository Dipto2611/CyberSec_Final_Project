import streamlit as st
import os
from app.pdf_generator import generate_pdf


# ==========================================================
# HEADER
# ==========================================================

def show_header():

    st.title("🛡 Enterprise AI Security Center")

    st.caption(
        "AI-Powered Phishing & Spam Detection Platform | "
        "Machine Learning + Explainable Threat Analysis"
    )

    st.divider()


# ==========================================================
# SIDEBAR
# ==========================================================

def show_sidebar():

    with st.sidebar:

        st.title("🛡 Enterprise AI")

        st.divider()

        st.success("🟢 System Online")

        st.metric("Model", "Logistic Regression")

        st.metric("Classes", "3")

        st.metric("Threat Engine", "Active")

        st.metric("Version", "4.2")

        st.divider()

        st.markdown("### Built With")

        st.write("• Python")

        st.write("• Scikit-Learn")

        st.write("• Streamlit")

        st.write("• NLP")

        st.write("• Explainable AI")


# ==========================================================
# ENTERPRISE ASSESSMENT
# ==========================================================

def show_enterprise_assessment(report):

    severity = report["severity"]

    title = report["final_assessment"]

    message = report["assessment_message"]


    st.subheader("🛡 Enterprise Security Assessment")


    if severity == "LOW":

        st.success(title)

    elif severity == "MEDIUM":

        st.warning(title)

    elif severity == "HIGH":

        st.error(title)

    else:

        st.error(title)


    st.info(message)


# ==========================================================
# METRIC CARDS
# ==========================================================

def show_metric_cards(report):

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(

            label="Prediction",

            value=report["prediction"]

        )


    with col2:

        st.metric(

            label="Confidence",

            value=f"{float(report['confidence']):.2f}%"

        )

        st.progress(report["confidence"]/100)


    with col3:

        st.metric(

            label="Risk Score",

            value=f"{report['risk_score']}/100"

        )


    with col4:

        st.metric(

            label="Threat Level",

            value=report["threat_level"]

        )


# ==========================================================
# THREAT INDICATORS
# ==========================================================

def show_threat_indicators(report):

    st.subheader("🚨 Threat Indicators")

    indicators = report.get("detected_indicators", [])


    if not indicators:

        st.success("No suspicious indicators detected.")

        return


    for indicator in indicators:

        st.success(indicator)


# ==========================================================
# RECOMMENDATIONS
# ==========================================================

def show_recommendations(report):

    st.subheader("🛡 Security Recommendations")

    recommendations = report.get("recommendations", [])


    if not recommendations:

        st.info("No recommendations available.")

        return


    for item in recommendations:

        st.info(item)


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def show_summary(report):

    st.subheader("📄 Executive Summary")

    with st.container(border=True):

        st.markdown(
        f"""
        **Assessment:** {report['final_assessment']}

        **Severity:** {report['severity']}

        **Threat Level:** {report['threat_level']}

        ---

        {report['summary']}
        """
)


# ==========================================================
# DOWNLOAD BUTTON
# ==========================================================

def show_download_button(report):

    filename = "Enterprise_AI_Report.pdf"

    try:

        generate_pdf(report, filename)

        with open(filename, "rb") as pdf:

            pdf_bytes = pdf.read()

        st.download_button(

            label="📄 Download Enterprise PDF Report",

            data=pdf_bytes,

            file_name=filename,

            mime="application/pdf",

            use_container_width=True,

        )

    except Exception as e:

        st.error(f"PDF Generation Failed: {e}")

    finally:

        if os.path.exists(filename):

            os.remove(filename)
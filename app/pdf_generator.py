"""
==========================================================
Enterprise AI Security Report Generator
==========================================================

Generates a professional one-page PDF report for the
Enterprise AI-Powered Phishing & Spam Detection System.

Author : Enterprise AI Project
"""

from io import BytesIO
from datetime import datetime

import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

styles = getSampleStyleSheet()


# ==========================================================
# COLORS
# ==========================================================

PRIMARY = colors.HexColor("#1E3A8A")
SUCCESS = colors.HexColor("#16A34A")
WARNING = colors.HexColor("#D97706")
DANGER = colors.HexColor("#DC2626")
LIGHT = colors.HexColor("#F3F4F6")
TEXT = colors.HexColor("#1F2937")


# ==========================================================
# TITLE
# ==========================================================

title_style = styles["Title"]
title_style.alignment = TA_CENTER
title_style.textColor = PRIMARY

heading_style = styles["Heading2"]
heading_style.textColor = PRIMARY

normal_style = styles["BodyText"]
normal_style.leading = 14

small_style = styles["Normal"]
small_style.fontSize = 9
small_style.leading = 12


# ==========================================================
# HEADER
# ==========================================================

def build_header(story):

    story.append(
        Paragraph(
            "<u><b>Enterprise AI Security Assessment Report</b></u>",
            title_style
        )
    )
    story.append(Spacer(1, 0.12 * inch))
    # story.append(
    #     Paragraph(
    #         datetime.now().strftime(
    #             "Generated : %d %B %Y  %I:%M %p"
    #         ),
    #         small_style,
    #     )
    # )
    story.append(
    Paragraph(
        f"<b>Generated: {datetime.now().strftime('%d %B %Y  %I:%M %p')}</b>",
        small_style,
    )
)

    story.append(Spacer(1, 0.10 * inch))


# ==========================================================
# METRICS TABLE
# ==========================================================

def build_metrics(report):

    data = [

        ["Prediction", report["prediction"]],

        ["Confidence",
         f'{float(report["confidence"]):.2f}%'],

        ["Risk Score",
         f'{report["risk_score"]}/100'],

        ["Threat Level",
         report["threat_level"]],

        ["Severity",
         report["severity"]],

        ["Final Assessment",
         report["final_assessment"]]

    ]

    table = Table(
        data,
        colWidths=[2.2 * inch, 4.0 * inch]
    )

    table.setStyle(

        TableStyle([

            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

            ("BACKGROUND",(0,0),(0,-1),PRIMARY),

            ("TEXTCOLOR",(0,0),(0,-1),colors.white),

            ("BACKGROUND",(1,0),(1,-1),LIGHT),

            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8),

            ("ALIGN",(0,0),(-1,-1),"CENTER")

        ])
    )

    return table


# ==========================================================
# DONUT CHART
# ==========================================================

def create_probability_chart(report):

    probabilities = report["class_probabilities"]

    labels = list(probabilities.keys())
    values = list(probabilities.values())

    combined = sorted(
    zip(labels, values),
    key=lambda x: x[1],
    reverse=True
    )

    labels, values = zip(*combined)

    labels = list(labels)
    values = list(values)
    
    fig, ax = plt.subplots(figsize=(6, 2.4))

    bars = ax.barh(
        labels,
        values,
        height=0.55
    )

    # Color each class
    colors = [
        "#22C55E",   # Safe
        "#F59E0B",   # Spam
        "#EF4444"    # Phishing
    ]

    for bar, color in zip(bars, colors):
        bar.set_color(color)

    # Write percentage at end of each bar
    for i, value in enumerate(values):
        ax.text(
            value + 1,
            i,
            f"{value:.2f}%",
            va="center",
            fontsize=10,
            fontweight="bold"
        )

    ax.set_xlim(0, 100)

    ax.set_xlabel("Probability (%)", fontsize=10)

    ax.set_title(
        "Prediction Probability Distribution",
        fontsize=13,
        fontweight="bold"
    )

    ax.grid(axis="x", linestyle="--", alpha=0.35)

    plt.tight_layout()

    buffer = BytesIO()

    plt.savefig(
        buffer,
        format="png",
        dpi=220,
        bbox_inches="tight"
    )

    plt.close(fig)

    buffer.seek(0)

    return Image(
        buffer,
        width=6.2 * inch,
        height=2.4 * inch
    )
# ==========================================================
# RISK METER
# ==========================================================

def create_risk_meter(report):

    score = report["risk_score"]

    fig, ax = plt.subplots(figsize=(6.5, 0.8))

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)

    ax.barh(
        0.5,
        25,
        left=0,
        color="#22C55E",
        height=0.35,
    )

    ax.barh(
        0.5,
        25,
        left=25,
        color="#FACC15",
        height=0.35,
    )

    ax.barh(
        0.5,
        25,
        left=50,
        color="#F97316",
        height=0.35,
    )

    ax.barh(
        0.5,
        25,
        left=75,
        color="#DC2626",
        height=0.35,
    )

    ax.plot(
        score,
        0.5,
        marker="v",
        markersize=12,
        color="black",
    )

    ax.text(
        0,
        0.05,
        "LOW",
        fontsize=8,
        ha="left",
    )

    ax.text(
        25,
        0.05,
        "MEDIUM",
        fontsize=8,
        ha="center",
    )

    ax.text(
        50,
        0.05,
        "HIGH",
        fontsize=8,
        ha="center",
    )

    ax.text(
        100,
        0.05,
        "CRITICAL",
        fontsize=8,
        ha="right",
    )

    ax.set_title("Enterprise Risk Meter")

    ax.axis("off")

    buffer = BytesIO()

    plt.tight_layout()

    plt.savefig(
        buffer,
        format="png",
        dpi=220,
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return Image(
        buffer,
        width=6.1 * inch,
        height=0.65 * inch,
    )


# ==========================================================
# THREAT INDICATORS
# ==========================================================

def build_threat_indicators(report):

    story = []

    story.append(
        Paragraph(
            "<b>Threat Indicators</b>",
            heading_style,
        )
    )

    indicators = report.get(
        "detected_indicators",
        [],
    )

    if not indicators:

        story.append(
            Paragraph(
                "• No suspicious indicators detected.",
                normal_style,
            )
        )

    else:

        for item in indicators:

            story.append(
                Paragraph(
                    f"• {item}",
                    normal_style,
                )
            )

    story.append(
        Spacer(1, 0.10 * inch)
    )

    return story


# ==========================================================
# RECOMMENDATIONS
# ==========================================================

def build_recommendations(report):

    story = []

    story.append(
        Paragraph(
            "<b>Recommendations</b>",
            heading_style,
        )
    )

    recommendations = report.get(
        "recommendations",
        [],
    )

    for item in recommendations:

        story.append(
            Paragraph(
                f"• {item}",
                normal_style,
            )
        )

    story.append(
        Spacer(1, 0.10 * inch)
    )

    return story


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def build_summary(report):

    story = []

    story.append(
        Paragraph(
            "<b>Executive Summary</b>",
            heading_style,
        )
    )

    summary = f"""
    <b>Assessment:</b> {report['final_assessment']}<br/><br/>

    <b>Severity:</b> {report['severity']}<br/>
    <b>Threat Level:</b> {report['threat_level']}<br/>
    <b>Confidence:</b> {float(report['confidence']):.2f}%<br/><br/>

    {report['assessment_message']}<br/><br/>

    <b>Threat Summary:</b><br/>
    {report['summary']}
    """

    story.append(
        Paragraph(
            summary,
            normal_style,
        )
    )

    story.append(
        Spacer(1, 0.12 * inch)
    )

    return story

# ==========================================================
# FOOTER
# ==========================================================

def build_footer(story):

    story.append(
        Spacer(1, 0.15 * inch)
    )

    # story.append(
    #     Paragraph(
    #         "<font size='9' color='grey'>"
    #         "Generated by Enterprise AI-Powered Phishing & Spam Detection System"
    #         "<br/>"
    #         "This report is automatically generated using Machine Learning "
    #         "and Rule-Based Threat Intelligence."
    #         "</font>",
    #         small_style,
    #     )
    # )


# ==========================================================
# MAIN PDF GENERATOR
# ==========================================================

def generate_pdf(report, output_path):

    doc = SimpleDocTemplate(

        output_path,

        pagesize=(8.27 * inch, 11.69 * inch),

        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,

        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch

    )

    story = []

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    build_header(story)

    # --------------------------------------------------
    # METRICS TABLE
    # --------------------------------------------------

    story.append(
        build_metrics(report)
    )

    story.append(
        Spacer(1, 0.10 * inch)
    )

    # --------------------------------------------------
    # DONUT CHART
    # --------------------------------------------------

    story.append(
        create_probability_chart(report)
    )

    story.append(
        Spacer(1, 0.10 * inch)
    )

    # --------------------------------------------------
    # RISK METER
    # --------------------------------------------------

    story.append(
        create_risk_meter(report)
    )

    story.append(
        Spacer(1, 0.10 * inch)
    )

    # --------------------------------------------------
    # THREAT INDICATORS
    # --------------------------------------------------

    story.extend(
        build_threat_indicators(report)
    )

    # --------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------

    story.extend(
        build_recommendations(report)
    )

    # --------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------

    story.extend(
        build_summary(report)
    )
    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    build_footer(story)

    # --------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------

    doc.build(story)

    return output_path


# ==========================================================
# OPTIONAL TEST
# ==========================================================

if __name__ == "__main__":

    sample_report = {
        "prediction": "Phishing",
        "confidence": 97.81,
        "risk_score": 78,
        "threat_level": "HIGH",
        "severity": "HIGH",
        "final_assessment": "High Confidence Threat",
        "assessment_message": (
            "Both the AI model and Threat Intelligence engine "
            "indicate this message is highly suspicious."
        ),
        "summary": (
            "Multiple phishing indicators were detected. "
            "Avoid interacting with this message."
        ),
        "detected_indicators": [
            "Suspicious URL detected",
            "Credential request detected",
            "Urgent language detected",
        ],
        "recommendations": [
            "Do not click links in the message.",
            "Verify the sender using official channels.",
            "Never share passwords, OTPs, or PINs.",
        ],
        "class_probabilities": {
            "Safe": 1.25,
            "Phishing": 97.81,
            "Spam": 0.94,
        },
    }

    output_file = "Enterprise_AI_Security_Report.pdf"

    generate_pdf(sample_report, output_file)

    print(f"PDF generated successfully: {output_file}")
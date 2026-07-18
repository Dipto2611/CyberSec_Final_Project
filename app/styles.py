import streamlit as st


def load_css():

    st.markdown("""
<style>

/* ===========================
   GLOBAL
=========================== */

.stApp{

    background:#0d1117;

    color:#e6edf3;

    font-family:"Segoe UI",sans-serif;

}

/* ===========================
   HIDE STREAMLIT
=========================== */

#MainMenu{

    visibility:hidden;

}

header{

    visibility:hidden;

}

footer{

    visibility:hidden;

}

/* ===========================
   SIDEBAR
=========================== */

[data-testid="stSidebar"]{

    background:#161b22;

    border-right:1px solid #30363d;

}

/* ===========================
   BUTTONS
=========================== */

.stButton>button{

    width:100%;

    height:50px;

    border-radius:12px;

    font-size:17px;

    font-weight:700;

}

/* ===========================
   TEXT AREA
=========================== */

textarea{

    border-radius:12px !important;

    background:#161b22 !important;

    color:white !important;

    border:1px solid #30363d !important;

}

/* ===========================
   METRIC CARDS
=========================== */

[data-testid="metric-container"]{

    background:#161b22;

    border:1px solid #30363d;

    border-radius:14px;

    padding:15px;

}

[data-testid="metric-container"]:hover{

    border-color:#58a6ff;

}

/* ===========================
   SUCCESS
=========================== */

[data-testid="stSuccess"]{

    border-radius:12px;

}

/* ===========================
   INFO
=========================== */

[data-testid="stInfo"]{

    border-radius:12px;

}

/* ===========================
   WARNING
=========================== */

[data-testid="stWarning"]{

    border-radius:12px;

}

/* ===========================
   ERROR
=========================== */

[data-testid="stError"]{

    border-radius:12px;

}

/* ===========================
   CONTAINERS
=========================== */

[data-testid="stVerticalBlockBorderWrapper"]{

    border-radius:14px;

}

/* ===========================
   SCROLLBAR
=========================== */

::-webkit-scrollbar{

    width:10px;

}

::-webkit-scrollbar-track{

    background:#161b22;

}

::-webkit-scrollbar-thumb{

    background:#30363d;

    border-radius:8px;

}

::-webkit-scrollbar-thumb:hover{

    background:#58a6ff;

}

</style>
""", unsafe_allow_html=True)
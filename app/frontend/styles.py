"""
Custom CSS and styling for hospital-themed UI.
"""

import streamlit as st
from app.frontend.theme_config import COLORS, FONTS, SPACING, SHADOWS, BORDER_RADIUS


def apply_custom_styling():
    """Apply custom CSS styling to the entire app."""
    
    custom_css = f"""
    <style>
        /* === ROOT STYLES === */
        :root {{
            --primary: {COLORS['primary']};
            --primary-light: {COLORS['primary_light']};
            --primary-lighter: {COLORS['primary_lighter']};
            --secondary: {COLORS['secondary']};
            --secondary-light: {COLORS['secondary_light']};
            --success: {COLORS['success']};
            --warning: {COLORS['warning']};
            --danger: {COLORS['danger']};
            --info: {COLORS['info']};
            --white: {COLORS['white']};
            --light: {COLORS['light']};
            --gray: {COLORS['gray']};
            --dark: {COLORS['dark']};
            --border: {COLORS['border']};
        }}

        /* === GLOBAL STYLES === */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            font-family: {FONTS['primary']};
            color: var(--dark);
            background-color: var(--light);
            line-height: 1.6;
        }}

        /* === SCROLLBAR === */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--light);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--primary);
            border-radius: {BORDER_RADIUS['md']};
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--primary-light);
        }}

        /* === MAIN CONTAINER === */
        .main {{
            padding: 0 !important;
        }}

        .stApp {{
            background-color: var(--light);
        }}

        /* === HEADER === */
        .header-container {{
            background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 100%);
            color: white;
            padding: {SPACING['xl']} {SPACING['lg']};
            margin: -2rem -1.5rem 2rem -1.5rem;
            border-bottom: 4px solid {COLORS['secondary']};
            box-shadow: {SHADOWS['lg']};
            animation: slideDown 0.5s ease-out;
        }}

        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .header-container h1 {{
            font-family: {FONTS['heading']};
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: {SPACING['sm']};
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .header-container p {{
            font-size: 1.1em;
            opacity: 0.95;
            font-weight: 300;
        }}

        /* === METRIC CARDS === */
        .metric-card {{
            background: white;
            border-radius: {BORDER_RADIUS['lg']};
            padding: {SPACING['lg']};
            box-shadow: {SHADOWS['md']};
            border-left: 4px solid var(--primary);
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease-out;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: {SHADOWS['xl']};
        }}

        .metric-card.success {{
            border-left-color: var(--success);
        }}

        .metric-card.warning {{
            border-left-color: var(--warning);
        }}

        .metric-card.danger {{
            border-left-color: var(--danger);
        }}

        .metric-card.info {{
            border-left-color: var(--info);
        }}

        .metric-label {{
            font-size: 0.9em;
            color: var(--gray);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: {SPACING['sm']};
        }}

        .metric-value {{
            font-family: {FONTS['heading']};
            font-size: 2em;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: {SPACING['xs']};
        }}

        .metric-delta {{
            font-size: 0.85em;
            color: var(--success);
            font-weight: 600;
        }}

        .metric-delta.negative {{
            color: var(--danger);
        }}

        /* === BUTTON STYLES === */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS['md']};
            padding: {SPACING['sm']} {SPACING['lg']};
            font-weight: 600;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: {SHADOWS['md']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: {SHADOWS['lg']};
        }}

        .stButton > button:active {{
            transform: translateY(0);
        }}

        /* === TAB STYLES === */
        .stTabs {{
            margin-bottom: {SPACING['lg']};
        }}

        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent;
            border-bottom: 2px solid var(--border);
            gap: {SPACING['lg']};
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            border-radius: 0;
            padding: {SPACING['md']} {SPACING['lg']};
            color: var(--gray);
            border-bottom: 3px solid transparent;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .stTabs [aria-selected="true"] {{
            color: var(--primary);
            border-bottom-color: var(--primary);
            background-color: transparent;
        }}

        /* === INFO BOXES === */
        .info-box {{
            background: var(--primary-lighter);
            border-left: 4px solid var(--primary);
            padding: {SPACING['lg']};
            border-radius: {BORDER_RADIUS['md']};
            margin: {SPACING['lg']} 0;
        }}

        .success-box {{
            background: #E8F5E9;
            border-left-color: var(--success);
        }}

        .warning-box {{
            background: #FFF3E0;
            border-left-color: var(--warning);
        }}

        .danger-box {{
            background: #FFEBEE;
            border-left-color: var(--danger);
        }}

        /* === DATAFRAME STYLES === */
        .dataframe {{
            font-size: 0.95em !important;
            border-collapse: collapse !important;
        }}

        .dataframe thead {{
            background: var(--primary) !important;
            color: white !important;
        }}

        .dataframe tbody tr:nth-child(even) {{
            background-color: var(--lighter) !important;
        }}

        .dataframe tbody tr:hover {{
            background-color: var(--primary-lighter) !important;
            transition: background-color 0.2s ease;
        }}

        /* === SIDEBAR === */
        .sidebar .sidebar-content {{
            background: linear-gradient(180deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 100%);
        }}

        section[data-testid="stSidebar"] {{
            background: var(--primary);
            color: white;
        }}

        section[data-testid="stSidebar"] .stRadio > label {{
            color: white;
            padding: {SPACING['md']};
            border-radius: {BORDER_RADIUS['md']};
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        section[data-testid="stSidebar"] .stRadio > label:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}

        /* === EXPANDER === */
        .streamlit-expanderHeader {{
            background-color: var(--primary-lighter);
            border-radius: {BORDER_RADIUS['md']};
            padding: {SPACING['md']};
        }}

        .streamlit-expanderHeader:hover {{
            background-color: var(--primary-lighter);
        }}

        /* === DIVIDER === */
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--border), transparent);
            margin: {SPACING['xl']} 0;
        }}

        /* === HEADINGS === */
        h1, h2, h3 {{
            font-family: {FONTS['heading']};
            font-weight: 700;
            color: var(--primary);
            margin-top: {SPACING['lg']};
            margin-bottom: {SPACING['md']};
        }}

        h1 {{
            font-size: 2.2em;
            border-bottom: 3px solid var(--secondary);
            padding-bottom: {SPACING['md']};
        }}

        h2 {{
            font-size: 1.8em;
        }}

        h3 {{
            font-size: 1.4em;
            color: var(--primary-dark);
        }}

        /* === LINKS === */
        a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
        }}

        a:hover {{
            border-bottom-color: var(--primary);
            color: var(--primary-light);
        }}

        /* === SELECTBOX === */
        .stSelectbox {{
            margin-bottom: {SPACING['md']};
        }}

        /* === ANIMATIONS === */
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.7;
            }}
        }}

        .pulse {{
            animation: pulse 2s ease-in-out infinite;
        }}

        @keyframes glow {{
            0%, 100% {{
                box-shadow: {SHADOWS['md']};
            }}
            50% {{
                box-shadow: {SHADOWS['xl']};
            }}
        }}

        .glow {{
            animation: glow 2s ease-in-out infinite;
        }}

        /* === RESPONSIVE === */
        @media (max-width: 768px) {{
            .header-container h1 {{
                font-size: 1.8em;
            }}

            .metric-card {{
                margin-bottom: {SPACING['lg']};
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: {SPACING['md']};
            }}
        }}
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)


def create_metric_card(label, value, delta=None, delta_type="positive", card_type="default"):
    """
    Create a styled metric card.
    
    Args:
        label (str): Metric label
        value (str): Metric value
        delta (str, optional): Change indicator
        delta_type (str): "positive", "negative", or "neutral"
        card_type (str): "default", "success", "warning", "danger", "info"
    """
    
    delta_html = ""
    if delta:
        delta_class = "metric-delta" if delta_type == "positive" else "metric-delta negative"
        delta_html = f'<div class="{delta_class}">{delta}</div>'
    
    card_html = f"""
    <div class="metric-card {card_type}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    
    return st.markdown(card_html, unsafe_allow_html=True)


def create_info_box(content, box_type="info", title=None):
    """
    Create a styled info box.
    
    Args:
        content (str): Box content
        box_type (str): "info", "success", "warning", "danger"
        title (str, optional): Box title
    """
    
    title_html = f"<strong style='color: var(--primary);'>{title}</strong><br/>" if title else ""
    
    box_html = f"""
    <div class="info-box {box_type}-box">
        {title_html}
        {content}
    </div>
    """
    
    return st.markdown(box_html, unsafe_allow_html=True)


def create_header(title, subtitle=None, emoji=None):
    """
    Create a styled header section.
    
    Args:
        title (str): Header title
        subtitle (str, optional): Header subtitle
        emoji (str, optional): Header emoji
    """
    
    emoji_html = f"<span style='font-size: 2.5em; margin-right: 10px;'>{emoji}</span>" if emoji else ""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    
    header_html = f"""
    <div class="header-container">
        <h1>{emoji_html}{title}</h1>
        {subtitle_html}
    </div>
    """
    
    return st.markdown(header_html, unsafe_allow_html=True)
def apply_custom_styling():
    st.markdown("""
    <style>

    .stApp{
        background: linear-gradient(
            135deg,
            #020B1F 0%,
            #001F54 30%,
            #0038A8 65%,
            #00A8FF 100%
        );
    }
                .metric-card{
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(0,229,255,0.4);
    border-radius:20px;
    padding:20px;
    box-shadow:0 0 30px rgba(0,229,255,0.25);
    transition:0.3s;
}

.metric-card:hover{
    transform:translateY(-5px);
    box-shadow:0 0 40px rgba(0,229,255,0.5);
}
                background: linear-gradient(90deg,#0057FF,#00E5FF);
color:white;
box-shadow:0 0 20px rgba(0,229,255,.6);

    </style>
    """, unsafe_allow_html=True)

    
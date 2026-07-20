"""
Hospital-themed design system configuration.
Defines colors, fonts, spacing, and visual styling.
"""

# Hospital Theme Color Palette
# ===== Neon Blue Theme =====

COLORS = {

    # Primary Neon Blues
    "primary_dark": "#001F54",
    "primary": "#0057FF",
    "primary_light": "#00A8FF",
    "primary_lighter": "#EAF8FF",

    # Neon Accent
    "secondary": "#00E5FF",
    "secondary_light": "#66F7FF",
    "secondary_lighter": "#E0FCFF",

    # Status
    "success": "#00E676",
    "warning": "#FFB300",
    "danger": "#FF1744",
    "info": "#00E5FF",

    # Background
    "white": "#FFFFFF",
    "light": "#F5FAFF",
    "lighter": "#FBFDFF",
    "gray": "#90A4AE",
    "dark": "#0A192F",
    "border": "#D6EFFF",

    # Neon Gradients
    "gradient_blue": "linear-gradient(135deg, #001F54 0%, #0057FF 50%, #00E5FF 100%)",

    "gradient_dark": "linear-gradient(135deg, #020B1F 0%, #001F54 100%)",

    "gradient_card": "linear-gradient(135deg, rgba(0,87,255,0.15) 0%, rgba(0,229,255,0.08) 100%)",

    "gradient_glow": "linear-gradient(135deg, #0057FF 0%, #00E5FF 100%)",
}

# Typography
FONTS = {
    "primary": "Segoe UI, -apple-system, sans-serif",
    "heading": "'Poppins', 'Segoe UI', sans-serif",
    "mono": "'Courier New', monospace",
}

# Spacing (in pixels)
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "xxl": "48px",
}

# Border radius
BORDER_RADIUS = {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "full": "9999px",
}

# Shadows (Material Design)
SHADOWS = {
    "sm": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
    "md": "0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12)",
    "lg": "0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)",
    "xl": "0 15px 35px rgba(0,0,0,0.2), 0 3px 6px rgba(0,0,0,0.1)",
}

# Icon sizes
ICON_SIZES = {
    "sm": 16,
    "md": 24,
    "lg": 32,
    "xl": 48,
    "xxl": 64,
}
"""
PlacementIQ Theme & Design System
Matches the dark neon pink / futuristic SaaS aesthetic from the reference design.
"""

class Theme:
    # Core background & surfaces
    BG_DARK = "#0B0B12"          # Deep charcoal / near-black main window
    SIDEBAR_BG = "#111119"       # Matte black sidebar
    CARD_BG = "#171723"          # Dark charcoal card surface
    CARD_BG_ALT = "#1E1E2E"      # Elevated card / inner element
    CARD_BORDER = "#2A293D"      # Subtle card border
    CARD_BORDER_ACTIVE = "#E83D84"# Active/selected card neon border

    # Gradient stops for hero banner & special cards
    GRADIENT_HERO_START = "#FFA256"   # Warm peach sunset
    GRADIENT_HERO_MID = "#E83D84"     # Vibrant neon pink / magenta
    GRADIENT_HERO_END = "#9B51E0"     # Electric violet

    GRADIENT_PURPLE_START = "#B84BF5"
    GRADIENT_PURPLE_END = "#E83D84"

    # Accent Colors
    ACCENT_PINK = "#FF2E93"      # Neon Pink / Magenta primary accent
    ACCENT_PINK_HOVER = "#FF4DA3"# Lighter pink on hover
    ACCENT_PURPLE = "#A855F7"    # Soft electric purple
    ACCENT_LAVENDER = "#C4B5FD"  # Muted lavender
    ACCENT_ORANGE = "#FF9F43"    # Warm orange
    ACCENT_CYAN = "#00D2FF"      # Cyan highlight

    # Status / Signal Colors
    COLOR_SUCCESS = "#00E096"    # Vibrant emerald ("Good Fit", "Selected")
    COLOR_WARNING = "#FFB300"    # Amber / Assessment
    COLOR_INFO = "#38BDF8"       # Sky blue / Applied
    COLOR_DANGER = "#FF4B6E"     # Crimson red / Ineligible / Rejected
    COLOR_PURPLE = "#C084FC"     # Interview stage

    # Typography / Text Colors
    TEXT_WHITE = "#FFFFFF"       # Bright white headers
    TEXT_LIGHT = "#E2E8F0"       # Primary text
    TEXT_MUTED = "#94A3B8"       # Secondary labels
    TEXT_SUBTLE = "#64748B"      # Captions & hint text
    TEXT_DARK = "#0F172A"        # Dark text for bright gradient surfaces

    # Inputs & Controls
    INPUT_BG = "#141420"
    INPUT_BORDER = "#2B2A3E"
    INPUT_BORDER_FOCUS = "#FF2E93"

    # Badges & Indicators
    BADGE_BG_GREEN = "#053321"
    BADGE_BORDER_GREEN = "#00E096"
    BADGE_TEXT_GREEN = "#34D399"

    BADGE_BG_PINK = "#3B1124"
    BADGE_BORDER_PINK = "#FF2E93"
    BADGE_TEXT_PINK = "#FF66B2"

    BADGE_BG_PURPLE = "#281747"
    BADGE_BORDER_PURPLE = "#A855F7"
    BADGE_TEXT_PURPLE = "#C084FC"

    BADGE_BG_ORANGE = "#3D240E"
    BADGE_BORDER_ORANGE = "#FF9F43"
    BADGE_TEXT_ORANGE = "#FDBA74"

    # Fonts (Windows Segoe UI family)
    FONT_TITLE_XL = ("Segoe UI", 20, "bold")
    FONT_TITLE_LARGE = ("Segoe UI", 16, "bold")
    FONT_TITLE_MED = ("Segoe UI", 13, "bold")
    FONT_HEADING = ("Segoe UI", 11, "bold")
    FONT_BODY = ("Segoe UI", 10)
    FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
    FONT_SMALL = ("Segoe UI", 9)
    FONT_SMALL_BOLD = ("Segoe UI", 9, "bold")
    FONT_TINY = ("Segoe UI", 8)
    FONT_NUMBER_HERO = ("Segoe UI", 24, "bold")
    FONT_NUMBER_MED = ("Segoe UI", 16, "bold")

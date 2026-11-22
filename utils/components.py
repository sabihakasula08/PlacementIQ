"""
Reusable Modern UI Components for PlacementIQ
Provides Canvas-rendered rounded cards, multi-stop gradient banners,
neon pill buttons, concentric circular gauges, interactive line charts,
and timeline widgets matching the dark neon SaaS reference design.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Dict, Any, Tuple
from utils.theme import Theme

# Helper: Convert HEX to RGB
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Helper: Interpolate between two RGB colors
def interpolate_color(color1: str, color2: str, t: float) -> str:
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def interpolate_multi(colors: List[str], t: float) -> str:
    if len(colors) == 1:
        return colors[0]
    n = len(colors) - 1
    segment = int(t * n)
    if segment >= n:
        return colors[-1]
    local_t = (t * n) - segment
    return interpolate_color(colors[segment], colors[segment + 1], local_t)


class ModernCard(tk.Frame):
    """
    A dark charcoal card container with smooth rounded borders.
    Hosts an inner frame for placing standard or custom child widgets.
    """
    def __init__(
        self,
        parent,
        bg_color: str = Theme.CARD_BG,
        border_color: str = Theme.CARD_BORDER,
        radius: int = 16,
        padding: int = 14,
        min_height: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        **kwargs
    ):
        super().__init__(parent, bg=Theme.BG_DARK, **kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.padding = padding
        self.min_height = max(min_height, height or 0)

        canvas_kwargs = {"bg": Theme.BG_DARK, "highlightthickness": 0, "bd": 0}
        if width:
            canvas_kwargs["width"] = width
        if self.min_height:
            canvas_kwargs["height"] = self.min_height

        self.canvas = tk.Canvas(self, **canvas_kwargs)
        self.canvas.pack(fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg_color)
        self.window_id = self.canvas.create_window(padding, padding, anchor="nw", window=self.inner)

        self.bind("<Configure>", self._on_resize)

    def set_card_height(self, new_height: int):
        self.min_height = new_height
        self.canvas.configure(height=new_height)
        self.configure(height=new_height)
        self._on_resize(type("Event", (), {"width": max(10, self.winfo_width()), "height": new_height})())

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, fill=fill, outline=outline, width=1, tags="card_bg")

    def _on_resize(self, event):
        w = event.width
        h = max(self.min_height, event.height)
        if w < 10 or h < 10:
            return
        self.canvas.delete("card_bg")
        pad = 1
        self._draw_rounded_rect(pad, pad, w - pad, h - pad, self.radius, self.bg_color, self.border_color)
        self.canvas.tag_lower("card_bg")

        inner_w = max(10, w - (self.padding * 2))
        inner_h = max(10, h - (self.padding * 2))
        self.canvas.coords(self.window_id, self.padding, self.padding)
        self.canvas.itemconfigure(self.window_id, width=inner_w, height=inner_h)


class GradientBanner(tk.Canvas):
    """
    The signature top hero welcome banner from the reference UI.
    Renders a warm sunset-to-magenta-to-violet gradient with typography,
    date badge, and custom call-to-action button.
    """
    def __init__(
        self,
        parent,
        title: str = "Welcome Back",
        subtitle: str = "PlacementIQ Portal",
        action_text: str = "+ Add Drive",
        action_callback: Optional[Callable] = None,
        date_text: str = "12 Nov 2026, 10:00 AM",
        height: int = 110,
        **kwargs
    ):
        super().__init__(parent, height=height, bg=Theme.BG_DARK, highlightthickness=0, bd=0, **kwargs)
        self.title_text = title
        self.subtitle_text = subtitle
        self.action_text = action_text
        self.action_callback = action_callback
        self.date_text = date_text
        self.height = height

        self.colors = [Theme.GRADIENT_HERO_START, Theme.GRADIENT_HERO_MID, Theme.GRADIENT_HERO_END]

        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_click)

    def update_content(self, title: str, subtitle: str, date_text: Optional[str] = None):
        self.title_text = title
        self.subtitle_text = subtitle
        if date_text:
            self.date_text = date_text
        self._redraw(self.winfo_width(), self.winfo_height())

    def _on_resize(self, event):
        self._redraw(event.width, event.height)

    def _redraw(self, w: int, h: int):
        self.delete("all")
        if w < 30 or h < 20:
            return

        # Render gradient stripes
        steps = min(120, max(40, w // 4))
        stripe_w = w / steps
        for i in range(steps):
            t = i / steps
            color = interpolate_multi(self.colors, t)
            x1 = i * stripe_w
            x2 = (i + 1) * stripe_w + 1
            self.create_rectangle(x1, 0, x2, h, fill=color, outline=color)

        # Draw Title and Subtitle with high-contrast dark typography
        self.create_text(
            24, h // 2 - 14,
            text=self.title_text,
            anchor="w",
            font=Theme.FONT_TITLE_XL,
            fill=Theme.TEXT_DARK
        )
        self.create_text(
            25, h // 2 + 16,
            text=self.subtitle_text,
            anchor="w",
            font=Theme.FONT_BODY_BOLD,
            fill="#2D1B36"
        )

        # Draw Date Pill on the right
        btn_w = 120
        pill_w = 170
        btn_h = 36
        pill_y = h // 2

        btn_x2 = w - 24
        btn_x1 = btn_x2 - btn_w
        pill_x2 = btn_x1 - 16
        pill_x1 = pill_x2 - pill_w

        # Date capsule pill
        self._draw_pill(pill_x1, pill_y - 18, pill_x2, pill_y + 18, fill="#FFFFFF", outline="#FFFFFF")
        self.create_text(
            (pill_x1 + pill_x2) // 2, pill_y,
            text=f"📅 {self.date_text}",
            font=Theme.FONT_SMALL_BOLD,
            fill=Theme.TEXT_DARK
        )

        # Action Button pill (Dark matte black with white text)
        self.btn_bounds = (btn_x1, pill_y - 18, btn_x2, pill_y + 18)
        self._draw_pill(btn_x1, pill_y - 18, btn_x2, pill_y + 18, fill="#0F0F17", outline="#0F0F17", tag="action_btn")
        self.create_text(
            (btn_x1 + btn_x2) // 2, pill_y,
            text=self.action_text,
            font=Theme.FONT_BODY_BOLD,
            fill=Theme.TEXT_WHITE,
            tag="action_btn"
        )

    def _draw_pill(self, x1, y1, x2, y2, fill, outline, tag=None):
        r = (y2 - y1) // 2
        pts = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        kwargs = {"smooth": True, "fill": fill, "outline": outline}
        if tag:
            kwargs["tags"] = tag
        return self.create_polygon(pts, **kwargs)

    def _on_click(self, event):
        if hasattr(self, "btn_bounds"):
            x1, y1, x2, y2 = self.btn_bounds
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if self.action_callback:
                    self.action_callback()


class NeonButton(tk.Canvas):
    """
    Sleek neon pill button with smooth hover animation and click feedback.
    Supports 'primary' (neon magenta/pink), 'secondary' (dark SaaS border),
    or 'success' (emerald green).
    """
    def __init__(
        self,
        parent,
        text: str,
        command: Optional[Callable] = None,
        style: str = "primary",  # 'primary', 'secondary', 'danger', 'success'
        width: int = 130,
        height: int = 36,
        font=Theme.FONT_BODY_BOLD,
        **kwargs
    ):
        super().__init__(parent, width=width, height=height, bg=Theme.BG_DARK, highlightthickness=0, bd=0, **kwargs)
        self.text = text
        self.command = command
        self.style = style
        self.w = width
        self.h = height
        self.font = font
        self.is_hover = False

        if style == "primary":
            self.color_normal = Theme.ACCENT_PINK
            self.color_hover = Theme.ACCENT_PINK_HOVER
            self.text_color = Theme.TEXT_WHITE
            self.border_color = Theme.ACCENT_PINK
        elif style == "success":
            self.color_normal = Theme.COLOR_SUCCESS
            self.color_hover = "#10B981"
            self.text_color = Theme.TEXT_DARK
            self.border_color = Theme.COLOR_SUCCESS
        elif style == "danger":
            self.color_normal = Theme.COLOR_DANGER
            self.color_hover = "#FF6B8B"
            self.text_color = Theme.TEXT_WHITE
            self.border_color = Theme.COLOR_DANGER
        else: # secondary / outline
            self.color_normal = Theme.CARD_BG_ALT
            self.color_hover = Theme.CARD_BORDER
            self.text_color = Theme.TEXT_LIGHT
            self.border_color = Theme.CARD_BORDER

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._on_resize)
        self._draw()

    def _on_resize(self, event):
        self.w = event.width
        self.h = event.height
        self._draw()

    def _on_enter(self, e):
        self.is_hover = True
        self._draw()

    def _on_leave(self, e):
        self.is_hover = False
        self._draw()

    def _on_click(self, e):
        if self.command:
            self.command()

    def set_text(self, text: str):
        self.text = text
        self._draw()

    def _draw(self):
        self.delete("all")
        pad = 2
        r = (self.h - pad * 2) // 2
        x1, y1 = pad, pad
        x2, y2 = self.w - pad, self.h - pad

        pts = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        fill = self.color_hover if self.is_hover else self.color_normal
        self.create_polygon(pts, smooth=True, fill=fill, outline=self.border_color, width=1)
        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text,
            font=self.font,
            fill=self.text_color
        )


class PillBadge(tk.Canvas):
    """
    Modern status pill badge (e.g. 'Good Fit', 'Selected', 'Assessment').
    """
    def __init__(
        self,
        parent,
        text: str,
        status: str = "default",
        width: int = 90,
        height: int = 24,
        **kwargs
    ):
        super().__init__(parent, width=width, height=height, bg=Theme.CARD_BG, highlightthickness=0, bd=0, **kwargs)
        self.text = text
        self.status = status
        self.w = width
        self.h = height

        if status in ("Good Fit", "Selected", "Active"):
            self.bg_c = Theme.BADGE_BG_GREEN
            self.border_c = Theme.BADGE_BORDER_GREEN
            self.text_c = Theme.BADGE_TEXT_GREEN
        elif status in ("Shortlisted", "Eligible"):
            self.bg_c = Theme.BADGE_BG_PINK
            self.border_c = Theme.BADGE_BORDER_PINK
            self.text_c = Theme.BADGE_TEXT_PINK
        elif status in ("Interview", "Moderate"):
            self.bg_c = Theme.BADGE_BG_PURPLE
            self.border_c = Theme.BADGE_BORDER_PURPLE
            self.text_c = Theme.BADGE_TEXT_PURPLE
        elif status in ("Assessment", "Upcoming"):
            self.bg_c = Theme.BADGE_BG_ORANGE
            self.border_c = Theme.BADGE_BORDER_ORANGE
            self.text_c = Theme.BADGE_TEXT_ORANGE
        elif status in ("Rejected", "Ineligible", "Closed"):
            self.bg_c = "#3D1118"
            self.border_c = Theme.COLOR_DANGER
            self.text_c = "#FFA3B2"
        else: # Applied / default
            self.bg_c = "#0E2438"
            self.border_c = Theme.COLOR_INFO
            self.text_c = "#7DD3FC"

        self._draw()

    def _draw(self):
        self.delete("all")
        pad = 1
        r = (self.h - pad * 2) // 2
        x1, y1 = pad, pad
        x2, y2 = self.w - pad, self.h - pad

        pts = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        self.create_polygon(pts, smooth=True, fill=self.bg_c, outline=self.border_c, width=1)
        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text,
            font=Theme.FONT_SMALL_BOLD,
            fill=self.text_c
        )


class SegmentedToggle(tk.Canvas):
    """
    Sleek segmented pill toggle switch (e.g. Daily | Weekly | Monthly)
    """
    def __init__(
        self,
        parent,
        options: List[str],
        default_index: int = 0,
        on_change: Optional[Callable[[str], None]] = None,
        height: int = 32,
        pill_width: int = 70,
        **kwargs
    ):
        self.options = options
        self.selected_index = default_index
        self.on_change = on_change
        self.height = height
        self.pill_width = pill_width
        total_width = len(options) * pill_width + 6

        super().__init__(parent, width=total_width, height=height, bg=Theme.CARD_BG, highlightthickness=0, bd=0, **kwargs)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        w = len(self.options) * self.pill_width + 6
        h = self.height

        # Background track
        self._draw_pill(2, 2, w - 2, h - 2, fill=Theme.INPUT_BG, outline=Theme.CARD_BORDER)

        # Active item pill highlight
        x1 = 3 + self.selected_index * self.pill_width
        x2 = x1 + self.pill_width
        self._draw_pill(x1 + 1, 3, x2 - 1, h - 3, fill=Theme.CARD_BG_ALT, outline=Theme.ACCENT_PINK)

        # Text labels
        for i, opt in enumerate(self.options):
            center_x = 3 + i * self.pill_width + self.pill_width // 2
            is_active = (i == self.selected_index)
            color = Theme.TEXT_WHITE if is_active else Theme.TEXT_MUTED
            font = Theme.FONT_SMALL_BOLD if is_active else Theme.FONT_SMALL
            self.create_text(center_x, h // 2, text=opt, font=font, fill=color)

    def _draw_pill(self, x1, y1, x2, y2, fill, outline):
        r = (y2 - y1) // 2
        pts = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        self.create_polygon(pts, smooth=True, fill=fill, outline=outline, width=1)

    def _on_click(self, event):
        clicked_idx = (event.x - 3) // self.pill_width
        if 0 <= clicked_idx < len(self.options) and clicked_idx != self.selected_index:
            self.selected_index = clicked_idx
            self._draw()
            if self.on_change:
                self.on_change(self.options[self.selected_index])


class InteractiveLineChart(tk.Canvas):
    """
    Canvas line chart matching the center 'Candidate Applied' chart in the screenshot.
    Renders dark background, horizontal dashed grid lines, a vibrant purple/magenta
    smoothed trend curve, data point nodes, and interactive hover tooltip pill!
    """
    def __init__(
        self,
        parent,
        data_points: Optional[List[int]] = None,
        labels: Optional[List[str]] = None,
        height: int = 210,
        **kwargs
    ):
        super().__init__(parent, height=height, bg=Theme.CARD_BG, highlightthickness=0, bd=0, **kwargs)
        self.data_points = data_points or [220, 240, 310, 480, 460, 680, 520, 580, 610, 490, 470, 540]
        self.labels = labels or ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.height = height
        self.hover_index = 5  # default active tooltip at Jun (like in screenshot)

        self.bind("<Configure>", self._on_resize)
        self.bind("<Motion>", self._on_motion)

    def set_data(self, data_points: List[int], labels: List[str]):
        self.data_points = data_points
        self.labels = labels
        self.hover_index = min(len(data_points) - 1, 5)
        self._redraw(self.winfo_width(), self.winfo_height())

    def _on_resize(self, event):
        self._redraw(event.width, event.height)

    def _on_motion(self, event):
        w = self.winfo_width()
        margin_l, margin_r = 45, 25
        chart_w = w - margin_l - margin_r
        if chart_w <= 0 or not self.data_points:
            return

        step_x = chart_w / max(1, len(self.data_points) - 1)
        idx = int(round((event.x - margin_l) / step_x))
        idx = max(0, min(len(self.data_points) - 1, idx))
        if idx != self.hover_index:
            self.hover_index = idx
            self._redraw(w, self.winfo_height())

    def _redraw(self, w: int, h: int):
        self.delete("all")
        if w < 100 or h < 80:
            return

        margin_l = 45
        margin_r = 25
        margin_t = 30
        margin_b = 30

        chart_w = w - margin_l - margin_r
        chart_h = h - margin_t - margin_b

        max_val = max(self.data_points) if self.data_points else 100
        max_val = max(100, int(max_val * 1.25))

        # Horizontal grid lines & Y labels
        grid_steps = 4
        for i in range(grid_steps + 1):
            y_val = int((max_val / grid_steps) * i)
            y_pos = margin_t + chart_h - (i * (chart_h / grid_steps))

            self.create_line(
                margin_l, y_pos, w - margin_r, y_pos,
                fill=Theme.CARD_BORDER,
                dash=(3, 4)
            )
            # Label
            label_text = f"{y_val}" if y_val < 1000 else f"{y_val/1000:.1f}k"
            self.create_text(
                margin_l - 10, y_pos,
                text=label_text,
                anchor="e",
                font=Theme.FONT_TINY,
                fill=Theme.TEXT_SUBTLE
            )

        # Calculate plot coordinates
        coords = []
        step_x = chart_w / max(1, len(self.data_points) - 1)
        for i, val in enumerate(self.data_points):
            x = margin_l + i * step_x
            y = margin_t + chart_h - (val / max_val) * chart_h
            coords.append((x, y))

            # X-axis label
            if i < len(self.labels):
                self.create_text(
                    x, h - 14,
                    text=self.labels[i],
                    font=Theme.FONT_TINY,
                    fill=Theme.TEXT_MUTED if i != self.hover_index else Theme.ACCENT_PINK
                )

        # Draw glowing smoothed polygon curve
        poly_pts = []
        for x, y in coords:
            poly_pts.extend([x, y])

        if len(coords) >= 2:
            self.create_line(
                poly_pts,
                smooth=True,
                fill=Theme.GRADIENT_PURPLE_START,
                width=3,
                joinstyle=tk.ROUND,
                capstyle=tk.ROUND
            )

        # Draw data point circles & Hover highlight
        for i, (x, y) in enumerate(coords):
            if i == self.hover_index:
                # Vertical guide line
                self.create_line(x, margin_t, x, margin_t + chart_h, fill=Theme.ACCENT_PINK, dash=(2, 2))
                # Outer glow
                self.create_oval(x - 8, y - 8, x + 8, y + 8, fill="", outline=Theme.ACCENT_PINK, width=2)
                # Inner node
                self.create_oval(x - 4, y - 4, x + 4, y + 4, fill=Theme.TEXT_WHITE, outline=Theme.ACCENT_PINK)

                # Tooltip capsule pill
                val = self.data_points[i]
                tooltip_text = f"Candidates : {val} ↗"
                tt_w = 120
                tt_h = 24
                tt_x1 = max(margin_l, min(w - margin_r - tt_w, x - tt_w // 2))
                tt_x2 = tt_x1 + tt_w
                tt_y1 = max(5, y - 34)
                tt_y2 = tt_y1 + tt_h

                self._draw_pill(tt_x1, tt_y1, tt_x2, tt_y2, fill="#252438", outline=Theme.ACCENT_PINK)
                self.create_text(
                    (tt_x1 + tt_x2) // 2, (tt_y1 + tt_y2) // 2,
                    text=tooltip_text,
                    font=Theme.FONT_SMALL_BOLD,
                    fill=Theme.TEXT_WHITE
                )
            else:
                self.create_oval(x - 3, y - 3, x + 3, y + 3, fill=Theme.CARD_BORDER, outline=Theme.ACCENT_PURPLE, width=1)

    def _draw_pill(self, x1, y1, x2, y2, fill, outline):
        r = (y2 - y1) // 2
        pts = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        self.create_polygon(pts, smooth=True, fill=fill, outline=outline, width=1)


class ConcentricGauge(tk.Canvas):
    """
    Concentric circular progress arcs matching the 'Statistic' card in the screenshot.
    Draws multi-colored neon rings representing:
    - Academics (Orange)
    - Technical Skills (Pink)
    - Aptitude (Purple)
    - Soft Skills / Communication (Emerald Green)
    - Projects & Practical (Cyan)
    """
    def __init__(
        self,
        parent,
        category_scores: Optional[Dict[str, float]] = None,
        overall_score: float = 85.0,
        height: int = 180,
        **kwargs
    ):
        super().__init__(parent, height=height, bg=Theme.CARD_BG, highlightthickness=0, bd=0, **kwargs)
        self.overall_score = overall_score
        self.category_scores = category_scores or {
            "Academics": 21.8,       # out of 25
            "Technical Skills": 22.5, # out of 25
            "Aptitude": 17.0,        # out of 20
            "Communication": 12.0,   # out of 15
            "Projects": 12.5         # out of 15
        }
        self.max_weights = {
            "Academics": 25.0,
            "Technical Skills": 25.0,
            "Aptitude": 20.0,
            "Communication": 15.0,
            "Projects": 15.0
        }
        self.ring_colors = [
            Theme.ACCENT_ORANGE,
            Theme.ACCENT_PINK,
            Theme.ACCENT_PURPLE,
            Theme.COLOR_SUCCESS,
            Theme.ACCENT_CYAN
        ]

        self.bind("<Configure>", self._on_resize)

    def set_scores(self, scores: Dict[str, float], overall: float):
        self.category_scores = scores
        self.overall_score = overall
        self._redraw(self.winfo_width(), self.winfo_height())

    def _on_resize(self, event):
        self._redraw(event.width, event.height)

    def _redraw(self, w: int, h: int):
        self.delete("all")
        if w < 50 or h < 50:
            return

        cx = w // 2 - 40
        cy = h // 2 + 10
        base_r = min(cx - 20, cy - 20, 65)

        categories = list(self.category_scores.keys())
        ring_thickness = 5
        ring_spacing = 7

        for i, cat in enumerate(categories):
            score = self.category_scores.get(cat, 0.0)
            max_w = self.max_weights.get(cat, 25.0)
            pct = min(1.0, max(0.0, score / max_w))

            r = base_r - (i * ring_spacing)
            if r <= 10:
                break

            color = self.ring_colors[i % len(self.ring_colors)]

            # Background track arc (180 degrees or 240 degrees)
            self.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=0, extent=180,
                style=tk.ARC,
                outline=Theme.CARD_BORDER,
                width=ring_thickness
            )

            # Active filled arc
            extent_angle = int(pct * 180)
            if extent_angle > 0:
                self.create_arc(
                    cx - r, cy - r, cx + r, cy + r,
                    start=180 - extent_angle, extent=extent_angle,
                    style=tk.ARC,
                    outline=color,
                    width=ring_thickness
                )

        # Center Score
        self.create_text(
            cx, cy - 10,
            text=f"{self.overall_score:.0f}",
            font=Theme.FONT_TITLE_XL,
            fill=Theme.TEXT_WHITE
        )
        self.create_text(
            cx, cy + 12,
            text="Readiness / 100",
            font=Theme.FONT_TINY,
            fill=Theme.TEXT_MUTED
        )

        # Legend on the right side
        leg_x = cx + base_r + 25
        leg_y_start = 24
        for i, cat in enumerate(categories):
            y = leg_y_start + (i * 24)
            color = self.ring_colors[i % len(self.ring_colors)]
            score = self.category_scores.get(cat, 0.0)
            max_w = self.max_weights.get(cat, 25.0)

            # Bullet dot
            self.create_oval(leg_x, y - 4, leg_x + 8, y + 4, fill=color, outline=color)
            # Label
            self.create_text(
                leg_x + 16, y,
                text=f"{cat} ({score:.1f}/{max_w:.0f})",
                anchor="w",
                font=Theme.FONT_SMALL,
                fill=Theme.TEXT_LIGHT
            )


class MiniSparkline(tk.Canvas):
    """
    Mini sparkline curve for KPI cards (like in top cards of reference design).
    """
    def __init__(self, parent, values: List[int], color: str = Theme.ACCENT_PURPLE, width: int = 110, height: int = 36, **kwargs):
        super().__init__(parent, width=width, height=height, bg=Theme.CARD_BG, highlightthickness=0, bd=0, **kwargs)
        self.values = values
        self.color = color
        self._draw(width, height)

    def _draw(self, w: int, h: int):
        self.delete("all")
        if not self.values or len(self.values) < 2:
            return
        max_v = max(self.values) or 1
        min_v = min(self.values)
        rng = max(1, max_v - min_v)

        step_x = (w - 6) / (len(self.values) - 1)
        coords = []
        for i, v in enumerate(self.values):
            x = 3 + i * step_x
            y = h - 3 - ((v - min_v) / rng) * (h - 6)
            coords.extend([x, y])

        self.create_line(coords, smooth=True, fill=self.color, width=2)


class ScheduleTimelineWidget(tk.Canvas):
    """
    Timeline widget matching 'Today's schedule' in the screenshot.
    Renders time slots: 09:00, 10:00, 11:00, 12:00, 01:00, 02:00
    with gradient schedule blocks representing recruitment events.
    """
    def __init__(self, parent, events: Optional[List[Dict[str, str]]] = None, height: int = 130, **kwargs):
        super().__init__(parent, height=height, bg=Theme.CARD_BG, highlightthickness=0, bd=0, **kwargs)
        self.events = events or [
            {"time_idx": 1, "title": "Google Cloud Online Test", "subtitle": "Auditorium Lab 3", "color": Theme.GRADIENT_PURPLE_START},
            {"time_idx": 4, "title": "Microsoft SDE Tech Interview", "subtitle": "Teams Virtual Room 2", "color": Theme.ACCENT_PINK}
        ]
        self.times = ["09:00", "10:00", "11:00", "12:00", "01:00", "02:00", "03:00"]
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self._redraw(event.width, event.height)

    def _redraw(self, w: int, h: int):
        self.delete("all")
        if w < 100 or h < 60:
            return

        slot_w = w / len(self.times)
        timeline_y = 25

        # Render time header
        for i, t in enumerate(self.times):
            x = i * slot_w + slot_w // 2
            is_highlighted = (i == 4) # like '02:00' in screenshot
            if is_highlighted:
                # white capsule highlight
                self._draw_pill(x - 26, timeline_y - 12, x + 26, timeline_y + 12, fill="#FFFFFF", outline="#FFFFFF")
                self.create_text(x, timeline_y, text=t, font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_DARK)
            else:
                self.create_text(x, timeline_y, text=t, font=Theme.FONT_SMALL, fill=Theme.TEXT_MUTED)

        # Render event blocks
        block_y1 = 48
        block_y2 = h - 10
        for ev in self.events:
            idx = ev.get("time_idx", 1)
            x1 = idx * slot_w + 4
            x2 = (idx + 1.8) * slot_w - 4
            color = ev.get("color", Theme.GRADIENT_PURPLE_START)

            # Gradient/colored block
            self._draw_pill(x1, block_y1, x2, block_y2, fill=color, outline=color)
            self.create_text(
                x1 + 14, (block_y1 + block_y2) // 2 - 8,
                text=ev.get("title", "Event"),
                anchor="w",
                font=Theme.FONT_SMALL_BOLD,
                fill=Theme.TEXT_WHITE
            )
            self.create_text(
                x1 + 14, (block_y1 + block_y2) // 2 + 9,
                text=ev.get("subtitle", ""),
                anchor="w",
                font=Theme.FONT_TINY,
                fill="#F1E8F8"
            )

    def _draw_pill(self, x1, y1, x2, y2, fill, outline):
        r = 10
        pts = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        self.create_polygon(pts, smooth=True, fill=fill, outline=outline, width=1)


class ScrollableFrame(tk.Frame):
    """
    A smooth dark scrollable container without clunky standard Tkinter styling.
    """
    def __init__(self, parent, bg: str = Theme.BG_DARK, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg=bg)

        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )
        self.bind_mousewheel(self.canvas)
        self.bind_mousewheel(self.scrollable_content)

    def bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        for child in widget.winfo_children():
            self.bind_mousewheel(child)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

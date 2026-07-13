"""
Build the LEFT panel of the profile: the InfinitySell infinity mark inside the
same terminal window as the rest of the profile, drawing itself on like a
plotter (SMIL stroke-dash reveal) instead of an ASCII portrait. Same canvas
size (840x875) and chrome as make_ascii_svg.py so it stays the same height as
the info card at README widths 370/490.

Source logo: assets/infinity-logo.svg (a lemniscate as an L-segment polyline).
STATIC=1 emits the frozen final frame for Quick Look / PNG previews.
"""
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "..", "assets", "infinity-logo.svg")
OUT = os.path.join(HERE, "..", "brand-card.svg")
STATIC = bool(os.environ.get("STATIC"))

# ---- canvas + chrome (mirrors make_ascii_svg.py) --------------------------
PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
CANVAS_W, CANVAS_H = 840, 875

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
LOGO_WHITE = "#eef4ff"   # bright front stroke
LOGO_SILVER = "#8b98ad"  # rotated back stroke (the double-line look)
ACCENT = "#22d3ee"
GREEN = "#3fb950"

# ---- pull the infinity path + its polyline length -------------------------
svg = open(LOGO).read()
D = re.search(r'<path[^>]*\bd="([^"]+)"', svg).group(1)
pts = [(float(x), float(y)) for x, y in re.findall(r'([\d.]+),([\d.]+)', D)]
length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
DASH = round(length + 2)  # a hair of slack so the join fully closes


def draw(stroke, width, dash_begin, dash_dur, extra_transform=""):
    """one infinity stroke; animates stroke-dashoffset DASH->0 unless STATIC."""
    tf = f' transform="{extra_transform}"' if extra_transform else ""
    if STATIC:
        return (f'<path d="{D}" fill="none" stroke="{stroke}" stroke-width="{width}" '
                f'stroke-linejoin="round" stroke-linecap="round"{tf}/>')
    return (f'<path d="{D}" fill="none" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"{tf} '
            f'stroke-dasharray="{DASH}" stroke-dashoffset="{DASH}">'
            f'<animate attributeName="stroke-dashoffset" from="{DASH}" to="0" '
            f'begin="{dash_begin:.2f}s" dur="{dash_dur:.2f}s" fill="freeze" '
            f'calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.2 1"/></path>')


def fade(inner, begin):
    if STATIC:
        return f"<g>{inner}</g>"
    return (f'<g opacity="0" transform="translate(0,6)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
            f'dur="0.5s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 6" '
            f'to="0 0" begin="{begin:.2f}s" dur="0.5s" fill="freeze" calcMode="spline" '
            f'keySplines="0.2 0.8 0.2 1"/></g>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
    f'<radialGradient id="glow" cx="0.5" cy="0.44" r="0.5">'
    f'<stop offset="0" stop-color="#1b2740"/><stop offset="1" stop-color="#0d1117" stop-opacity="0"/>'
    f'</radialGradient></defs>',
    f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
    f'fill="none" stroke="{FRAME}" stroke-width="1"/>',
    # title bar
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">shahmir@github: ~$ ./brand.sh</text>')

# soft glow behind the mark
cx, cy = CANVAS_W / 2, TITLEBAR_H + 320
parts.append(f'<rect x="{PAD}" y="{TITLEBAR_H+40}" width="{CANVAS_W-2*PAD}" height="560" '
             f'fill="url(#glow)"/>')

# ---- the infinity mark: logo viewBox is 240x80; scale + center ------------
scale = 2.55
gx = cx - (240 * scale) / 2
gy = cy - (80 * scale) / 2
parts.append(f'<g transform="translate({gx:.1f},{gy:.1f}) scale({scale})">')
parts.append(draw(LOGO_SILVER, 2.6, 0.35, 1.55, "rotate(3 120 40)"))
parts.append(draw(LOGO_WHITE, 2.6, 0.15, 1.55))
parts.append('</g>')

# ---- wordmark + tagline (letter-spaced caps, like the brand) --------------
wm_y = cy + 250
parts.append(fade(
    f'<text x="{cx}" y="{wm_y}" text-anchor="middle" fill="{INK}" font-size="46" '
    f'font-weight="300" letter-spacing="18">INFINITY SELL</text>', 1.35))
parts.append(fade(
    f'<text x="{cx}" y="{wm_y+40}" text-anchor="middle" fill="{TITLE_TEXT}" font-size="17" '
    f'font-weight="400" letter-spacing="9">SYSTEMS THAT SELL.</text>', 1.7))

# ---- status bar: whoami + role, steady blinking cursor --------------------
status_line_y = CANVAS_H - STATUS_H - PAD * 0.5
status_y = status_line_y + 20
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(
    f'<text x="{PAD}" y="{status_y:.1f}" font-size="13">'
    f'<tspan fill="{TITLE_TEXT}">shahmir@github:~$ whoami </tspan>'
    f'<tspan fill="{INK}">Shahmir Gill</tspan>'
    f'<tspan fill="{TITLE_TEXT}"> — Founder, </tspan>'
    f'<tspan fill="{ACCENT}">InfinitySell.io</tspan></text>')
parts.append(f'<rect x="{PAD+505}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
out = "".join(parts)
with open(OUT, "w") as f:
    f.write(out)
print("wrote", OUT, len(out), "bytes; path length", round(length, 1), "dash", DASH)

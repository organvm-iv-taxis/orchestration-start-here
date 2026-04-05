"""Render the Systematic Cartography canvas — contribution network topology.

Produces 3 LinkedIn-ready PNGs at 2400x1260 (LinkedIn carousel ratio).
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path.home() / ".claude/skills/canvas-design/canvas-fonts"
OUT = Path(__file__).parent

W, H = 2400, 1260
BG = (8, 8, 24)  # deep navy


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


# Fonts
MONO = lambda s: load_font("JetBrainsMono-Regular.ttf", s)
MONO_BOLD = lambda s: load_font("JetBrainsMono-Bold.ttf", s)
SANS = lambda s: load_font("InstrumentSans-Regular.ttf", s)
SANS_BOLD = lambda s: load_font("InstrumentSans-Bold.ttf", s)
SERIF_IT = lambda s: load_font("InstrumentSerif-Italic.ttf", s)

# Colors — the cartographic palette
INDIGO = (60, 50, 120)       # home territory
VIOLET = (120, 70, 160)      # mid-flow
ROSE = (200, 80, 100)        # active engagement
GOLD = (220, 180, 80)        # harvested returns
DIM = (80, 80, 110)          # grid/annotations
BRIGHT = (220, 215, 230)     # primary text
MUTED = (140, 135, 155)      # secondary text
ACCENT = (230, 69, 96)       # highlight


def draw_grid(draw: ImageDraw.Draw):
    """Subtle geodetic grid."""
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill=(15, 15, 35), width=1)
    for y in range(0, H, 80):
        draw.line([(0, y), (W, y)], fill=(15, 15, 35), width=1)


def draw_circle(draw: ImageDraw.Draw, cx: int, cy: int, r: int,
                fill=None, outline=None, width=2):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=fill, outline=outline, width=width)


def draw_connection(draw: ImageDraw.Draw, x1, y1, x2, y2, color, width=2, dashed=False):
    if dashed:
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        segments = int(length / 12)
        for i in range(0, segments, 2):
            t1 = i / segments
            t2 = min((i + 1) / segments, 1.0)
            sx = x1 + (x2 - x1) * t1
            sy = y1 + (y2 - y1) * t1
            ex = x1 + (x2 - x1) * t2
            ey = y1 + (y2 - y1) * t2
            draw.line([(sx, sy), (ex, ey)], fill=color, width=width)
    else:
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)


def centered_text(draw, x, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x - tw // 2, y), text, font=font, fill=fill)


# ============================================================
# CANVAS 1: The Network Topology
# ============================================================
def render_network():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_grid(draw)

    # Title area — top left
    draw.text((60, 40), "SYSTEMATIC CARTOGRAPHY", font=MONO_BOLD(14), fill=DIM)
    draw.text((60, 60), "Contribution Network Topology", font=SANS(24), fill=BRIGHT)
    draw.text((60, 95), "7 targets  |  138,531 combined stars  |  7 open PRs", font=MONO(13), fill=MUTED)

    # Center node — ORGANVM
    cx, cy = W // 2, H // 2 + 20
    # Glow rings
    for r, alpha in [(140, 15), (120, 20), (100, 25)]:
        draw_circle(draw, cx, cy, r, outline=(*INDIGO, alpha), width=1)
    draw_circle(draw, cx, cy, 80, fill=(25, 22, 55), outline=VIOLET, width=3)
    centered_text(draw, cx, cy - 22, "ORGANVM", font=SANS_BOLD(22), fill=BRIGHT)
    centered_text(draw, cx, cy + 5, "118 repos", font=MONO(13), fill=MUTED)
    centered_text(draw, cx, cy + 25, "8 organs", font=MONO(13), fill=MUTED)

    # Target nodes — positioned around the center
    targets = [
        ("Anthropic/Skills", "100K", 99735, -55, ROSE),
        ("LangGraph", "27K", 27129, -15, ROSE),
        ("AdenHQ/Hive", "9.8K", 9766, 25, ACCENT),
        ("Temporal SDK", "1K", 1001, 65, VIOLET),
        ("dbt-mcp", "516", 516, 110, VIOLET),
        ("ipapi-py", "151", 151, 155, DIM),
        ("github-stars", "0", 0, 195, DIM),
    ]

    nodes = []
    for name, stars_str, stars, angle_deg, color in targets:
        angle = math.radians(angle_deg)
        dist = 380 + (100000 - min(stars, 100000)) / 100000 * 100  # closer = more stars
        dist = max(300, min(480, dist))
        nx = cx + int(dist * math.cos(angle))
        ny = cy + int(dist * math.sin(angle))
        # Node radius proportional to log(stars)
        r = max(18, int(12 + math.log(max(stars, 1)) * 4))

        # Connection line
        draw_connection(draw, cx, cy, nx, ny, (*color, 180), width=2)

        # Node
        draw_circle(draw, nx, ny, r, fill=(*color[:3], 40) if len(color) == 3 else (color[0], color[1], color[2], 40),
                     outline=color, width=2)

        # Labels
        label_x = nx + r + 12 if nx > cx else nx - r - 12
        anchor = "left" if nx > cx else "right"
        font_name = SANS(16)
        font_stars = MONO(12)

        if anchor == "left":
            draw.text((label_x, ny - 12), name, font=font_name, fill=BRIGHT)
            draw.text((label_x, ny + 8), f"{stars_str} stars", font=font_stars, fill=MUTED)
        else:
            bbox_n = draw.textbbox((0, 0), name, font=font_name)
            bbox_s = draw.textbbox((0, 0), f"{stars_str} stars", font=font_stars)
            draw.text((label_x - (bbox_n[2] - bbox_n[0]), ny - 12), name, font=font_name, fill=BRIGHT)
            draw.text((label_x - (bbox_s[2] - bbox_s[0]), ny + 8), f"{stars_str} stars", font=font_stars, fill=MUTED)

        nodes.append((nx, ny, r, name))

    # Legend — bottom right
    lx, ly = W - 340, H - 160
    draw.text((lx, ly), "SIGNAL TYPE", font=MONO_BOLD(11), fill=DIM)
    draw.line([(lx, ly + 20), (lx + 40, ly + 20)], fill=ACCENT, width=2)
    draw.text((lx + 50, ly + 14), "inbound (they reached out)", font=MONO(11), fill=MUTED)
    draw.line([(lx, ly + 40), (lx + 40, ly + 40)], fill=ROSE, width=2)
    draw.text((lx + 50, ly + 34), "high visibility (10K+ stars)", font=MONO(11), fill=MUTED)
    draw.line([(lx, ly + 60), (lx + 40, ly + 60)], fill=VIOLET, width=2)
    draw.text((lx + 50, ly + 54), "strategic (enterprise/niche)", font=MONO(11), fill=MUTED)
    draw.line([(lx, ly + 80), (lx + 40, ly + 80)], fill=DIM, width=2)
    draw.text((lx + 50, ly + 74), "opportunity (easy win)", font=MONO(11), fill=MUTED)

    # Bottom left — citation
    draw.text((60, H - 60), "Lakhani & von Hippel (2003). Research Policy, 32(6), 923-943.", font=SERIF_IT(12), fill=DIM)
    draw.text((60, H - 40), '"The community learns from its participants, and each individual learns from the community."', font=SERIF_IT(12), fill=MUTED)

    img.save(OUT / "linkedin-01-network.png", "PNG", dpi=(300, 300))
    print(f"Saved: linkedin-01-network.png ({img.size})")


# ============================================================
# CANVAS 2: The Campaign Phases
# ============================================================
def render_phases():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_grid(draw)

    draw.text((60, 40), "SYSTEMATIC CARTOGRAPHY", font=MONO_BOLD(14), fill=DIM)
    draw.text((60, 60), "Campaign Phase Architecture", font=SANS(24), fill=BRIGHT)

    phases = [
        ("UNBLOCK", "Sign CLAs\nClaim issues\nFix CI blockers", (200, 65, 75)),
        ("ENGAGE", "Join community\nIntroduce self\nBe helpful first", (210, 120, 50)),
        ("CULTIVATE", "Respond to reviews\nIterate on feedback\nBuild standing", (200, 180, 60)),
        ("HARVEST", "Extract patterns\nFormalize theory\nCreate artifacts", (55, 170, 95)),
        ("INJECT", "Deposit to organs\nPublish narrative\nDistribute", (55, 130, 190)),
    ]

    phase_w = 360
    phase_h = 320
    gap = 40
    total_w = len(phases) * phase_w + (len(phases) - 1) * gap
    start_x = (W - total_w) // 2
    y_top = 160

    positions = []
    for i, (name, desc, color) in enumerate(phases):
        x = start_x + i * (phase_w + gap)
        # Phase box
        draw.rounded_rectangle(
            [x, y_top, x + phase_w, y_top + phase_h],
            radius=8, fill=(color[0] // 8, color[1] // 8, color[2] // 8),
            outline=color, width=2
        )

        # Phase number
        draw.text((x + 20, y_top + 16), f"0{i + 1}", font=MONO_BOLD(48), fill=(*color, 60))

        # Phase name
        draw.text((x + 20, y_top + 80), name, font=SANS_BOLD(28), fill=BRIGHT)

        # Description
        for j, line in enumerate(desc.split("\n")):
            draw.text((x + 20, y_top + 125 + j * 28), line, font=SANS(17), fill=MUTED)

        # Arrow to next
        if i < len(phases) - 1:
            ax = x + phase_w + 5
            ay = y_top + phase_h // 2
            draw.polygon(
                [(ax, ay - 8), (ax + 25, ay), (ax, ay + 8)],
                fill=color
            )

        positions.append((x, y_top, phase_w, phase_h))

    # Feedback loop arrow — bottom
    loop_y = y_top + phase_h + 40
    last_x = positions[-1][0] + phase_w // 2
    first_x = positions[0][0] + phase_w // 2
    draw_connection(draw, last_x, y_top + phase_h + 10, last_x, loop_y, DIM, 2)
    draw_connection(draw, last_x, loop_y, first_x, loop_y, DIM, 2, dashed=True)
    draw_connection(draw, first_x, loop_y, first_x, y_top + phase_h + 10, DIM, 2)
    centered_text(draw, W // 2, loop_y - 20, "feeds next cycle", font=SERIF_IT(14), fill=MUTED)

    # Bottom citation
    draw.text((60, H - 60), "von Krogh, Spaeth & Lakhani (2003). Research Policy, 32(7), 1217-1241.", font=SERIF_IT(12), fill=DIM)
    draw.text((60, H - 40), '"Community, Joining, and Specialization in Open Source Software Innovation"', font=SERIF_IT(12), fill=MUTED)

    img.save(OUT / "linkedin-02-phases.png", "PNG", dpi=(300, 300))
    print(f"Saved: linkedin-02-phases.png ({img.size})")


# ============================================================
# CANVAS 3: The Cross-Organ Symbiote
# ============================================================
def render_symbiote():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_grid(draw)

    draw.text((60, 40), "SYSTEMATIC CARTOGRAPHY", font=MONO_BOLD(14), fill=DIM)
    draw.text((60, 60), "Cross-Organ Symbiote Pattern", font=SANS(24), fill=BRIGHT)
    draw.text((60, 95), "One contribution  |  Seven returns", font=MONO(13), fill=MUTED)

    # Central PR node
    pr_x, pr_y = W // 2, 200
    draw_circle(draw, pr_x, pr_y, 50, fill=(ACCENT[0] // 4, ACCENT[1] // 4, ACCENT[2] // 4),
                outline=ACCENT, width=3)
    centered_text(draw, pr_x, pr_y - 14, "PR", font=SANS_BOLD(28), fill=BRIGHT)
    centered_text(draw, pr_x, pr_y + 12, "upstream", font=MONO(12), fill=MUTED)

    # Organ nodes — fanned below
    organs = [
        ("I", "Theoria", "Pattern\nFormalization", (55, 100, 180)),
        ("II", "Poiesis", "Generative\nArtifacts", (130, 75, 170)),
        ("III", "Ergon", "Shipped\nCode", (55, 170, 95)),
        ("IV", "Taxis", "Orchestration\nJournal", (80, 80, 140)),
        ("V", "Logos", "Public\nNarrative", (210, 140, 50)),
        ("VI", "Koinonia", "Community\nCapital", (50, 160, 155)),
        ("VII", "Kerygma", "Distribution\nContent", (200, 65, 75)),
    ]

    organ_y = 550
    total_organs = len(organs)
    organ_spacing = (W - 300) // (total_organs - 1)
    start_ox = 150

    organ_positions = []
    for i, (num, name, desc, color) in enumerate(organs):
        ox = start_ox + i * organ_spacing
        oy = organ_y + (20 if i % 2 == 0 else 0)  # slight stagger

        # Connection from PR
        draw_connection(draw, pr_x, pr_y + 50, ox, oy - 55, color, width=2)

        # Organ box
        bw, bh = 220, 140
        draw.rounded_rectangle(
            [ox - bw // 2, oy - bh // 2, ox + bw // 2, oy + bh // 2],
            radius=6, fill=(color[0] // 8, color[1] // 8, color[2] // 8),
            outline=color, width=2
        )

        # Roman numeral
        centered_text(draw, ox, oy - bh // 2 + 14, num, font=MONO_BOLD(16), fill=color)
        # Name
        centered_text(draw, ox, oy - 10, name, font=SANS_BOLD(18), fill=BRIGHT)
        # Description
        for j, line in enumerate(desc.split("\n")):
            centered_text(draw, ox, oy + 16 + j * 22, line, font=SANS(14), fill=MUTED)

        organ_positions.append((ox, oy))

    # Feedback loops
    # ORGAN-I deepens expertise -> PR
    ix, iy = organ_positions[0]
    draw_connection(draw, ix - 100, iy - 40, pr_x - 160, pr_y + 30, (55, 100, 180), 1, dashed=True)
    draw.text((ix - 200, iy - 80), "deepens expertise", font=SERIF_IT(13), fill=(55, 100, 180))

    # ORGAN-VII attracts next target -> PR
    vx, vy = organ_positions[6]
    draw_connection(draw, vx + 100, vy - 40, pr_x + 160, pr_y + 30, (200, 65, 75), 1, dashed=True)
    draw.text((vx + 50, vy - 80), "attracts next target", font=SERIF_IT(13), fill=(200, 65, 75))

    # Bottom citation
    draw.text((60, H - 60), "Shen & Monge (2011). J. of Computer-Mediated Communication, 16(4).", font=SERIF_IT(12), fill=DIM)
    draw.text((60, H - 40), '"Network Effects: The Influence of Structural Social Capital on Open Source Project Success"', font=SERIF_IT(12), fill=MUTED)

    img.save(OUT / "linkedin-03-symbiote.png", "PNG", dpi=(300, 300))
    print(f"Saved: linkedin-03-symbiote.png ({img.size})")


if __name__ == "__main__":
    render_network()
    render_phases()
    render_symbiote()
    print("Done. 3 canvases rendered.")

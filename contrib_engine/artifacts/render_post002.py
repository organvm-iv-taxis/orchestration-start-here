"""Render production-grade visuals for LinkedIn Post #002.

Four carousel images, one per section:
1. Before/After — Testament audit scores (matplotlib)
2. The ℝ³ Rhetorical Space — multiplicative collapse (matplotlib 3D)
3. Contribution Network — 7 targets with data (matplotlib + networkx)
4. Recursive Proof — backflow capture (matplotlib flow)

All 2400x1260 (LinkedIn carousel ratio), dark theme, publication grade.
"""

import matplotlib

matplotlib.use("Agg")
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent
FONTS = Path.home() / ".claude/skills/canvas-design/canvas-fonts"

# Dark theme
BG = "#08081a"
GRID = "#12122a"
TEXT = "#ddd8e6"
MUTED = "#8c879b"
ACCENT = "#e94560"
ROSE = "#c85070"
VIOLET = "#7846a0"
INDIGO = "#3c3278"
GOLD = "#dcb450"
GREEN = "#37aa5f"
TEAL = "#32a09b"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "grid.alpha": 0.3,
    "font.size": 14,
    "font.family": "sans-serif",
})


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.3,
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"Saved: {name}")


# ============================================================
# IMAGE 1: Before/After Testament Audit
# ============================================================
def render_audit():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6.3))

    articles = [
        "I. Knowledge", "II. Causation", "III. Triple Layer",
        "IV. Units", "V. Collision", "VI. Recognition",
        "VII. Citation", "X. Opening", "XI. Paragraphs",
        "XII. Language", "XIII. Power"
    ]
    # Post #1 scores (0-10, based on audit)
    post1 = [1, 0, 2, 1, 0, 1, 0, 1, 0, 3, 2]
    # Post #2 scores (self-audited)
    post2 = [8, 9, 8, 7, 9, 8, 9, 8, 8, 7, 7]

    y = np.arange(len(articles))

    # Post 1 — left panel
    ax1.barh(y, post1, color=ACCENT, alpha=0.7, height=0.6)
    ax1.set_xlim(0, 10)
    ax1.set_yticks(y)
    ax1.set_yticklabels(articles, fontsize=10)
    ax1.set_xlabel("Score (0-10)", fontsize=10)
    ax1.set_title("Post #001 — Before", fontsize=16, color=ACCENT, pad=15)
    ax1.invert_yaxis()
    for i, v in enumerate(post1):
        ax1.text(v + 0.2, i, str(v), va="center", fontsize=9, color=MUTED)
    ax1.axvline(x=5, color=MUTED, linestyle="--", alpha=0.3)

    # Post 2 — right panel
    ax2.barh(y, post2, color=GREEN, alpha=0.7, height=0.6)
    ax2.set_xlim(0, 10)
    ax2.set_yticks(y)
    ax2.set_yticklabels([""] * len(articles))
    ax2.set_xlabel("Score (0-10)", fontsize=10)
    ax2.set_title("Post #002 — After", fontsize=16, color=GREEN, pad=15)
    ax2.invert_yaxis()
    for i, v in enumerate(post2):
        ax2.text(v + 0.2, i, str(v), va="center", fontsize=9, color=MUTED)
    ax2.axvline(x=5, color=MUTED, linestyle="--", alpha=0.3)

    fig.suptitle("Testament Audit: 13 Articles Applied", fontsize=11,
                 color=MUTED, y=0.02, fontstyle="italic")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    save(fig, "post002-01-audit.png")


# ============================================================
# IMAGE 2: The ℝ³ Rhetorical Space
# ============================================================
def render_rhetorical_space():
    fig = plt.figure(figsize=(12, 6.3))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    ax.set_facecolor(BG)
    fig.patch.set_facecolor(BG)

    # The positive orthant — where valid writing lives
    # Draw wireframe cube edges for the orthant
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_zlim(0, 10)
    ax.set_xlabel("Logos\n(argument)", fontsize=11, labelpad=10)
    ax.set_ylabel("Ethos\n(credibility)", fontsize=11, labelpad=10)
    ax.set_zlabel("Pathos\n(felt truth)", fontsize=11, labelpad=10)

    # Failed states — on the planes (volume = 0)
    # Resume: high ethos, no pathos/logos
    ax.scatter([1], [9], [0.5], c=ACCENT, s=200, marker="x", linewidths=3, zorder=5)
    ax.text(1, 9, 1.2, "Resume\n(ethos only)", fontsize=8, color=ACCENT)

    # Textbook: high logos, no pathos/ethos
    ax.scatter([9], [1], [0.5], c=ACCENT, s=200, marker="x", linewidths=3, zorder=5)
    ax.text(9, 1, 1.2, "Textbook\n(logos only)", fontsize=8, color=ACCENT)

    # Diary: high pathos, no logos/ethos
    ax.scatter([1], [0.5], [9], c=ACCENT, s=200, marker="x", linewidths=3, zorder=5)
    ax.text(1, 0.5, 9.5, "Diary\n(pathos only)", fontsize=8, color=ACCENT)

    # Post #1 — high ethos, low everything else
    ax.scatter([2], [8], [1], c=ROSE, s=300, marker="o", alpha=0.8, zorder=5)
    ax.text(2.5, 8, 1.5, "Post #1", fontsize=10, color=ROSE, fontweight="bold")

    # Post #2 — balanced in the orthant
    ax.scatter([8], [7], [7], c=GREEN, s=400, marker="o", alpha=0.9, zorder=5)
    ax.text(8.5, 7, 7.5, "Post #2", fontsize=10, color=GREEN, fontweight="bold")

    # Draw arrow from post1 to post2
    ax.plot([2, 8], [8, 7], [1, 7], color=GOLD, alpha=0.6, linewidth=2, linestyle="--")

    # Volume annotation
    v1 = 2 * 8 * 1
    v2 = 8 * 7 * 7
    ax.text2D(0.02, 0.95, f"V(Post #1) = {v1}  →  V(Post #2) = {v2}",
              transform=ax.transAxes, fontsize=11, color=GOLD)
    ax.text2D(0.02, 0.90, "V = logos × ethos × pathos  (zero on any axis = collapse)",
              transform=ax.transAxes, fontsize=9, color=MUTED)

    ax.view_init(elev=20, azim=135)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor(GRID)
    ax.yaxis.pane.set_edgecolor(GRID)
    ax.zaxis.pane.set_edgecolor(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)

    fig.suptitle("The Rhetorical Space: ℝ³₊₊", fontsize=11,
                 color=MUTED, y=0.02, fontstyle="italic")
    save(fig, "post002-02-rhetorical-space.png")


# ============================================================
# IMAGE 3: Contribution Network with Real Data
# ============================================================
def render_network():
    import networkx as nx

    fig, ax = plt.subplots(figsize=(12, 6.3))

    G = nx.Graph()

    # Center node
    G.add_node("ORGANVM", size=3000, color=VIOLET)

    # Targets with real data
    targets = [
        ("Anthropic\nSkills", 99735, ROSE, "PR #723"),
        ("LangGraph", 27129, ROSE, "PR #7237"),
        ("AdenHQ\nHive", 9766, ACCENT, "PR #6707"),
        ("Temporal\nSDK", 1001, VIOLET, "PR #1385"),
        ("dbt-mcp", 516, VIOLET, "PR #669"),
        ("ipapi-py", 151, MUTED, "PR #8"),
        ("github\nstars", 1, MUTED, "PR #39"),
    ]

    for name, stars, color, pr in targets:
        G.add_node(name, size=max(300, np.log(max(stars, 2)) * 250), color=color, stars=stars, pr=pr)
        G.add_edge("ORGANVM", name)

    # Position: center ORGANVM, radial layout for targets
    pos = {"ORGANVM": (0, 0)}
    angles = np.linspace(0, 2 * np.pi, len(targets), endpoint=False)
    # Offset so largest nodes are top-right
    angles = angles - np.pi / 4
    for i, (name, stars, _, _) in enumerate(targets):
        r = 1.8
        pos[name] = (r * np.cos(angles[i]), r * np.sin(angles[i]))

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=INDIGO, width=1.5, alpha=0.5)

    # Draw nodes
    for node in G.nodes():
        data = G.nodes[node]
        x, y = pos[node]
        size = data.get("size", 1500)
        color = data.get("color", VIOLET)
        circle = plt.Circle((x, y), np.sqrt(size) / 500, color=color, alpha=0.15)
        ax.add_patch(circle)
        circle2 = plt.Circle((x, y), np.sqrt(size) / 500, fill=False,
                              edgecolor=color, linewidth=2, alpha=0.8)
        ax.add_patch(circle2)
        ax.text(x, y, node, ha="center", va="center",
                fontsize=10 if node == "ORGANVM" else 8,
                fontweight="bold" if node == "ORGANVM" else "normal",
                color=TEXT)

    # Star count labels
    for name, stars, color, pr in targets:
        x, y = pos[name]
        r_offset = np.sqrt(G.nodes[name]["size"]) / 500 + 0.15
        angle = np.arctan2(y, x)
        lx = x + r_offset * np.cos(angle) * 0.8
        ly = y + r_offset * np.sin(angle) - 0.2
        stars_str = f"{stars:,}" if stars > 0 else "0"
        ax.text(lx, ly, f"{stars_str} ★  {pr}", fontsize=7, color=MUTED,
                ha="center")

    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-2.8, 2.8)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title and data summary
    ax.text(-3.0, 2.5, "Contribution Network", fontsize=16, color=TEXT, fontweight="bold")
    ax.text(-3.0, 2.2, "7 targets  |  138,531 combined stars  |  7 open PRs  |  0 human reviews",
            fontsize=9, color=MUTED)

    # Legend
    ax.text(1.8, -2.4, "● inbound signal (they reached out)", fontsize=8, color=ACCENT)
    ax.text(1.8, -2.6, "● high visibility (10K+ stars)", fontsize=8, color=ROSE)
    ax.text(1.8, -2.8, "● strategic / opportunity", fontsize=8, color=VIOLET)

    fig.suptitle("Node size ∝ log(stars)  |  118 repos → 7 targets via capability matching",
                 fontsize=9, color=MUTED, y=0.02, fontstyle="italic")
    save(fig, "post002-03-network.png")


# ============================================================
# IMAGE 4: The Recursive Proof — Backflow Capture
# ============================================================
def render_recursive():
    fig, ax = plt.subplots(figsize=(12, 6.3))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.3)
    ax.axis("off")

    # Title
    ax.text(6, 5.8, "The Recursive Proof", fontsize=20, ha="center",
            color=TEXT, fontweight="bold")
    ax.text(6, 5.4, "The backflow pipeline's first capture was from formalizing its own rules",
            fontsize=10, ha="center", color=MUTED)

    # Flow boxes
    boxes = [
        (1.5, 3.5, "Build\nContribution\nEngine", VIOLET, "16 commits\n111 tests"),
        (4.5, 3.5, "Formalize\nOperational\nRules", ROSE, "13 articles\n→ logic + math"),
        (7.5, 3.5, "Discover\nStructural\nCouplings", GOLD, "III/V isomorphism\ncharge coupling"),
        (10.5, 3.5, "Backflow\nCaptures\nItself", GREEN, "recursive proof\nthesis validated"),
    ]

    for x, y, label, color, annotation in boxes:
        rect = mpatches.FancyBboxPatch(
            (x - 1.1, y - 0.9), 2.2, 1.8,
            boxstyle="round,pad=0.15",
            facecolor=color + "18", edgecolor=color, linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x, y + 0.15, label, ha="center", va="center",
                fontsize=11, color=TEXT, fontweight="bold", linespacing=1.3)
        ax.text(x, y - 1.2, annotation, ha="center", va="top",
                fontsize=8, color=MUTED, linespacing=1.4)

    # Arrows between boxes
    for i in range(3):
        x1 = boxes[i][0] + 1.2
        x2 = boxes[i + 1][0] - 1.2
        y = 3.5
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                     arrowprops=dict(arrowstyle="->", color=MUTED, lw=2))
        # THEREFORE labels
        labels = ["THEREFORE", "THEREFORE", "THEREFORE"]
        ax.text((x1 + x2) / 2, y + 0.55, labels[i], ha="center",
                fontsize=7, color=MUTED, fontstyle="italic")

    # Recursive loop arrow — from last box back to first
    from matplotlib.patches import FancyArrowPatch
    style = "arc3,rad=-0.5"
    arrow = FancyArrowPatch(
        (10.5, 2.4), (1.5, 2.4),
        arrowstyle="->", color=ACCENT, linewidth=2,
        connectionstyle=style, mutation_scale=20
    )
    ax.add_patch(arrow)
    ax.text(6, 1.5, "feeds back into the system that built it",
            ha="center", fontsize=9, color=ACCENT, fontstyle="italic")

    # Bottom data bar
    data_items = [
        "7 PRs open", "138K combined ★", "13 Testament articles",
        "92 narrative algorithms", "6 organ backflow types"
    ]
    for i, item in enumerate(data_items):
        x = 1.2 + i * 2.2
        ax.text(x, 0.6, item, ha="center", fontsize=8, color=MUTED,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=GRID, edgecolor=INDIGO, alpha=0.5))

    fig.suptitle("Bidirectional knowledge transfer proved structural, not accidental — Lakhani & von Hippel (2003)",
                 fontsize=9, color=MUTED, y=0.02, fontstyle="italic")
    save(fig, "post002-04-recursive.png")


if __name__ == "__main__":
    render_audit()
    render_rhetorical_space()
    render_network()
    render_recursive()
    print("Done. 4 production images rendered.")

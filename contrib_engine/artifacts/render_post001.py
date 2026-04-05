"""Render visuals for Post #001 revision.

Two images:
1. System topology — 8 organs, 118 repos, dependency flow
2. Narrative algorithms — 14 theories × 92 algorithms with convergence data
"""

import matplotlib

matplotlib.use("Agg")
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).parent

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
BLUE = "#3780b8"

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
    "font.size": 12,
    "font.family": "sans-serif",
})


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.3,
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"Saved: {name}")


# ============================================================
# IMAGE 1: System Topology — 8 organs, key metrics
# ============================================================
def render_system():
    fig, ax = plt.subplots(figsize=(12, 6.3))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.3)
    ax.axis("off")

    ax.text(6, 5.9, "ORGANVM System Architecture", fontsize=18,
            ha="center", color=TEXT, fontweight="bold")
    ax.text(6, 5.5, "118 repositories  |  8 organs  |  740K words  |  55 dependency edges  |  0 violations",
            fontsize=9, ha="center", color=MUTED)

    organs = [
        ("I", "Theoria", "Theory &\nformal methods", 21, BLUE, 1.5),
        ("II", "Poiesis", "Generative art\n& performance", 32, VIOLET, 3.5),
        ("III", "Ergon", "Commercial\nproducts", 29, ROSE, 5.5),
        ("IV", "Taxis", "Orchestration\n& governance", 12, ACCENT, 7.5),
        ("V", "Logos", "Public\ndiscourse", 2, GOLD, 1.5),
        ("VI", "Koinonia", "Community\n& learning", 6, TEAL, 3.5),
        ("VII", "Kerygma", "Distribution\n& POSSE", 4, GREEN, 5.5),
        ("META", "Meta", "Cross-organ\ngovernance", 12, MUTED, 7.5),
    ]

    # Top row: I-IV (production chain)
    # Bottom row: V-VII + META (support functions)
    for i, (num, name, desc, repos, color, x) in enumerate(organs):
        y = 3.6 if i < 4 else 1.4
        w, h = 1.6, 1.5

        rect = mpatches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color + "15", edgecolor=color, linewidth=2
        )
        ax.add_patch(rect)

        ax.text(x, y + 0.35, num, ha="center", va="center",
                fontsize=9, color=color, fontweight="bold", fontstyle="italic")
        ax.text(x, y + 0.05, name, ha="center", va="center",
                fontsize=12, color=TEXT, fontweight="bold")
        ax.text(x, y - 0.35, desc, ha="center", va="center",
                fontsize=7, color=MUTED, linespacing=1.3)
        ax.text(x, y - h/2 - 0.15, f"{repos} repos", ha="center",
                fontsize=8, color=color)

    # Dependency arrows: I → II → III (top row)
    for x1, x2 in [(2.3, 2.7), (4.3, 4.7)]:
        ax.annotate("", xy=(x2, 3.6), xytext=(x1, 3.6),
                     arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.5))

    # IV orchestrates all — dashed lines down
    for target_x in [1.5, 3.5, 5.5]:
        ax.plot([7.5, target_x], [2.85, 2.2], color=INDIGO, linewidth=1,
                linestyle="--", alpha=0.4)

    # Label the dependency flow
    ax.text(3.5, 4.55, "I → II → III  (unidirectional production chain)",
            fontsize=8, ha="center", color=MUTED, fontstyle="italic")
    ax.text(7.5, 2.55, "IV orchestrates all",
            fontsize=7, ha="center", color=ACCENT, fontstyle="italic")

    # Bottom metrics bar
    metrics = [
        ("104 CI/CD\npipelines", BLUE),
        ("23K+\ntests", GREEN),
        ("seed.yaml\ncontracts", VIOLET),
        ("Forward-only\npromotion FSM", ACCENT),
        ("Zero\nviolations", GOLD),
    ]
    for i, (label, color) in enumerate(metrics):
        mx = 1.2 + i * 2.2
        ax.text(mx, 0.3, label, ha="center", va="center", fontsize=8, color=color,
                bbox=dict(boxstyle="round,pad=0.25", facecolor=GRID,
                          edgecolor=color + "40", alpha=0.8))

    save(fig, "post001-01-system-map.png")


# ============================================================
# IMAGE 2: Narrative Algorithms — 14 × 92 convergence
# ============================================================
def render_narratives():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6.3),
                                     gridspec_kw={"width_ratios": [1.4, 1]})

    # Left: the 14 studies as horizontal bars with algorithm counts
    studies = [
        ("Aristotle", 18, "Poetics — recognition, catharsis, unity"),
        ("Kubrick", 12, "Non-submersible units, productive ambiguity"),
        ("South Park", 8, "But/therefore causal connectors"),
        ("Waller-Bridge", 9, "Three-layer scene construction"),
        ("Larry David", 11, "Collision geometry, retrofit plotting"),
        ("Hitchcock", 7, "Suspense vs. surprise, bomb theory"),
        ("Miyazaki", 5, "Ma (negative space), ecological narrative"),
        ("Vince Gilligan", 6, "Transformation arc, consequence engine"),
        ("Bong Joon-ho", 4, "Parasite structure, tonal whiplash"),
        ("Pixar", 6, "Story spine, emotional beats"),
        ("David Simon", 3, "Systems-as-character, institutional failure"),
        ("Jordan Peele", 2, "Dual-register horror, social allegory"),
        ("Charlie Kaufman", 1, "Self-referential recursion"),
    ]

    # Sort by algorithm count
    studies.sort(key=lambda x: x[1], reverse=True)
    names = [s[0] for s in studies]
    counts = [s[1] for s in studies]
    descs = [s[2] for s in studies]

    y = np.arange(len(studies))
    colors = [ACCENT if c >= 10 else ROSE if c >= 7 else VIOLET if c >= 4 else MUTED
              for c in counts]

    ax1.barh(y, counts, color=colors, alpha=0.7, height=0.65)
    ax1.set_yticks(y)
    ax1.set_yticklabels(names, fontsize=9)
    ax1.set_xlabel("Algorithms extracted", fontsize=10)
    ax1.set_title("14 Narrative Theorists → 92 Algorithms", fontsize=14,
                  color=TEXT, pad=15)
    ax1.invert_yaxis()
    for i, (count, desc) in enumerate(zip(counts, descs)):
        ax1.text(count + 0.3, i, f"{count}", va="center", fontsize=8, color=MUTED)

    # Right: convergence diagram — where narrative meets engineering
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis("off")
    ax2.set_title("The Convergence", fontsize=14, color=TEXT, pad=15)

    # Two circles overlapping (Venn-like)
    circle1 = plt.Circle((3.5, 5), 2.8, fill=False, edgecolor=VIOLET,
                          linewidth=2, linestyle="-")
    circle2 = plt.Circle((6.5, 5), 2.8, fill=False, edgecolor=ACCENT,
                          linewidth=2, linestyle="-")
    ax2.add_patch(circle1)
    ax2.add_patch(circle2)

    # Fill intersection
    theta = np.linspace(0, 2 * np.pi, 100)
    # Just label the regions
    ax2.text(2, 5, "Narrative\nTheory", ha="center", va="center",
             fontsize=11, color=VIOLET, fontweight="bold")
    ax2.text(2, 3.8, "Recognition\nCausation\nLayering", ha="center", va="center",
             fontsize=8, color=MUTED)

    ax2.text(8, 5, "Systems\nEngineering", ha="center", va="center",
             fontsize=11, color=ACCENT, fontweight="bold")
    ax2.text(8, 3.8, "State machines\nDependency graphs\nCI/CD", ha="center", va="center",
             fontsize=8, color=MUTED)

    ax2.text(5, 5, "Shared\nFormal\nStructure", ha="center", va="center",
             fontsize=12, color=GOLD, fontweight="bold")
    ax2.text(5, 3.5, "ℝ³ constraint\nMultiplicative\ncollapse\nForward-only\ntransitions",
             ha="center", va="center", fontsize=7, color=GOLD, alpha=0.8)

    ax2.text(5, 1.2, "Not metaphor. Isomorphism.", ha="center",
             fontsize=10, color=TEXT, fontstyle="italic")

    fig.suptitle("Narratological Algorithmic Lenses — github.com/organvm-i-theoria/narratological-algorithmic-lenses",
                 fontsize=8, color=MUTED, y=0.02, fontstyle="italic")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    save(fig, "post001-02-narrative-algorithms.png")


if __name__ == "__main__":
    render_system()
    render_narratives()
    print("Done. 2 images for post-001 revision.")

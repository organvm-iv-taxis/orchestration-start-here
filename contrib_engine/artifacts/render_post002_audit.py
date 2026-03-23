"""Single production image for Post #002: The Bridge Audit.

Shows post #001's Testament violations with specific diagnosis per article.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent

BG = "#08081a"
GRID = "#12122a"
TEXT = "#ddd8e6"
MUTED = "#8c879b"
ACCENT = "#e94560"
GREEN = "#37aa5f"
GOLD = "#dcb450"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "grid.alpha": 0.2,
    "font.size": 13,
    "font.family": "sans-serif",
})


def render():
    fig, ax = plt.subplots(figsize=(14, 8))

    articles = [
        "I. Knowledge\nImperative",
        "II. Cascading\nCausation",
        "III. Triple\nLayer",
        "IV. Non-Submersible\nUnits",
        "V. Collision\nGeometry",
        "VI. Recognition\nPleasure",
        "VII. Citation\nDiscipline",
        "X. Opening\nArchitecture",
        "XI. Paragraph\nDiscipline",
        "XII. Charged\nLanguage",
        "XIII. Power\nPosition",
    ]

    scores = [1, 0, 2, 1, 0, 1, 0, 1, 0, 3, 2]

    violations = [
        "Creates zero new knowledge\n— every claim verifiable, none surprising",
        "AND_THEN throughout\n— no sentence causes the next",
        "Pure ethos, no pathos or logos\n— reads as resume, not argument",
        "Single text block\n— no modular sections",
        "Three projects listed in parallel\n— never converging",
        "No layered depth\n— surface meaning only",
        "No sources cited\n— claims without evidence",
        "Opens with credential dump\n— thesis buried at bottom",
        "No paragraph structure\n— no transitions, no clustering",
        "Throat-clearing present\n— 'Key projects I'm sharing publicly'",
        "Flat heartbeat\n— only 'discipline' carries weight",
    ]

    # Color by severity
    colors = [ACCENT if s == 0 else GOLD if s <= 2 else MUTED for s in scores]

    y = np.arange(len(articles))
    bars = ax.barh(y, scores, color=colors, alpha=0.8, height=0.7, edgecolor=GRID)
    ax.set_xlim(0, 10)
    ax.set_yticks(y)
    ax.set_yticklabels(articles, fontsize=10, linespacing=1.2)
    ax.invert_yaxis()
    ax.set_xlabel("Score (0–10)", fontsize=11)

    # Violation annotations
    for i, (score, violation) in enumerate(zip(scores, violations)):
        x_pos = max(score + 0.3, 0.3)
        ax.text(x_pos, i, violation, va="center", fontsize=8,
                color=MUTED, linespacing=1.3)

    # Threshold line
    ax.axvline(x=5, color=MUTED, linestyle="--", alpha=0.3, linewidth=1)
    ax.text(5.1, -0.8, "passing threshold", fontsize=8, color=MUTED, fontstyle="italic")

    # Title
    ax.set_title("Post #001 — Testament Audit\n"
                  "Aristotle · Parker/Stone · Waller-Bridge · Kubrick · Larry David\n"
                  "14 narrative theorists formalized into 13 diagnostic articles",
                  fontsize=14, color=TEXT, pad=20, linespacing=1.5)

    # Average score callout
    avg = np.mean(scores)
    ax.text(8.5, len(articles) - 0.5, f"avg: {avg:.1f}/10",
            fontsize=16, color=ACCENT, fontweight="bold", ha="center")

    # Bottom annotation
    fig.text(0.5, 0.02,
             "The same formal rules that govern scene construction govern technical communication.",
             ha="center", fontsize=10, color=GOLD, fontstyle="italic")

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(OUT / "post002-audit-violations.png", dpi=200,
                bbox_inches="tight", pad_inches=0.4,
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print("Saved: post002-audit-violations.png")


if __name__ == "__main__":
    render()

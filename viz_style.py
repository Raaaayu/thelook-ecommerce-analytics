"""Wspólny styl wykresów matplotlib – jedna paleta i wygląd we wszystkich notatnikach. Importuj:

    from viz_style import apply_style, legend_outside, COLORS, MONTHS_PL
"""
import matplotlib as mpl

COLORS = {
    # categorical slots in fixed order – series 1 is always blue, series 2 always orange
    "series_1": "#2a78d6",
    "series_2": "#eb6834",
    # diverging pair (polarity: above / below a reference value)
    "above": "#2a78d6",
    "below": "#e34948",
    # chart chrome and ink
    "surface": "#fcfcfb",
    "text_primary": "#0b0b0b",
    "text_secondary": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
}

MONTHS_PL = ["sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"]


def legend_outside(ax, **kwargs):
    """Legenda poza obszarem wykresu, przy jego prawym górnym rogu – nie zasłania danych."""
    return ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, **kwargs)


def apply_style():
    """Ustawia domyślny wygląd wykresów: jasne tło, cienkie linie, recesywna siatka, tytuł z lewej."""
    mpl.rcParams.update({
        "figure.figsize": (10, 4),
        "figure.dpi": 110,
        "figure.facecolor": COLORS["surface"],
        "axes.facecolor": COLORS["surface"],
        "savefig.facecolor": COLORS["surface"],
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
        "font.size": 10,
        "text.color": COLORS["text_primary"],
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlecolor": COLORS["text_primary"],
        "axes.titlepad": 12,
        "axes.labelcolor": COLORS["text_secondary"],
        "axes.edgecolor": COLORS["axis"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": COLORS["grid"],
        "grid.linewidth": 0.8,
        "grid.linestyle": "-",
        "xtick.color": COLORS["muted"],
        "ytick.color": COLORS["muted"],
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "legend.frameon": False,
        "legend.fontsize": 9,
        "legend.labelcolor": COLORS["text_secondary"],
    })

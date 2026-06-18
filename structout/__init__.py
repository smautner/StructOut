"""structout - Pretty-print data structures in the terminal.

Provides functions for rendering networkx graphs as ASCII art, numeric lists
as colored sparklines, 2D arrays as heatmaps, and scatter plots using braille
characters.
"""

from structout.graph import gprint, ginfo
from structout.intlist import dprint
from structout.intlist import lprint, npprint, iprint, doALine, str_to, scatter, plot, plot_braille, colorize
from structout.heatmap import heatmap
from structout.rna import RNAprint
import numpy as np


def hist(values: list[float], bins: int = 40, xlim: tuple[float, float] | None = None, color: str = '1') -> None:
    """Print a braille-character histogram of the given values.

    Args:
        values: Data to histogram.
        bins: Number of histogram bins.
        xlim: Optional (min, max) range for the x-axis.
        color: ANSI color code for the plot (empty string to disable).
    """
    val, _ = np.histogram(values, density=False, bins=bins, range=xlim)
    print(str_to(min(values) if not xlim else xlim[0]), end='|')
    text = plot_braille(np.arange(bins), val, rows=1, cols=bins // 2, xlim=np.array((0, bins)))[0]
    if color:
        text = colorize(text, '1')
    print(text, end='|')
    print(str_to(max(values) if not xlim else xlim[1]))

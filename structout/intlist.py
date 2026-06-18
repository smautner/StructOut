from __future__ import annotations

from typing import Callable

from scipy.sparse import csr_matrix as csr
import os
import numpy as np
import math

"""Functions for rendering numerical data as Unicode sparklines and braille plots in the terminal."""

DOT_POS: dict[tuple[int, int], int] = {
    (0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 6,
    (1, 0): 3, (1, 1): 4, (1, 2): 5, (1, 3): 7
}


def render_sparkline(
    values: np.ndarray,
    log: bool = False,
    chunk_operation: Callable[..., object] = max,
    showrange: bool = True,
    symbols: str = '▁▂▃▄▅▆▇█',
    colors: str = '0467',
    ylim: bool | tuple[float, float] = False,
    characterlimit: int = 99999,
) -> str:
    """Render a single sparkline string from numeric values.

    Args:
        values: Numeric array to visualize.
        log: If True, apply log2 scaling before binning.
        chunk_operation: Aggregation function used when downsampling to fit the character limit.
        showrange: If True, prepend and append the min/max range to the output.
        symbols: Block characters ordered from low to high intensity.
        colors: Single-character ANSI color codes to combine with symbols.
        ylim: Fixed y-axis range as (min, max), or False to auto-scale.
        characterlimit: Maximum number of characters in the output string.

    Returns:
        A formatted sparkline string.
    """
    values = np.array(values)
    pre, post, space = determine_characterlimit(values, characterlimit, showrange=showrange)
    values = horizontalsquish(values, space, chunk_operation)
    if log:
        values = np.log2(values)
    values = binning(values, count=len(symbols) * len(colors), ylim=ylim)
    symbols = decorate(values, symbols, colors)
    return pre + ''.join(symbols) + post


def determine_characterlimit(
    values: np.ndarray,
    characterlimit: int,
    showrange: bool = True,
    ignore_val_len: bool = False,
) -> tuple[str, str, int]:
    """Compute the available character space for a sparkline after accounting for range labels.

    Args:
        values: Numeric array used to compute the range prefix/suffix.
        characterlimit: Total character budget for the output line.
        showrange: If True, reserve space for min/max labels.
        ignore_val_len: If True, ignore the array length when computing available space.

    Returns:
        A tuple of (pre, post, space) where pre and post are range label strings
        and space is the number of characters available for the sparkline itself.
    """
    if showrange:
        pre = str_to(values.min()) + "|"
        post = "|" + str_to(values.max())
    else:
        pre = ''
        post = ''
    maxlength = getcolumns() - len(pre + post)
    characterlimit -= len(pre + post)

    space = min(maxlength, len(values)) if not ignore_val_len else maxlength
    return pre, post, space


def str_to(num: float) -> str:
    """
    copy pasta seems to work...
    Expresses a float in a string of exactly 5 characters.

    The function finds the best representation (integer, decimal, or scientific)
    that is at most 5 characters long, and then pads it with spaces to
    ensure the final string is exactly 5 characters.

    Args:
        num: The float number to express.

    Returns:
        A string representation of the number, 5 characters long.
    """
    # This variable will hold the generated string before padding
    result = ""

    # 1. Handle special cases first
    if math.isnan(num):
        result = "nan"
    elif math.isinf(num):
        result = "inf" if num > 0 else "-inf"
    elif num == 0:
        result = "0"
    else:
        # This variable will be set once a suitable representation is found
        found_rep = None

        # 2. Try simple integer representation
        if num == int(num):
            s_int = str(int(num))
            if len(s_int) <= 5:
                found_rep = s_int

        # 3. Try fixed-point decimal notation (if integer didn't work)
        if found_rep is None:
            for precision in range(4, -1, -1):
                s_float = f"{num:.{precision}f}"
                if -1 < num < 1:
                    s_float = s_float.lstrip('0') if num > 0 else "-" + s_float[2:]

                if len(s_float) <= 5:
                    found_rep = s_float.rstrip('.')
                    break # Exit loop once a representation is found

        # 4. Fallback to scientific notation
        if found_rep is None:
            for precision in range(2, -1, -1):
                s_sci = f"{num:.{precision}e}".replace('e+', 'e')
                if len(s_sci) <= 5:
                    found_rep = s_sci
                    break

        # 5. Absolute last resort
        if found_rep is None:
            s_sci_final = f"{num:.0e}".replace('e+', 'e')
            found_rep = s_sci_final[:5]

        result = found_rep

    # Pad with spaces if the length is smaller than 5
    return result.ljust(5)


def getcolumns() -> int:
    """Return the terminal width in columns, defaulting to 100 if unavailable.

    Returns:
        Number of terminal columns.
    """
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 100


def horizontalsquish(
    values: np.ndarray,
    desired_length: int,
    chunk_operation: Callable[..., object] = max,
) -> np.ndarray:
    """Downsample an array to a target length by applying an aggregation function to chunks.

    Args:
        values: Input numeric array.
        desired_length: Target length of the output array.
        chunk_operation: Function applied to each chunk (e.g. max, min, mean).

    Returns:
        A numpy array of length ``desired_length``.
    """
    length = len(values)
    if length <= desired_length:
        return values
    size = float(length) / desired_length
    values = [
        chunk_operation(values[int(i * size): int(math.ceil((i + 1) * size))])
        for i in range(desired_length)
    ]
    return np.array(values)


def binning(
    values: np.ndarray,
    count: int,
    ylim: tuple[float, float] | bool,
) -> np.ndarray:
    """Discretize continuous values into integer bin indices.

    Args:
        values: Input numeric array.
        count: Number of bins.
        ylim: Fixed (min, max) range, or False to use the array's own range.

    Returns:
        Integer array of bin indices (0-indexed).
    """
    mi, ma = ylim or (values.min(), values.max())
    bins = np.arange(mi, ma + .0001, ((ma + .0001) - mi) / count)
    bins[-1] += .0001
    return np.digitize(values, bins) - 1


def decorate(values: np.ndarray, symbols: str, colors: str) -> str:
    """Map integer bin indices to colored Unicode characters.

    Args:
        values: Integer array of bin indices.
        symbols: Block characters ordered from low to high intensity.
        colors: Single-character ANSI color codes to combine with symbols.

    Returns:
        A string of colored Unicode characters.
    """
    allcolors = [colorize(s, c) for s in symbols for c in colors]
    return ''.join([allcolors[i] for i in values])


def colorize(chr: str, col: str | tuple[float, float, float]) -> str:
    """Wrap a character with ANSI escape codes for terminal coloring.

    Args:
        chr: The character to colorize.
        col: A single-character ANSI color code (e.g. '4') or an (r, g, b) tuple
             with values in [0, 1].

    Returns:
        The character wrapped in ANSI color escape codes.
    """
    if isinstance(col, str):
        return '\x1b[1;3%s;48m%s\x1b[0m' % (col, chr)

    # 24 bit
    else:
        r, g, b = [str(int(c * 255)) for c in col]
        return "\x1b[38;2;" + r + ";" + g + ";" + b + "m" + chr + '\x1b[0m'


def lprint(values: np.ndarray, **kwargs: object) -> None:
    """Print a sparkline for the given values.

    Args:
        values: Numeric array to visualize.
        **kwargs: Additional keyword arguments passed to :func:`render_sparkline`.
    """
    print(render_sparkline(values, **kwargs))


def plot(x: np.ndarray, y: np.ndarray | bool = False, **z: object) -> None:
    """Plot either a sparkline or a scatter plot depending on arguments.

    Args:
        x: Numeric array (sparkline values if *y* is False, x-coordinates otherwise).
        y: If False, plot a sparkline of *x*. If an array, plot *x* vs *y*.
        **z: Additional keyword arguments passed to :func:`lprint` or :func:`scatter`.
    """
    if isinstance(y, bool):
        lprint(x, **z)
    else:
        scatter(x, y, **z)


def npprint(thing: np.ndarray, shareylim: bool = True, **kwargs: object) -> None:
    """Print each row of a 2D array as a sparkline.

    Args:
        thing: 2D numeric array (each row is rendered as a separate sparkline).
        shareylim: If True, all rows share the same y-axis range (global min/max).
        **kwargs: Additional keyword arguments passed to :func:`lprint`.
    """
    thing = csr(thing)
    if shareylim:
        kwargs['ylim'] = thing.min(), thing.max()
    for i in range(thing.shape[0]):
        a = thing.getrow(i).todense().getA1()
        lprint(a, **kwargs)


def iprint(
    dic: dict[float, float],
    bins: int = 1000,
    spacemin: float | bool = False,
    spacemax: float | bool = False,
    **kwargs: object,
) -> None:
    """Print a sparkline from an irregularly sampled dictionary of values.

    The dictionary keys are binned into ``bins`` evenly spaced buckets across
    the range [spacemin, spacemax], and the resulting sequence is rendered as
    a sparkline.

    Args:
        dic: Mapping of positions to values.
        bins: Number of bins to discretize the key space into.
        spacemin: Minimum of the key range, or False to use the actual minimum.
        spacemax: Maximum of the key range, or False to use the actual maximum.
        **kwargs: Additional keyword arguments passed to :func:`lprint`.
    """
    keys = np.array(list(dic.keys()))
    spacemin = spacemin or min(keys)
    spacemax = spacemax or max(keys)
    discrete = np.digitize(keys, bins=np.linspace(spacemin, spacemax, bins))

    base = [min(dic.values())] * (bins + 1)
    for k, e in zip(keys, discrete):
        base[e] = dic[k]
    lprint(base, **kwargs)


def dprint(posdict: dict[int, float], length: int = 100, chunk_operation: Callable[..., object] = max) -> None:
    """Print a sparkline from a sparse position-to-value dictionary.

    Args:
        posdict: Mapping of integer positions to numeric values.
        length: Desired output length in characters.
        chunk_operation: Aggregation function used when downsampling.
    """
    print(numberdict_to_str(posdict, length, chunk_operation=chunk_operation))


def numberdict_to_str(
    ndict: dict[int, float],
    dlength: int,
    chunk_operation: Callable[..., object] = max,
    symbols: str = '▁▂▃▄▅▆▇█',
    colors: str = '0467',
) -> str:
    """Convert a sparse position-to-value dictionary into a sparkline string.

    Args:
        ndict: Mapping of integer positions to numeric values.
        dlength: Desired output length in characters.
        chunk_operation: Aggregation function used when downsampling.
        symbols: Block characters ordered from low to high intensity.
        colors: Single-character ANSI color codes to combine with symbols.

    Returns:
        A sparkline string.
    """
    ret = resize_number_dict(ndict, desired_length=dlength, chunk_operation=chunk_operation)
    return "".join(decorate(np.array(ret), symbols, colors))


def access_region(d: dict[int, float], start: int, end: int) -> list[float]:
    """Return all values in a dictionary whose keys fall within [start, end].

    Args:
        d: Mapping of integer positions to numeric values.
        start: Start of the inclusive range.
        end: End of the inclusive range.

    Returns:
        List of values in the specified region.
    """
    return [v for pos, v in d.items() if start <= pos <= end]


def resize_number_dict(
    posdict: dict[int, float],
    desired_length: int,
    chunk_operation: Callable[..., object] = max,
) -> list[float]:
    """Downsample a sparse position dictionary to a fixed-length list.

    Args:
        posdict: Mapping of integer positions to numeric values.
        desired_length: Target length of the output list.
        chunk_operation: Aggregation function used when combining values within a chunk.

    Returns:
        A list of length ``desired_length``.
    """
    minn = min(posdict)
    maxx = max(posdict)
    length = maxx - minn
    size = float(length) / desired_length
    posdict = [
        chunk_operation([0] + access_region(posdict, int(i * size) + minn, int(math.ceil(i + 1) * size + minn)))
        for i in range(desired_length)
    ]
    return posdict


def scatter(
    x: np.ndarray,
    y: np.ndarray,
    xlim: tuple[float, float] = (),
    ylim: tuple[float, float] = (),
    rows: int = 2,
    columns: int = 14,
) -> None:
    """Print a braille scatter plot of x vs y with colored axis labels.

    The core plot is rendered using braille characters. Colored min/max labels
    are added for both axes: y-axis labels on the top row and x-axis labels on
    the bottom row.

    Args:
        x: X-coordinate values.
        y: Y-coordinate values.
        xlim: X-axis range as (min, max), or empty to auto-detect.
        ylim: Y-axis range as (min, max), or empty to auto-detect.
        rows: Number of braille-character rows for the plot area.
        columns: Number of braille-character columns for the plot area.
    """
    xlim = xlim or (np.min(x), np.max(x))
    ylim = ylim or (np.min(y), np.max(y))
    xlim = np.array(xlim)
    ylim = np.array(ylim)
    prex, postx, spacex = determine_characterlimit(xlim, 0000, ignore_val_len=True)
    prey, posty, _ = determine_characterlimit(ylim, 0000, ignore_val_len=True)
    maxl = lambda x, y: max(len(x), len(y))
    prelen = maxl(prex, prey)
    postlen = maxl(postx, posty)
    spacelen = len(prex + postx) + spacex - prelen - postlen
    spacelen = columns or spacelen

    chars = plot_braille(x, y, cols=spacelen, rows=rows, xlim=xlim, ylim=ylim)

    for i, row in enumerate(chars):
        pre, post = '', ''
        if i == 0:
            pre, post = prey, posty
        if i == len(chars) - 1:
            pre, post = prex, postx
        pre = pre.ljust(prelen)
        post = post.ljust(postlen)

        if i == 0:
            pre, post = colorize(pre, '4'), colorize(post, '4')
        if i == len(chars) - 1:
            pre, post = colorize(pre, '6'), colorize(post, '6')

        print(pre + row + post)


def plot_braille(
    x: np.ndarray,
    y: np.ndarray,
    rows: int = 20,
    cols: int = 40,
    xlim: tuple[float, float] = (),
    ylim: tuple[float, float] = (),
) -> list[str]:
    """Render x vs y data as a braille-character grid.

    Args:
        x: X-coordinate values.
        y: Y-coordinate values.
        rows: Number of braille-character rows.
        cols: Number of braille-character columns.
        xlim: X-axis range as (min, max), or empty to auto-detect.
        ylim: Y-axis range as (min, max), or empty to auto-detect.

    Returns:
        A list of strings, one per row, containing braille characters.

    Raises:
        ValueError: If x and y have different lengths.
    """
    if len(x) != len(y):
        raise ValueError("x and y must be the same length")

    if len(ylim) == 0:
        ylim = np.array((min(y), max(y)))

    if len(xlim) == 0:
        xlim = np.array((min(x), max(x)))
    # Scale data into pixel coordinates (cols*2 wide, rows*4 tall)
    x = np.asarray(x)
    y = -np.asarray(y)
    ylim = -ylim[::-1]

    # 2x4 pixel grid per Braille character
    width_px = cols * 2
    height_px = rows * 4
    x_bins = np.linspace(*xlim, width_px + 1)
    y_bins = np.linspace(*ylim, height_px + 1)

    x_idx = np.digitize(x, x_bins) - 1
    y_idx = np.digitize(y, y_bins) - 1

    # Clamp to grid bounds
    x_idx = np.clip(x_idx, 0, width_px - 1)
    y_idx = np.clip(y_idx, 0, height_px - 1)

    # Initialize Braille canvas
    canvas = np.zeros((rows, cols), dtype=np.uint8)

    for xi, yi in zip(x_idx, y_idx):
        char_col = xi // 2
        char_row = yi // 4
        dot_col = xi % 2
        dot_row = yi % 4

        dot_bit = DOT_POS[(dot_col, dot_row)]
        canvas[char_row, char_col] |= (1 << dot_bit)

    chars = ["".join(chr(0x2800 + cell) if cell else ' ' for cell in row) for row in canvas]
    return chars

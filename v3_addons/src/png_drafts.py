"""Deterministic, linear-axis PNG drafts using only NumPy and the stdlib.

Labels use an embedded uppercase bitmap font; unsupported characters show as
question marks. Nonfinite (x, y) pairs break lines and are counted, not imputed.
No images are produced on import. Output paths must stay inside v3_addons.
"""

from __future__ import annotations

import math
from pathlib import Path
import struct
import unicodedata
import zlib

import numpy as np

__all__ = ["line_plot"]

_WIDTH, _HEIGHT = 1600, 1000
_BACKGROUND = (246, 248, 251)
_WHITE = (255, 255, 255)
_NAVY = (24, 43, 65)
_TEAL = (0, 126, 134)
_AMBER = (189, 125, 20)
_SLATE = (91, 110, 129)
_GRID = (222, 229, 236)
_ROOT = Path(__file__).resolve().parents[1]

# Five columns by seven rows. A slash separates rows, not displayed text.
_FONT_ROWS = {
    " ": "00000/00000/00000/00000/00000/00000/00000",
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "D": "11110/10001/10001/10001/10001/10001/11110",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01111/10000/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "J": "00111/00010/00010/00010/10010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/10101/01010",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00010/00100/01000/11111",
    "3": "11110/00001/00001/01110/00001/00001/11110",
    "4": "00010/00110/01010/10010/11111/00010/00010",
    "5": "11111/10000/10000/11110/00001/00001/11110",
    "6": "01110/10000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00001/01110",
    ".": "00000/00000/00000/00000/00000/00110/00110",
    ",": "00000/00000/00000/00000/00110/00110/00100",
    ":": "00000/00110/00110/00000/00110/00110/00000",
    ";": "00000/00110/00110/00000/00110/00110/00100",
    "-": "00000/00000/00000/11111/00000/00000/00000",
    "_": "00000/00000/00000/00000/00000/00000/11111",
    "+": "00000/00100/00100/11111/00100/00100/00000",
    "=": "00000/00000/11111/00000/11111/00000/00000",
    "/": "00001/00001/00010/00100/01000/10000/10000",
    "\\": "10000/10000/01000/00100/00010/00001/00001",
    "(": "00010/00100/01000/01000/01000/00100/00010",
    ")": "01000/00100/00010/00010/00010/00100/01000",
    "[": "01110/01000/01000/01000/01000/01000/01110",
    "]": "01110/00010/00010/00010/00010/00010/01110",
    "{": "00011/00100/00100/01000/00100/00100/00011",
    "}": "11000/00100/00100/00010/00100/00100/11000",
    "%": "11001/11010/00100/00100/01000/10110/00110",
    "<": "00010/00100/01000/10000/01000/00100/00010",
    ">": "01000/00100/00010/00001/00010/00100/01000",
    "!": "00100/00100/00100/00100/00100/00000/00100",
    "?": "01110/10001/00001/00010/00100/00000/00100",
    "'": "00100/00100/00000/00000/00000/00000/00000",
    '"': "01010/01010/00000/00000/00000/00000/00000",
    "|": "00100/00100/00100/00100/00100/00100/00100",
    "*": "00000/10101/01110/11111/01110/10101/00000",
    "#": "01010/01010/11111/01010/11111/01010/01010",
    "&": "01100/10010/10100/01000/10101/10010/01101",
    "@": "01110/10001/10111/10101/10111/10000/01110",
    "$": "00100/01111/10100/01110/00101/11110/00100",
    "^": "00100/01010/10001/00000/00000/00000/00000",
    "~": "00000/00000/01001/10110/00000/00000/00000",
}
_FONT = {
    char: np.array([[cell == "1" for cell in row] for row in rows.split("/")])
    for char, rows in _FONT_ROWS.items()
}
_TRANSLATION = str.maketrans({
    "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u2264": "<=", "\u2265": ">=",
    "\u00d7": "X", "\u03bc": "MU", "\u00b5": "MU", "\u03c3": "SIGMA",
})


def _text(value):
    value = unicodedata.normalize("NFKD", str(value).translate(_TRANSLATION))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(value.upper().split())


def _text_width(text, scale):
    return max(0, (6 * len(text) - 1) * scale)


def _wrap(text, width, scale, max_lines=None):
    capacity = max(4, (width // scale + 1) // 6)
    lines, current = [], ""
    for word in _text(text).split():
        if current and len(current) + 1 + len(word) <= capacity:
            current += " " + word
            continue
        if current:
            lines.append(current)
            current = ""
        while len(word) > capacity:
            lines.append(word[:capacity])
            word = word[capacity:]
        current = word
    if current or not lines:
        lines.append(current)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:capacity - 3].rstrip() + "..."
    return lines


def _draw_text(canvas, text, x, y, color, scale=2, align="left", vertical=False):
    text = _text(text)
    mask = np.zeros((7 * scale, _text_width(text, scale)), dtype=bool)
    for index, char in enumerate(text):
        glyph = np.repeat(np.repeat(_FONT.get(char, _FONT["?"]), scale, 0), scale, 1)
        start = index * 6 * scale
        mask[:, start:start + 5 * scale] = glyph
    if vertical:
        mask = np.rot90(mask)
    height, width = mask.shape
    x = int(x - (width // 2 if align == "center" else width if align == "right" else 0))
    y = int(y)
    left, top = max(0, x), max(0, y)
    right, bottom = min(canvas.shape[1], x + width), min(canvas.shape[0], y + height)
    if right > left and bottom > top:
        region = canvas[top:bottom, left:right]
        region[mask[top - y:bottom - y, left - x:right - x]] = color


def _line(canvas, x0, y0, x1, y1, color, width=1, clip=None):
    steps = max(abs(int(x1) - int(x0)), abs(int(y1) - int(y0))) + 1
    xs = np.rint(np.linspace(x0, x1, steps)).astype(np.intp)
    ys = np.rint(np.linspace(y0, y1, steps)).astype(np.intp)
    left, top, right, bottom = clip or (0, 0, canvas.shape[1] - 1, canvas.shape[0] - 1)
    for dy in range(-(width // 2), width // 2 + 1):
        for dx in range(-(width // 2), width // 2 + 1):
            xx, yy = xs + dx, ys + dy
            valid = (xx >= left) & (xx <= right) & (yy >= top) & (yy <= bottom)
            canvas[yy[valid], xx[valid]] = color


def _dot(canvas, x, y, color, radius=4, clip=None):
    left, top, right, bottom = clip or (0, 0, canvas.shape[1] - 1, canvas.shape[0] - 1)
    x0, x1 = max(left, x - radius), min(right, x + radius)
    y0, y1 = max(top, y - radius), min(bottom, y + radius)
    if x0 <= x1 and y0 <= y1:
        yy, xx = np.ogrid[y0:y1 + 1, x0:x1 + 1]
        canvas[y0:y1 + 1, x0:x1 + 1][(xx - x) ** 2 + (yy - y) ** 2 <= radius ** 2] = color


def _limits(requested, low, high, axis):
    if requested is not None:
        raw = np.asarray(requested)
        if np.iscomplexobj(raw):
            raise ValueError(f"{axis}_limits must be real, not complex")
        values = np.asarray(raw, dtype=float)
        if values.shape != (2,):
            raise ValueError(f"{axis}_limits must contain exactly two numbers")
        low, high = map(float, values)
    elif low is None:
        low, high = 0.0, 1.0  # Explicitly disclosed as placeholder axes in the plot.
    else:
        span = float(high - low)
        if not math.isfinite(span):
            raise ValueError(f"{axis} axis span exceeds float precision; rescale the data")
        padding = span * 0.04 if span else (abs(low) * 0.05 if low else 0.5)
        with np.errstate(over="ignore", invalid="ignore"):
            spacings = [abs(float(np.spacing(value))) for value in (low, high)]
        padding = max([padding] + [value for value in spacings if math.isfinite(value)])
        largest = float(np.finfo(float).max)
        low, high = max(-largest, low - padding), min(largest, high + padding)
    if not (math.isfinite(low) and math.isfinite(high) and low < high):
        raise ValueError(f"{axis}_limits must be finite and strictly increasing")
    if not math.isfinite(high - low):
        raise ValueError(f"{axis} axis span exceeds float precision; rescale the data")
    return low, high


def _ticks(limits, target=6):
    low, high = limits
    span = high - low
    exponent = math.floor(math.log10(span) - math.log10(target))
    unit = 10.0 ** exponent
    if unit == 0:
        return [low, high]
    fraction = (span / unit) / target
    multiplier = next((v for v in (1.0, 2.0, 2.5, 5.0, 10.0) if v >= fraction), 10.0)
    step = multiplier * unit
    first, last = math.ceil(low / step), math.floor(high / step)
    values = []
    for index in range(first, min(last + 1, first + 20)):
        value = index * step
        if abs(value) < step * 1e-10:
            value = 0.0
        if low <= value <= high and (not values or value > values[-1]):
            values.append(value)
    return values if len(values) >= 2 else [low, high]


def _tick_labels(values):
    for precision in range(6, 18):
        labels = []
        for value in values:
            label = format(value, f".{precision}g") if value else "0"
            if "e" in label:
                mantissa, exponent = label.split("e")
                label = f"{mantissa}E{int(exponent):+d}"
            labels.append(label)
        if len(set(labels)) == len(labels):
            return labels
    raise ValueError("Axis ticks cannot be distinguished; rescale the data")


def _clip_segment(x0, y0, x1, y1):
    """Cohen-Sutherland clipping in normalized coordinates, preserving gaps."""
    def code(x, y):
        return (1 if x < 0 else 2 if x > 1 else 0) | (4 if y < 0 else 8 if y > 1 else 0)

    def fraction(boundary, start, end):
        scale = max(abs(start), abs(end), abs(boundary), 1.0)
        return (boundary / scale - start / scale) / (end / scale - start / scale)

    for _ in range(12):
        c0, c1 = code(x0, y0), code(x1, y1)
        if not (c0 | c1):
            return x0, y0, x1, y1
        if c0 & c1:
            return None
        outside = c0 or c1
        if outside & 12:
            y = 1.0 if outside & 8 else 0.0
            t = fraction(y, y0, y1)
            x = (1 - t) * x0 + t * x1
        else:
            x = 1.0 if outside & 2 else 0.0
            t = fraction(x, x0, x1)
            y = (1 - t) * y0 + t * y1
        if outside == c0:
            x0, y0 = x, y
        else:
            x1, y1 = x, y
    raise ValueError("Segment clipping lost precision; rescale the data")


def _chunk(kind, payload):
    crc = zlib.crc32(payload, zlib.crc32(kind)) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _write_png(path, canvas):
    height, width, _ = canvas.shape
    compressor = zlib.compressobj(level=6)
    blocks = []
    for row in canvas:
        blocks.append(compressor.compress(b"\x00" + row.tobytes()))
    blocks.append(compressor.flush())
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"pHYs", struct.pack(">IIB", 3780, 3780, 1))
        + _chunk(b"IDAT", b"".join(blocks))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


def line_plot(path, title, x_label, y_label, series, x_limits=None, y_limits=None):
    """Write a 1600x1000 RGB PNG and return its resolved pathlib.Path.

    ``series`` is a list of dicts with ``label``, one-dimensional numeric ``x``
    and ``y`` sequences of equal length, and an integer RGB ``color`` (0..255).
    Segments follow input order, never connect across NaN/Inf, and are clipped
    to the limits. Single finite points remain visible. Auto limits use finite
    pairs only; empty data get explicitly marked placeholder axes, not zeros.
    Existing parent directories are required. Excessively long/many legend
    labels raise ValueError rather than silently dropping a series.
    """
    path = Path(path).resolve()
    if not path.is_relative_to(_ROOT) or path.suffix.lower() != ".png":
        raise ValueError("PNG output must be a .png file inside v3_addons")
    if not path.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {path.parent}")
    if not isinstance(series, list):
        raise TypeError("series must be a list of dictionaries")
    if not all(isinstance(value, str) for value in (title, x_label, y_label)):
        raise TypeError("title and axis labels must be strings")

    prepared = []
    extrema = [None, None, None, None]
    valid_count = missing_count = 0
    for index, item in enumerate(series):
        if not isinstance(item, dict) or not {"label", "x", "y", "color"}.issubset(item):
            raise ValueError(f"series[{index}] needs label, x, y, and color")
        if not isinstance(item["label"], str):
            raise TypeError(f"series[{index}].label must be a string")
        raw_x, raw_y = np.asarray(item["x"]), np.asarray(item["y"])
        if np.iscomplexobj(raw_x) or np.iscomplexobj(raw_y):
            raise ValueError(f"series[{index}] x/y must be real, not complex")
        x, y = np.asarray(raw_x, dtype=float), np.asarray(raw_y, dtype=float)
        if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape:
            raise ValueError(f"series[{index}] x/y must be equal-length 1-D sequences")
        color = np.asarray(item["color"])
        if (color.shape != (3,) or color.dtype.kind not in "iu"
                or np.any(color < 0) or np.any(color > 255)):
            raise ValueError(f"series[{index}].color must be three integers in 0..255")
        finite = np.isfinite(x) & np.isfinite(y)
        count = int(np.count_nonzero(finite))
        missing = len(x) - count
        valid_count += count
        missing_count += missing
        if count:
            bounds = (float(x[finite].min()), float(x[finite].max()),
                      float(y[finite].min()), float(y[finite].max()))
            for slot, value in enumerate(bounds):
                if extrema[slot] is None:
                    extrema[slot] = value
                else:
                    extrema[slot] = (min if slot % 2 == 0 else max)(extrema[slot], value)
        prepared.append({"label": item["label"], "x": x, "y": y, "finite": finite,
                         "count": count, "missing": missing, "color": tuple(map(int, color))})

    x_range = _limits(x_limits, extrema[0], extrema[1], "x")
    y_range = _limits(y_limits, extrema[2], extrema[3], "y")
    xticks, yticks = _ticks(x_range), _ticks(y_range)
    xlabels, ylabels = _tick_labels(xticks), _tick_labels(yticks)
    yscale = 3 if max(_text_width(label, 3) for label in ylabels) <= 200 else 2
    left = max(190, 112 + max(_text_width(label, yscale) for label in ylabels))
    right, bottom = 1198, 802
    title_lines = _wrap(title, 1472, 4, 3)
    subtitle_y = 40 + 40 * len(title_lines) + 8
    top = subtitle_y + 62
    if left >= right - 350:
        raise ValueError("Y-axis numbers are too wide; rescale the data")
    xscale = 3 if max(_text_width(label, 3) for label in xlabels) <= 200 else 2
    spacing = max(_text_width(label, xscale) for label in xlabels) + 24
    if len(xticks) > 2:
        stride = max(1, math.ceil(spacing * (len(xticks) - 1) / (right - left)))
        xticks, xlabels = xticks[::stride], xlabels[::stride]

    # All legend entries must fit; do not conceal data by omitting labels.
    legend_x, legend_width = 1254, 296
    for legend_scale in (3, 2):
        legend_entries = []
        for item in prepared:
            lines = _wrap(item["label"] or "(UNLABELED)", legend_width - 50, legend_scale)
            status = "NO FINITE PAIRS" if not item["count"] else (
                f"{item['missing']} NONFINITE" if item["missing"] else "")
            item_height = len(lines) * (9 * legend_scale) + (24 if status else 0) + 20
            legend_entries.append((item, lines, status, item_height))
        if sum(entry[3] for entry in legend_entries) <= bottom - top - 46:
            break
    else:
        raise ValueError("Legend does not fit; shorten labels or split the plot")

    outside_count = 0
    for item in prepared:
        finite = item["finite"]
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            u = (item["x"][finite] - x_range[0]) / (x_range[1] - x_range[0])
            v = (item["y"][finite] - y_range[0]) / (y_range[1] - y_range[0])
        if not (np.isfinite(u).all() and np.isfinite(v).all()):
            raise ValueError("Finite values exceed axis projection precision; rescale the data")
        outside_count += int(np.count_nonzero((u < 0) | (u > 1) | (v < 0) | (v > 1)))
        item["u"] = np.full(item["x"].shape, np.nan)
        item["v"] = np.full(item["y"].shape, np.nan)
        item["u"][finite], item["v"][finite] = u, v

    canvas = np.full((_HEIGHT, _WIDTH, 3), _BACKGROUND, dtype=np.uint8)
    canvas[:10] = _TEAL
    for index, text in enumerate(title_lines):
        _draw_text(canvas, text, 64, 40 + index * 40, _NAVY, 4)
    _draw_text(canvas, "DRAFT | LINEAR AXES | PROVIDED SERIES ONLY", 64, subtitle_y, _SLATE, 2)
    canvas[top:bottom + 1, left:right + 1] = _WHITE
    plot_box = (left, top, right, bottom)

    def pixel(u, v):
        return round(left + u * (right - left)), round(bottom - v * (bottom - top))

    for value, label in zip(xticks, xlabels):
        x, _ = pixel((value - x_range[0]) / (x_range[1] - x_range[0]), 0)
        _line(canvas, x, top, x, bottom, _GRID)
        _line(canvas, x, bottom, x, bottom + 7, _SLATE)
        _draw_text(canvas, label, x, bottom + 17, _SLATE, xscale, "center")
    for value, label in zip(yticks, ylabels):
        _, y = pixel(0, (value - y_range[0]) / (y_range[1] - y_range[0]))
        _line(canvas, left, y, right, y, _GRID)
        _line(canvas, left - 7, y, left, y, _SLATE)
        _draw_text(canvas, label, left - 16, y - 7 * yscale // 2, _SLATE, yscale, "right")
    _line(canvas, left, top, left, bottom, _SLATE, 1)
    _line(canvas, left, bottom, right, bottom, _SLATE, 1)
    _line(canvas, left, top, right, top, _GRID, 1)
    _line(canvas, right, top, right, bottom, _GRID, 1)

    visible = False
    for item in prepared:
        u, v, finite, color = item["u"], item["v"], item["finite"], item["color"]
        # Only adjacent original indices form a segment: NaN/Inf create gaps.
        for index in np.flatnonzero(finite[:-1] & finite[1:]):
            segment = _clip_segment(float(u[index]), float(v[index]),
                                    float(u[index + 1]), float(v[index + 1]))
            if segment is not None:
                x0, y0 = pixel(*segment[:2])
                x1, y1 = pixel(*segment[2:])
                _line(canvas, x0, y0, x1, y1, color, 3, plot_box)
                visible = True
        inside = finite & (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
        for index in np.flatnonzero(inside):
            x, y = pixel(float(u[index]), float(v[index]))
            _dot(canvas, x, y, color, 4, plot_box)
            visible = True

    if not visible:
        message = ("NO FINITE (X, Y) PAIRS TO PLOT" if not valid_count
                   else "NO DATA VISIBLE WITHIN LIMITS")
        _draw_text(canvas, message, (left + right) // 2, (top + bottom) // 2 - 20,
                   _SLATE, 3, "center")
        if not valid_count and (x_limits is None or y_limits is None):
            _draw_text(canvas, "DEFAULT 0..1 AXES ARE PLACEHOLDERS, NOT OBSERVATIONS",
                       (left + right) // 2, (top + bottom) // 2 + 20, _AMBER, 2, "center")

    for index, text in enumerate(_wrap(x_label, right - left, 3, 2)):
        _draw_text(canvas, text, (left + right) // 2, 857 + index * 29, _NAVY, 3, "center")
    for index, text in enumerate(_wrap(y_label, bottom - top, 3, 2)):
        height = _text_width(text, 3)
        _draw_text(canvas, text, 30 + index * 30, (top + bottom - height) // 2,
                   _NAVY, 3, vertical=True)

    _draw_text(canvas, "SERIES", legend_x, top, _NAVY, 3)
    legend_y = top + 46
    if not prepared:
        _draw_text(canvas, "NONE SUPPLIED", legend_x, legend_y, _SLATE, 2)
    for item, lines, status, item_height in legend_entries:
        sample_y = legend_y + 7 * legend_scale // 2
        _line(canvas, legend_x, sample_y, legend_x + 32, sample_y, item["color"], 3)
        _dot(canvas, legend_x + 16, sample_y, item["color"], 4)
        for index, text in enumerate(lines):
            _draw_text(canvas, text, legend_x + 50, legend_y + index * 9 * legend_scale,
                       _NAVY, legend_scale)
        if status:
            _draw_text(canvas, status, legend_x + 50, legend_y + len(lines) * 9 * legend_scale,
                       _SLATE, 2)
        legend_y += item_height

    _line(canvas, 64, 926, 1536, 926, _GRID)
    summary = (f"VALID PAIRS: {valid_count} | NONFINITE PAIRS: {missing_count} "
               f"(GAPS NOT JOINED) | SAMPLES OUTSIDE LIMITS: {outside_count}")
    for index, text in enumerate(_wrap(summary, 1472, 2, 2)):
        _draw_text(canvas, text, 64, 942 + index * 21, _SLATE, 2)
    _write_png(path, canvas)
    return path

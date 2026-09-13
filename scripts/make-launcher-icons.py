"""Generate Android launcher icons for Every Day, no third-party libs.

Two families:

  ic_launcher_foreground.png  — RGBA, transparent. This is the adaptive-icon
      foreground layer, drawn on a 108dp canvas of which only the central 72dp
      is guaranteed visible (the launcher masks the rest), so the grid is sized
      to sit well inside that safe zone.

  ic_launcher.png / _round.png — RGB, opaque dark background. Legacy icons for
      pre-adaptive launchers; the round variant is circle-masked.
"""
import zlib, struct, math, os, sys

BG = (0x0b, 0x0b, 0x0e)
AMB = (0xe8, 0xa3, 0x3d)
UNLIT = 0.30
LIT = {0, 1, 2, 3, 4, 5}          # six lit, three outlines — an unbroken run
SS = 3

DENSITIES = [("mdpi", 1.0), ("hdpi", 1.5), ("xhdpi", 2.0), ("xxhdpi", 3.0), ("xxxhdpi", 4.0)]

# The canonical design, identical to the web/PWA icons: a 180-unit canvas with a
# 3x3 grid spanning 98 units (54%). Everything else is derived from it by scale,
# so the launcher icon and the web icon are the same drawing at different sizes.
D_UNITS, D_CELL, D_GAP, D_RADIUS, D_STROKE = 180.0, 26.0, 10.0, 7.0, 2.6


def geom(units):
    """Scale the canonical design onto a canvas of `units`."""
    k = units / D_UNITS
    return D_CELL * k, D_GAP * k, D_RADIUS * k, D_STROKE * k


def sdf(px, py, cx, cy, half, r):
    dx, dy = abs(px - cx) - (half - r), abs(py - cy) - (half - r)
    return math.hypot(max(dx, 0.0), max(dy, 0.0)) + min(max(dx, dy), 0.0) - r


def render(size, units, cell_u, gap_u, radius_u, stroke_u, alpha, circle):
    """units = canvas size in design units; geometry given in those units."""
    s = size / float(units)
    span = 3 * cell_u + 2 * gap_u
    start = (units - span) / 2.0
    ch = 4 if alpha else 3

    if alpha:
        rows = [bytearray(size * 4) for _ in range(size)]        # transparent
    else:
        rows = [bytearray(BG * size) for _ in range(size)]

    if not alpha and circle:
        cx = cy = size / 2.0
        rad = size / 2.0
        for y in range(size):
            row = rows[y]
            for x in range(size):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) - rad
                if d > 0.7:
                    row[x * 3:x * 3 + 3] = bytes((0, 0, 0))

    for idx in range(9):
        r_, c_ = divmod(idx, 3)
        cx = (start + c_ * (cell_u + gap_u) + cell_u / 2.0) * s
        cy = (start + r_ * (cell_u + gap_u) + cell_u / 2.0) * s
        half, rad = (cell_u / 2.0) * s, radius_u * s
        lit = idx in LIT
        stroke = stroke_u * s
        pad = 2 + int(stroke)
        x0, x1 = max(0, int(cx - half) - pad), min(size, int(cx + half) + pad + 1)
        y0, y1 = max(0, int(cy - half) - pad), min(size, int(cy + half) + pad + 1)

        for y in range(y0, y1):
            row = rows[y]
            for x in range(x0, x1):
                hits = 0
                for sy in range(SS):
                    py = y + (sy + 0.5) / SS
                    for sx in range(SS):
                        px = x + (sx + 0.5) / SS
                        d = sdf(px, py, cx, cy, half, rad)
                        if (d <= 0.0) if lit else (abs(d) <= stroke / 2.0):
                            hits += 1
                if not hits:
                    continue
                a = hits / float(SS * SS)
                if not lit:
                    a *= UNLIT
                o = x * ch
                if alpha:
                    prev_a = row[o + 3] / 255.0
                    new_a = a + prev_a * (1 - a)
                    for k in range(3):
                        src = AMB[k]
                        dst = row[o + k]
                        row[o + k] = int(round((src * a + dst * prev_a * (1 - a)) / new_a)) if new_a else 0
                    row[o + 3] = int(round(new_a * 255))
                else:
                    for k in range(3):
                        row[o + k] = int(round(row[o + k] + (AMB[k] - row[o + k]) * a))
    return rows, ch


def write_png(path, size, rows, ch):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)
    color_type = 6 if ch == 4 else 2
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, color_type, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


res = sys.argv[1]
for name, mult in DENSITIES:
    d = os.path.join(res, "mipmap-" + name)

    # Adaptive foreground on a 108dp canvas. Using the canonical proportions
    # means the launcher's safe-zone crop lands exactly where it did on the
    # maskable PWA icon, so the two look the same on the home screen.
    fg = int(round(108 * mult))
    c, g, r, st = geom(108)
    rows, ch = render(fg, 108, c, g, r, st, alpha=True, circle=False)
    write_png(os.path.join(d, "ic_launcher_foreground.png"), fg, rows, ch)

    # Legacy square + round at 48dp, same proportions, opaque.
    lg = int(round(48 * mult))
    c, g, r, st = geom(48)
    rows, ch = render(lg, 48, c, g, r, st, alpha=False, circle=False)
    write_png(os.path.join(d, "ic_launcher.png"), lg, rows, ch)
    rows, ch = render(lg, 48, c, g, r, st, alpha=False, circle=True)
    write_png(os.path.join(d, "ic_launcher_round.png"), lg, rows, ch)

    print("%-9s foreground %dpx, legacy %dpx" % (name, fg, lg))

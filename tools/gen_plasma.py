#!/usr/bin/env python3
"""Render tokens/tokens.json into the Plasma desktop themes.

Writes plasma/desktoptheme/platinum-neue-light and platinum-neue-dark. Neutral surfaces use the
token colours directly, because the mockup's frame colour runs the opposite way in dark mode from
any colour-scheme role. Accent elements use the ColorScheme-Highlight class, so they follow the
system accent.

Every frame is a set of 9-slice elements (prefix-topleft … prefix-bottomright) that is built
geometrically, piece by piece, so element bounds are exact. Optional pieces: shadow-*, hint-*-margin.

Usage: python3 tools/gen_plasma.py
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text())
OUT = ROOT / "plasma" / "desktoptheme"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


HL = "HL"  # marker: paint with the ColorScheme-Highlight class


def paint(colour, opacity=1.0):
    """SVG fill attributes for a colour (hex or HL)."""
    op = f' fill-opacity="{opacity:g}"' if opacity < 1 else ""
    if colour == HL:
        return f'fill="currentColor" class="ColorScheme-Highlight"{op}'
    return f'fill="{colour}"{op}'


class Sheet:
    """One SVG document; frames are stacked vertically on a canvas."""

    def __init__(self):
        self.parts = []
        self.defs = []
        self.y = 0
        self.uid = 0

    def element(self, eid, x, y, w, h, body=""):
        # an invisible rect pins the element bounds to the full tile
        self.parts.append(f'<g id="{eid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none"/>{body}</g>')

    def hint(self, eid, size):
        """hint-*-margin elements: a rect whose width (or height) is the margin."""
        self.parts.append(f'<rect id="{eid}" x="0" y="{self.y}" width="{size}" height="{size}" fill="none"/>')
        self.y += size + 2

    def insets(self, v=1):
        """hint-*-inset: how far inside the tile edge the visible frame starts. Plasma sizes popup
        padding as margin - inset and extends PlasmoidHeading by that padding; without these hints it
        assumes about the edge-tile size and headings stop short. v = 1 (the border width) puts
        headings exactly inside the popup's border, which stays visible on every side."""
        y = self.y
        self.parts.append(f'<rect id="hint-left-inset" x="0" y="{y}" width="{v}" height="4" fill="none"/>')
        self.parts.append(f'<rect id="hint-right-inset" x="2" y="{y}" width="{v}" height="4" fill="none"/>')
        self.parts.append(f'<rect id="hint-top-inset" x="4" y="{y}" width="4" height="{v}" fill="none"/>')
        self.parts.append(f'<rect id="hint-bottom-inset" x="4" y="{y + 2}" width="4" height="{v}" fill="none"/>')
        self.y += 6

    def flag(self, eid):
        self.parts.append(f'<rect id="{eid}" x="0" y="{self.y}" width="1" height="1" fill="none"/>')
        self.y += 3

    def frame(self, prefix, fill=None, border=None, hi=None, shade=None, r=3, c=4, m=4, border_width=1,
              fill_opacity=1.0, border_opacity=1.0, margins=None, open_top=None, open_bottom=None, inset=(0, 0, 0, 0),
              shade2=None, cast=None, hi_left=None, lo=None, tint=None):
        """A rounded 9-slice frame. c = corner tile size, m = edge/centre tile size.
        fill/border/hi/shade are colours (or None). hi is a 1px light line inside the top edge
        (raised); shade is a 1px dark line inside the top edge (inset).
        shade2: a second, softer inset line below shade (deeper well).
        cast: a 1px shadow just below the bottom edge, drawn in the inset band (needs inset bottom >= 1).
        hi_left / lo: Platinum's inner bevel: a lit line inside the left edge (with hi along the top), and
        a shadow line inside the bottom and right edges.
        tint: a (colour, opacity) wash over the fill, under the border and edge lines.
        open_top/open_bottom: that side is square and drawn as a hairline of the given colour, or a
        (colour, opacity) pair (used by popup heading/footer strips that cover the popup's own edge)."""
        p = f"{prefix}-" if prefix else ""
        x0, y0 = 0, self.y
        bw = border_width
        # inset = transparent band (top, bottom, left, right) between the tile edge and the drawing
        it, ib, il, ir = inset
        cols = [(0, c + il), (c + il, m), (c + il + m, c + ir)]   # x offset, width (tile)
        rows = [(0, c + it), (c + it, m), (c + it + m, c + ib)]
        names = [["topleft", "top", "topright"], ["left", "center", "right"], ["bottomleft", "bottom", "bottomright"]]
        ri = max(r - bw, 0)
        W = 2 * c + m

        def corner_paths(fx, fy, ox=0, oy=0):
            """Paths for the top-left corner, mirrored by fx/fy (0 or 1) into the c×c square at (ox,oy).
            Absolute coordinates, no transforms: KSvg places transformed pieces wrongly at fractional scales."""
            def P(x, y):
                return (ox + (c - x if fx else x), oy + (c - y if fy else y))

            sweep = 1 if fx == fy else 0
            nsweep = 1 - sweep

            def pt(x, y):
                X, Y = P(x, y)
                return f"{X:g},{Y:g}"
            # outer shape, inner (inside the border) shape
            outer = f"M{pt(0, c)} L{pt(0, r)} A{r},{r} 0 0 {sweep} {pt(r, 0)} L{pt(c, 0)} L{pt(c, c)} Z"
            if ri > 0:
                inner = f"M{pt(bw, c)} L{pt(bw, r)} A{ri},{ri} 0 0 {sweep} {pt(r, bw)} L{pt(c, bw)} L{pt(c, c)} Z"
                ring = (f"M{pt(0, c)} L{pt(0, r)} A{r},{r} 0 0 {sweep} {pt(r, 0)} L{pt(c, 0)} L{pt(c, bw)} L{pt(r, bw)} "
                        f"A{ri},{ri} 0 0 {nsweep} {pt(bw, r)} L{pt(bw, c)} Z")
            else:
                inner = f"M{pt(bw, c)} L{pt(bw, bw)} L{pt(c, bw)} L{pt(c, c)} Z"
                ring = f"M{pt(0, c)} L{pt(0, 0)} L{pt(c, 0)} L{pt(c, bw)} L{pt(bw, bw)} L{pt(bw, c)} Z"
            return outer, inner, ring

        for ri_, (ry, rh) in enumerate(rows):
            for ci, (cx, cw) in enumerate(cols):
                rh = rows[ri_][1]
                name = names[ri_][ci]
                TX, TY, TW, TH = x0 + cx, y0 + ry, cw, rh
                X, Y = TX + (il if ci == 0 else 0), TY + (it if ri_ == 0 else 0)
                cw = TW - (il if ci == 0 else ir if ci == 2 else 0)
                rh = TH - (it if ri_ == 0 else ib if ri_ == 2 else 0)
                body = []
                corner = ri_ != 1 and ci != 1
                hair = open_bottom if ri_ == 2 else open_top if ri_ == 0 else None
                if hair:
                    hair_c, hair_o = hair if isinstance(hair, tuple) else (hair, 1.0)
                    if fill:
                        body.append(f'<rect x="{X}" y="{Y}" width="{cw}" height="{rh}" {paint(fill, fill_opacity)}/>')
                    body.append(f'<rect x="{X}" y="{Y + rh - 1 if ri_ == 2 else Y}" width="{cw}" height="1" {paint(hair_c, hair_o)}/>')
                    if border and ci != 1:
                        body.append(f'<rect x="{X if ci == 0 else X + cw - bw}" y="{Y}" width="{bw}" height="{rh}" {paint(border)}/>')
                elif corner:
                    fx, fy = (1 if ci == 2 else 0), (1 if ri_ == 2 else 0)
                    outer, inner, ring = corner_paths(fx, fy, X, Y)
                    g = []
                    if fill:
                        g.append(f'<path d="{inner if border else outer}" {paint(fill, fill_opacity)}/>')
                    if tint:
                        g.append(f'<path d="{inner if border else outer}" {paint(*tint)}/>')
                    if border:
                        g.append(f'<path d="{ring}" {paint(border, border_opacity)}/>')
                    if fy == 0:
                        lx0, lx1 = (r, c) if fx == 0 else (0, c - r)
                        if hi:
                            g.append(f'<rect x="{X + lx0}" y="{Y + bw}" width="{lx1 - lx0}" height="1" {paint(hi)}/>')
                        if shade:
                            g.append(f'<rect x="{X + lx0}" y="{Y + bw}" width="{lx1 - lx0}" height="1" {paint(shade)}/>')
                        if shade2:
                            g.append(f'<rect x="{X + lx0}" y="{Y + bw + 1}" width="{lx1 - lx0}" height="1" {paint(shade2)}/>')
                    elif cast:
                        cx0, cx1 = (r, c) if fx == 0 else (0, c - r)
                        g.append(f'<rect x="{X + cx0}" y="{Y + c}" width="{cx1 - cx0}" height="1" {paint(cast)}/>')
                    # inner bevel: segments from the end of the corner curve to the tile edge
                    vy0, vy1 = (r, c) if fy == 0 else (0, c - r)        # vertical run, outside the curve
                    hx0, hx1 = (r, c) if fx == 0 else (0, c - r)        # horizontal run, outside the curve
                    if hi_left and fx == 0 and vy1 > vy0:
                        g.append(f'<rect x="{X + bw}" y="{Y + vy0}" width="1" height="{vy1 - vy0}" {paint(hi_left)}/>')
                    if lo and fx == 1 and vy1 > vy0:
                        g.append(f'<rect x="{X + c - bw - 1}" y="{Y + vy0}" width="1" height="{vy1 - vy0}" {paint(lo)}/>')
                    if lo and fy == 1 and hx1 > hx0:
                        g.append(f'<rect x="{X + hx0}" y="{Y + c - bw - 1}" width="{hx1 - hx0}" height="1" {paint(lo)}/>')
                    body.append("".join(g))
                else:
                    # edges and centre: fill + 1px border strip on the outer side
                    if fill:
                        body.append(f'<rect x="{X}" y="{Y}" width="{cw}" height="{rh}" {paint(fill, fill_opacity)}/>')
                    if tint:
                        body.append(f'<rect x="{X}" y="{Y}" width="{cw}" height="{rh}" {paint(*tint)}/>')
                    if border and name != "center":
                        if name == "top":
                            bx, by, bwid, bh = X, Y, cw, bw
                        elif name == "bottom":
                            bx, by, bwid, bh = X, Y + rh - bw, cw, bw
                        elif name == "left":
                            bx, by, bwid, bh = X, Y, bw, rh
                        else:
                            bx, by, bwid, bh = X + cw - bw, Y, bw, rh
                        if fill and fill_opacity == 1:
                            pass
                        body.append(f'<rect x="{bx}" y="{by}" width="{bwid}" height="{bh}" {paint(border, border_opacity)}/>')
                    if name == "top":
                        for col in (hi, shade):
                            if col:
                                body.append(f'<rect x="{X}" y="{Y + bw}" width="{cw}" height="1" {paint(col)}/>')
                        if shade2:
                            body.append(f'<rect x="{X}" y="{Y + bw + 1}" width="{cw}" height="1" {paint(shade2)}/>')
                    if name == "bottom" and cast:
                        body.append(f'<rect x="{X}" y="{Y + rh}" width="{cw}" height="1" {paint(cast)}/>')
                    if name == "left" and hi_left:
                        body.append(f'<rect x="{X + bw}" y="{Y}" width="1" height="{rh}" {paint(hi_left)}/>')
                    if name == "right" and lo:
                        body.append(f'<rect x="{X + cw - bw - 1}" y="{Y}" width="1" height="{rh}" {paint(lo)}/>')
                    if name == "bottom" and lo:
                        body.append(f'<rect x="{X}" y="{Y + rh - bw - 1}" width="{cw}" height="1" {paint(lo)}/>')
                self.element(p + name, TX, TY, TW, TH, "".join(body))
        self.y += W + it + ib + 4
        if margins:
            margins = [v + d for v, d in zip(margins, inset)]
            for side, v in zip(("top", "bottom", "left", "right"), margins):
                self.hint(f"{p}hint-{side}-margin", v)

    def shadow(self, alpha, size=14, offset=3):
        """shadow-* tiles: a soft falloff around the frame, reaching further below than above.

        KWin places each tile with its outer edge `margin` px outside the window and the rest
        beneath it (Breeze: 16px tiles, 10px margins). So every tile must be at least as deep as
        its margin, or a gap opens between the window and its shadow. Here every tile is T deep,
        and each gradient runs from the window edge (inside the tile) out to the margin."""
        mt, mb, ml, mr = size - offset, size + offset, size, size
        T = max(mt, mb, ml, mr) + 4
        y0 = self.y
        stops = (f'<stop offset="0" stop-color="#000" stop-opacity="{alpha:g}"/>'
                 f'<stop offset="0.3" stop-color="#000" stop-opacity="{alpha * 0.45:g}"/>'
                 f'<stop offset="0.7" stop-color="#000" stop-opacity="{alpha * 0.1:g}"/>'
                 f'<stop offset="1" stop-color="#000" stop-opacity="0"/>')
        # window edge position inside each tile, measured from the tile origin
        ex = {"left": ml, "right": T - mr}
        ey = {"top": mt, "bottom": T - mb}
        tiles = {
            "topleft": (0, 0), "top": (T, 0), "topright": (2 * T, 0),
            "left": (0, T), "center": (T, T), "right": (2 * T, T),
            "bottomleft": (0, 2 * T), "bottom": (T, 2 * T), "bottomright": (2 * T, 2 * T),
        }
        for name, (tx, ty) in tiles.items():
            X, Y = tx, y0 + ty
            if name == "center":
                self.element(f"shadow-{name}", X, Y, T, T)
                continue
            self.uid += 1
            gid = f"sg{self.uid}"
            v = next((k for k in ("top", "bottom") if name.startswith(k)), None)
            h = next((k for k in ("left", "right") if name.endswith(k)), None)
            if v and h:   # corner: elliptical falloff centred on the window corner
                cx, cy = X + ex[h], Y + ey[v]
                rx, ry = (ml if h == "left" else mr), (mt if v == "top" else mb)
                self.defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" '
                                 f'gradientTransform="translate({cx} {cy}) scale({rx} {ry})">{stops}</radialGradient>')
            elif v:       # top/bottom edge: from the window edge out to the margin
                outer = Y if v == "top" else Y + T
                self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{X}" y1="{Y + ey[v]}" '
                                 f'x2="{X}" y2="{outer}">{stops}</linearGradient>')
            else:
                outer = X if h == "left" else X + T
                self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{X + ex[h]}" y1="{Y}" '
                                 f'x2="{outer}" y2="{Y}">{stops}</linearGradient>')
            self.element(f"shadow-{name}", X, Y, T, T, f'<rect x="{X}" y="{Y}" width="{T}" height="{T}" fill="url(#{gid})"/>')
        self.y += 3 * T + 4
        for side, m in (("top", mt), ("bottom", mb), ("left", ml), ("right", mr)):
            self.hint(f"shadow-hint-{side}-margin", m)

    def write(self, path):
        w, h = 80, self.y + 4
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
               f'<style type="text/css" id="current-color-scheme">.ColorScheme-Highlight{{color:#4C5BD4;}}</style>'
               f'<defs>{"".join(self.defs)}</defs>' + "\n".join(self.parts) + "</svg>\n")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg)


def build(mode):
    t = TOKENS["modes"][mode]
    dark = mode == "dark"
    hi = mix(t["raised"], "#FFFFFF", 0.06 if dark else 0.85)        # lit top edge
    chrome_hi = mix(t["chrome"], "#FFFFFF", 0.05 if dark else 0.8)
    shade = mix(t["chrome2"], "#000000", 0.25 if dark else 0.08)     # inset top edge
    shadow_a = 0.5 if dark else 0.2
    out = OUT / f"platinum-neue-{mode}"
    if out.exists():
        shutil.rmtree(out)

    # Platinum bevel colours: a lit line inside the top/left edges, a shadow line inside bottom/right
    pressed = mix(t["chrome"], "#000000", 0.38) if dark else mix(t["chrome"], t["text"], 0.15)
    pressed_edge = mix(t["line"], "#000000", 0.35) if dark else mix(t["line"], t["text"], 0.25)
    press_shade = mix(pressed, "#000000", 0.43 if dark else 0.18)
    press_shade2 = mix(pressed, "#000000", 0.2 if dark else 0.08)
    panel_hi = mix(t["chrome"], "#FFFFFF", 0.14 if dark else 0.8)
    panel_lo = mix(t["chrome"], "#000000", 0.35) if dark else mix(t["chrome"], t["text"], 0.12)
    btn_hi = mix(t["raised"], "#FFFFFF", 0.12 if dark else 0.85)
    btn_lo = mix(t["raised"], "#000000", 0.3) if dark else mix(t["raised"], t["text"], 0.1)
    pop_hi = mix(t["raised"], "#FFFFFF", 0.1 if dark else 0.85)
    pop_lo = mix(t["raised"], "#000000", 0.3) if dark else mix(t["raised"], t["text"], 0.08)

    # panel: a classic bevel. Docked at the screen edge, Plasma draws only its top tiles, so the rim is
    # the frame-coloured edge and a clearly lit line; when floating, the sides and bottom close the bevel.
    s = Sheet()
    s.frame("", fill=t["chrome"], border=t["frame"], hi=panel_hi, hi_left=panel_hi, lo=panel_lo, margins=(2, 2, 3, 3))
    s.shadow(shadow_a, size=10, offset=2)
    s.write(out / "widgets" / "panel-background.svg")

    # popups and desktop widgets: raised sheets with the same inner bevel, and a deeper shadow
    for rel in ("dialogs/background.svg", "widgets/background.svg"):
        s = Sheet()
        s.frame("", fill=t["raised"], border=t["frame"], hi=pop_hi, hi_left=pop_hi, lo=pop_lo, margins=(8, 8, 8, 8))
        s.insets(1e-8)
        s.shadow(0.6 if dark else 0.26, size=16, offset=3)
        s.write(out / rel)

    # tooltips: same surface (panel tooltips draw with window colours), tighter margins
    s = Sheet()
    s.frame("", fill=t["raised"], border=t["frame"], hi=pop_hi, hi_left=pop_hi, lo=pop_lo, r=2, margins=(6, 6, 8, 8))
    s.shadow(shadow_a * 0.9, size=10, offset=2)
    s.write(out / "widgets" / "tooltip.svg")

    # task manager: real buttons. Open windows are raised like the apps' push buttons, the active window
    # is pushed in, minimized windows are recessed, launchers (no frame) stay flat; hover lifts
    s = Sheet()
    m = (1, 1, 6, 6)
    cast = mix(t["chrome"], "#000000", 0.45 if dark else 0.16)
    # Even 4px gutters: above, below and between buttons. The panel's 2px rim (frame line + lit line) sits
    # on the side facing the desktop, so that side's inset is 2px deeper; Plasma asks for "<edge>-<state>"
    # first, then "<state>". The cast shadow is drawn inside the bottom gutter.
    focus_tint = (HL, 0.42 if dark else 0.3)
    for loc, ti in (("", (6, 4, 2, 2)), ("south-", (6, 4, 2, 2)), ("north-", (4, 6, 2, 2)),
                    ("west-", (2, 2, 4, 6)), ("east-", (2, 2, 6, 4))):
        s.frame(f"{loc}normal", fill=t["raised"], border=t["line"], hi=btn_hi, hi_left=btn_hi, lo=btn_lo, cast=cast,
                margins=m, inset=ti)
        s.frame(f"{loc}hover", fill=t["raisedHover"], border=t["line"], hi=btn_hi, hi_left=btn_hi, lo=btn_lo, cast=cast,
                margins=m, inset=ti)
        # the active window: pushed in, washed and outlined in the accent colour
        s.frame(f"{loc}focus", fill=pressed, tint=focus_tint, border=HL, shade=press_shade, shade2=press_shade2,
                margins=m, inset=ti)
        s.frame(f"{loc}minimized", fill=mix(t["chrome"], t["chrome2"], 0.6), border=mix(t["line"], t["chrome"], 0.45),
                shade=shade, margins=m, inset=ti)
        s.frame(f"{loc}attention", fill=mix(t["raised"], t["neutral"], 0.25), border=t["neutral"], hi=btn_hi,
                hi_left=btn_hi, lo=btn_lo, cast=cast, margins=m, inset=ti)
        s.frame(f"{loc}progress", fill=HL, fill_opacity=0.3, margins=m, inset=ti)
    s.write(out / "widgets" / "tasks.svg")

    # buttons in popups
    s = Sheet()
    s.frame("normal", fill=t["raised"], border=t["line"], hi=btn_hi, hi_left=btn_hi, lo=btn_lo, margins=(4, 4, 8, 8))
    # pressed: a clearly darker face, firmer edge, two-step shadow under the top (colours defined above)
    s.frame("pressed", fill=pressed, border=pressed_edge, shade=press_shade, shade2=press_shade2, margins=(5, 3, 8, 8))
    s.frame("hover", fill=t["raisedHover"], border=t["line"], hi=btn_hi, hi_left=btn_hi, lo=btn_lo, margins=(4, 4, 8, 8))
    s.frame("focus", fill=t["raised"], border=HL, hi=hi, margins=(4, 4, 8, 8))
    s.frame("toolbutton-hover", fill=t["raised"], border=t["line"], hi=hi, margins=(4, 4, 4, 4))
    s.frame("toolbutton-pressed", fill=pressed, border=pressed_edge, shade=press_shade, shade2=press_shade2, margins=(5, 3, 4, 4))
    s.frame("toolbutton-focus", border=HL, margins=(4, 4, 4, 4))
    s.write(out / "widgets" / "button.svg")

    # text fields: inset well
    s = Sheet()
    s.flag("hint-focus-over-base")
    s.frame("base", fill=t["content"], border=t["line"], shade=mix(t["content"], t["lineStrong"], 0.18), margins=(4, 4, 6, 6))
    s.frame("hover", border=t["line"], margins=(4, 4, 6, 6))
    s.frame("focus", border=HL, border_width=2, margins=(4, 4, 6, 6))
    s.frame("focusframe", border=HL, border_width=2, margins=(4, 4, 6, 6))
    s.write(out / "widgets" / "lineedit.svg")

    # list items in popups: soft accent wash, so text keeps its colour
    s = Sheet()
    s.frame("normal", margins=(4, 4, 6, 6))
    s.frame("hover", fill=HL, fill_opacity=0.12, r=2, margins=(4, 4, 6, 6))
    s.frame("selected", fill=HL, fill_opacity=0.22, border=HL, border_opacity=0.55, r=2, margins=(4, 4, 6, 6))
    s.frame("selected+hover", fill=HL, fill_opacity=0.3, border=HL, border_opacity=0.7, r=2, margins=(4, 4, 6, 6))
    s.write(out / "widgets" / "viewitem.svg")

    # tab bars and the "applet open" indicator in the panel: pressed in, like an open tray item
    s = Sheet()
    for loc in ("north", "south", "east", "west"):
        s.frame(f"{loc}-active-tab", fill=pressed, border=pressed_edge, shade=press_shade, shade2=press_shade2, margins=(3, 1, 6, 6), inset=(4, 4, 1, 1))
    s.write(out / "widgets" / "tabbar.svg")

    # ---- controls in popups (volume, brightness, battery, network…) ----
    on_accent = TOKENS["accents"][TOKENS["accents"]["default"]]["onDark" if dark else "onLight"]
    well_shade = mix(t["chrome2"], t["lineStrong"], 0.25 if dark else 0.12)

    # slider: inset groove, accent fill, raised rectangular handle with a grip line (as in the app style)
    s = Sheet()
    s.frame("groove", fill=t["chrome2"], border=t["line"], shade=well_shade, r=2, c=3, m=3)
    s.frame("groove-highlight", fill=HL, r=2, c=3, m=3)
    hw, hh = 12, 20

    def handle(eid, w, h, fill, border, grip_vertical, y):
        body = (f'<rect x="1.5" y="{y + 0.5}" width="{w - 3}" height="{h - 2}" rx="2" fill="{fill}" stroke="{border}"/>'
                f'<rect x="3" y="{y + 1.5}" width="{w - 6}" height="1" fill="{hi}"/>')
        if grip_vertical:
            body += f'<rect x="{w / 2 - 0.5}" y="{y + h / 2 - 4.5}" width="1" height="8" fill="{t["line"]}"/>'
        else:
            body += f'<rect x="{w / 2 - 4}" y="{y + h / 2 - 1}" width="8" height="1" fill="{t["line"]}"/>'
        # cast shadow under the handle
        body = f'<rect x="1.5" y="{y + 1.5}" width="{w - 3}" height="{h - 2}" rx="2" fill="{cast}"/>' + body
        s.element(eid, 0, y, w, h, body)

    for orient, (w, h, gv) in (("horizontal", (hw, hh, True)), ("vertical", (hh, hw, False))):
        for state, fill, border in (("handle", t["raised"], t["line"]), ("hover", t["raisedHover"], t["line"]),
                                    ("focus", t["raised"], HL)):
            y = s.y
            if state == "focus":
                body = f'<rect x="0.5" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="3" fill="none" stroke="currentColor" class="ColorScheme-Highlight" stroke-width="1"/>'
                s.element(f"{orient}-slider-focus", 0, y, w, h, body)
            else:
                handle(f"{orient}-slider-{state}", w, h, fill, border, gv, y)
            s.y += h + 2
        s.element(f"{orient}-slider-shadow", 0, s.y, w, h)
        s.y += h + 2
    s.parts.append(f'<rect id="hint-handle-size" x="40" y="0" width="{hw}" height="{hh}" fill="none"/>')
    s.write(out / "widgets" / "slider.svg")

    # progress bars: inset well, accent fill
    s = Sheet()
    s.parts.append('<rect id="hint-bar-size" x="60" y="0" width="8" height="8" fill="none"/>')
    s.frame("bar-inactive", fill=t["chrome2"], border=t["line"], shade=well_shade, r=2, c=3, m=3)
    s.frame("bar-active", fill=HL, r=2, c=3, m=3)
    s.write(out / "widgets" / "bar_meter_horizontal.svg")

    # scrollbars: sunken track, raised thumb (thumb sits 3px inside the track)
    s = Sheet()
    s.parts.append('<rect id="hint-scrollbar-size" x="60" y="0" width="20" height="20" fill="none"/>')
    for orient in ("vertical", "horizontal"):
        s.frame(f"background-{orient}", fill=t["chrome2"], border=t["lineSoft"], r=2, c=3, m=3)
    s.frame("slider", fill=t["raised"], border=t["line"], hi=hi, r=2, c=3, m=3)
    s.frame("mouseover-slider", fill=t["raisedHover"], border=t["line"], hi=hi, r=2, c=3, m=3)
    for pre in ("slider", "mouseover-slider"):
        for side in ("top", "bottom", "left", "right"):
            s.hint(f"{pre}-hint-{side}-inset", 3)
    s.write(out / "widgets" / "scrollbar.svg")

    # switch: pill track (inset when off, accent when on), raised round knob
    s = Sheet()
    s.flag("hint-stretch-borders")
    s.parts.append('<rect id="hint-bar-size" x="60" y="0" width="32" height="16" fill="none"/>')
    for pre, fill, border in (("inactive", t["chrome2"], t["line"]), ("active", HL, None)):
        y = s.y
        fattr = paint(fill)
        # left cap (0..8), centre (8..12), right cap (12..20), all 16 tall; stroke centred on the half-pixel
        # caps: filled half-disc plus a filled 1px ring for the outline (strokes pad the bounds)
        def cap(x0, sweep):
            ring = (f'<path d="M{x0},{y} A8,8 0 0 {sweep} {x0},{y + 16} L{x0},{y + 15} A7,7 0 0 {1 - sweep} {x0},{y + 1} Z" fill="{border}"/>'
                    if border else "")
            return f'<path d="M{x0},{y} A8,8 0 0 {sweep} {x0},{y + 16} Z" {fattr}/>' + ring
        s.element(f"{pre}-left", 0, y, 8, 16, cap(8, 0))
        s.element(f"{pre}-center", 8, y, 4, 16, f'<rect x="8" y="{y}" width="4" height="16" {fattr}/>'
                  + (f'<rect x="8" y="{y}" width="4" height="1" fill="{border}"/><rect x="8" y="{y + 15}" width="4" height="1" fill="{border}"/>' if border else ""))
        s.element(f"{pre}-right", 12, y, 8, 16, cap(12, 1))
        s.y += 18
    for eid, fill in (("handle", t["raised"]), ("handle-hover", t["raisedHover"]), ("handle-pressed", t["chrome2"])):
        y = s.y
        s.element(eid, 0, y, 16, 16, f'<circle cx="8" cy="{y + 8.5}" r="7" fill="{cast}"/>'
                  f'<circle cx="8" cy="{y + 8}" r="7" fill="{fill}" stroke="{t["line"]}"/>')
        s.y += 18
    y = s.y
    s.element("handle-focus", 0, y, 18, 18, f'<circle cx="9" cy="{y + 9}" r="8.5" fill="none" stroke="currentColor" class="ColorScheme-Highlight"/>')
    s.y += 20
    s.element("handle-shadow", 0, s.y, 18, 18)
    s.y += 20
    s.write(out / "widgets" / "switch.svg")

    # radio buttons: inset circle, accent when checked, light dot
    s = Sheet()
    s.parts.append('<rect id="hint-size" x="60" y="0" width="16" height="16" fill="none"/>')
    y = s.y
    s.element("normal", 0, y, 16, 16, f'<circle cx="8" cy="{y + 8}" r="7.5" fill="{t["content"]}" stroke="{t["line"]}" stroke-width="1"/>'
              f'<path d="M3.2,{y + 4.5} A6.5,6.5 0 0 1 12.8,{y + 4.5}" fill="none" stroke="{well_shade}"/>')
    s.y += 18
    y = s.y
    s.element("checked", 0, y, 16, 16, f'<circle cx="8" cy="{y + 8}" r="7.5" {paint(HL)}/>')
    s.y += 18
    y = s.y
    s.element("hover", 0, y, 16, 16, f'<circle cx="8" cy="{y + 8}" r="7" fill="none" stroke="{t["lineStrong"]}" stroke-opacity="0.5"/>')
    s.y += 18
    y = s.y
    s.element("focus", 0, y, 20, 20, f'<circle cx="10" cy="{y + 10}" r="9.5" fill="none" stroke="currentColor" class="ColorScheme-Highlight"/>')
    s.y += 22
    y = s.y
    s.element("symbol", 0, y, 6, 6, f'<circle cx="3" cy="{y + 3}" r="2.5" fill="{on_accent}"/>')
    s.y += 8
    s.element("shadow", 0, s.y, 16, 16)
    s.y += 18
    s.write(out / "widgets" / "radiobutton.svg")

    # check marks (drawn on the button frame for checkboxes, and in menus): plain tick and dot
    s = Sheet()
    y = s.y
    s.element("checkbox", 0, y, 16, 16, f'<path d="M3.5,{y + 8.5} L6.5,{y + 11.5} L12.5,{y + 4.5}" fill="none" stroke="{t["text"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    s.y += 18
    y = s.y
    s.element("radiobutton", 0, y, 16, 16, f'<circle cx="8" cy="{y + 8}" r="3" fill="{t["text"]}"/>')
    s.y += 18
    s.write(out / "widgets" / "checkmarks.svg")

    # popup heading and footer strips: they cover the popup's own edge, so they carry its border
    s = Sheet()
    s.flag("hint-stretch-borders")
    # headings sit just inside the popup's 1px border (dialog insets = 1), so they draw no border of
    # their own: fill, the lit top line, and a hairline where they meet the popup body
    # Popup headings reach the popup edge (dialog insets = 0), but Plasma decides per popup whether a
    # heading draws its side borders, and gets it wrong in some (clock calendar, Kickoff corners). So the
    # heading is a translucent darkening over the popup instead of an opaque strip: the popup's own
    # border, rounded corners and lit edge always show through, and the band still reads as chrome.
    tint = 0.2 if dark else 0.058                       # raised -> chrome
    hair = ("#FFFFFF", 0.09) if dark else ("#000000", 0.13)
    s.frame("header", fill="#000000", fill_opacity=tint, open_bottom=hair, margins=(6, 6, 8, 8))
    s.frame("footer", fill="#000000", fill_opacity=tint, open_top=hair, margins=(6, 6, 8, 8))
    s.write(out / "widgets" / "plasmoidheading.svg")

    name = f"Platinum Neue {mode.capitalize()}"
    meta = {
        "KPlugin": {
            "Authors": [{"Name": "Platinum Neue"}],
            "Description": f"Quiet, tactile Platinum descendant ({mode})",
            "Id": f"platinum-neue-{mode}",
            "License": "GPL-2.0-or-later",
            "Name": name,
            "Version": "0.1",
        },
        "X-Plasma-API": "5.0",
    }
    (out / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")
    # no translucency: one opaque look everywhere
    (out / "plasmarc").write_text("[AdaptiveTransparency]\nenabled=false\n\n[ContrastEffect]\nenabled=false\n\n[BlurBehindEffect]\nenabled=false\n")
    print(out)


LAYOUT_JS = """// Platinum Neue: a plain, full-width bottom panel with a serif clock
loadTemplate("org.kde.plasma.desktop.defaultPanel")

var panel = panels()[0];
if (panel) {
    panel.location = "bottom";
    panel.height = %(panelHeight)d;
    panel.floating = false;
    var clocks = panel.widgets("org.kde.plasma.digitalclock");
    for (var i = 0; i < clocks.length; i++) {
        var c = clocks[i];
        c.currentConfigGroup = ["Appearance"];
        c.writeConfig("autoFontAndSize", false);
        c.writeConfig("fontFamily", "%(serif)s");
        c.writeConfig("fontWeight", 500);
        c.writeConfig("fontSize", 13);
        c.writeConfig("dateDisplayFormat", "BesideTime");
        c.writeConfig("dateFormat", "custom");
        c.writeConfig("customDateFormat", "ddd d MMM");
    }
}
"""


def qfont(family, size, weight=400):
    # Qt 6 QFont::toString: family,pointSize,pixelSize,styleHint,weight,style,underline,strike,fixedPitch,…
    return f"{family},{size},-1,5,{weight},0,0,0,0,0,0,0,0,0,0,1"


def build_lnf(mode):
    f = TOKENS["fonts"]
    ui, small = f["ui"]["family"], f["ui"]["small"]
    size = f["ui"]["size"]
    pid = f"org.platinumneue.{mode}.desktop"
    out = ROOT / "plasma" / "look-and-feel" / pid
    if out.exists():
        shutil.rmtree(out)
    c = out / "contents"
    (c / "layouts").mkdir(parents=True)
    scheme = f"PlatinumNeue{mode.capitalize()}"
    (c / "defaults").write_text(f"""[kdeglobals][KDE]
widgetStyle=PlatinumNeue

[kdeglobals][General]
ColorScheme={scheme}
font={qfont(ui, size)}
menuFont={qfont(ui, size)}
toolBarFont={qfont(ui, size)}
smallestReadableFont={qfont(ui, small)}

[kdeglobals][WM]
activeFont={qfont(ui, f["ui"]["title"], 600)}

[plasmarc][Theme]
name=platinum-neue-{mode}

[kwinrc][org.kde.kdecoration2]
library=org.kde.platinumneue
theme=

[ksplashrc][KSplash]
Engine=KSplashQML
Theme=org.kde.breeze.desktop
""")
    prev = ROOT / "plasma" / "previews" / f"{mode}.png"
    if prev.exists():
        (c / "previews").mkdir()
        shutil.copy(prev, c / "previews" / "preview.png")
        shutil.copy(prev, c / "previews" / "fullscreenpreview.jpg")
    (c / "layouts" / "org.kde.plasma.desktop-layout.js").write_text(
        LAYOUT_JS % {"panelHeight": TOKENS["metrics"]["panelHeight"], "serif": f["serif"]["family"]})
    meta = {
        "KPackageStructure": "Plasma/LookAndFeel",
        "KPlugin": {
            "Authors": [{"Name": "Platinum Neue"}],
            "Category": "",
            "Description": f"Platinum Neue {mode}: app style, window decoration, Plasma theme, colours and fonts",
            "Id": pid,
            "License": "GPL-2.0-or-later",
            "Name": f"Platinum Neue {mode.capitalize()}",
            "Version": "0.1",
        },
        "X-Plasma-MainScript": "defaults",
    }
    (out / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")
    print(out)


if __name__ == "__main__":
    for mode in ("light", "dark"):
        build(mode)
        build_lnf(mode)

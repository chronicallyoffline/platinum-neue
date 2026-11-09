#!/usr/bin/env python3
"""Render tokens/tokens.json into the Platinum Neue GTK 3 / GTK 4 theme.

Writes gtk/Platinum-Neue (gtk.css = light, gtk-dark.css = dark) and gtk/Platinum-Neue-Dark.

The theme builds on Breeze GTK (installed by breeze-gtk): it imports Breeze for complete widget
coverage, then restyles the controls with Platinum shapes - raised buttons with a lit top edge,
inset fields, folder tabs, a 20px scrollbar with a gripped thumb. It takes its colours from the
*_breeze named colours, the same ones Plasma (kde-gtk-config) writes from the active colour scheme
into ~/.config/gtk-{3,4}.0/colors.css, so GTK apps follow the scheme and system accent just as Qt
apps do. Token values are defined as fallbacks for use outside Plasma.

libadwaita apps ignore GTK themes; they still pick up the colour scheme through Plasma.

Usage: python3 tools/gen_gtk.py
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text())
OUT = ROOT / "gtk"
BREEZE = "/usr/share/themes/Breeze"

# the named colours Breeze GTK uses (and kde-gtk-config overrides from the colour scheme)
BREEZE_NAMES = """borders_breeze content_view_bg_breeze error_color_backdrop_breeze error_color_breeze
error_color_insensitive_backdrop_breeze error_color_insensitive_breeze insensitive_base_color_breeze
insensitive_base_fg_color_breeze insensitive_bg_color_breeze insensitive_borders_breeze insensitive_fg_color_breeze
insensitive_selected_bg_color_breeze insensitive_selected_fg_color_breeze insensitive_unfocused_bg_color_breeze
insensitive_unfocused_fg_color_breeze insensitive_unfocused_selected_bg_color_breeze
insensitive_unfocused_selected_fg_color_breeze link_color_breeze link_visited_color_breeze
success_color_backdrop_breeze success_color_breeze success_color_insensitive_backdrop_breeze
success_color_insensitive_breeze theme_base_color_breeze theme_bg_color_breeze
theme_button_background_backdrop_breeze theme_button_background_backdrop_insensitive_breeze
theme_button_background_insensitive_breeze theme_button_background_normal_breeze
theme_button_decoration_focus_backdrop_breeze theme_button_decoration_focus_backdrop_insensitive_breeze
theme_button_decoration_focus_breeze theme_button_decoration_focus_insensitive_breeze
theme_button_decoration_hover_backdrop_breeze theme_button_decoration_hover_backdrop_insensitive_breeze
theme_button_decoration_hover_breeze theme_button_decoration_hover_insensitive_breeze
theme_button_foreground_active_backdrop_breeze theme_button_foreground_active_backdrop_insensitive_breeze
theme_button_foreground_active_breeze theme_button_foreground_active_insensitive_breeze
theme_button_foreground_backdrop_breeze theme_button_foreground_backdrop_insensitive_breeze
theme_button_foreground_insensitive_breeze theme_button_foreground_normal_breeze theme_fg_color_breeze
theme_header_background_backdrop_breeze theme_header_background_breeze theme_header_background_light_breeze
theme_header_foreground_backdrop_breeze theme_header_foreground_breeze theme_header_foreground_insensitive_backdrop_breeze
theme_header_foreground_insensitive_breeze theme_hovering_selected_bg_color_breeze theme_selected_bg_color_breeze
theme_selected_fg_color_breeze theme_text_color_breeze theme_titlebar_background_backdrop_breeze
theme_titlebar_background_breeze theme_titlebar_background_light_breeze theme_titlebar_foreground_backdrop_breeze
theme_titlebar_foreground_breeze theme_titlebar_foreground_insensitive_backdrop_breeze
theme_titlebar_foreground_insensitive_breeze theme_unfocused_base_color_breeze theme_unfocused_bg_color_breeze
theme_unfocused_fg_color_breeze theme_unfocused_selected_bg_color_alt_breeze theme_unfocused_selected_bg_color_breeze
theme_unfocused_selected_fg_color_breeze theme_unfocused_text_color_breeze theme_unfocused_view_bg_color_breeze
theme_unfocused_view_text_color_breeze theme_view_active_decoration_color_breeze
theme_view_hover_decoration_color_breeze tooltip_background_breeze tooltip_border_breeze tooltip_text_breeze
unfocused_borders_breeze unfocused_insensitive_borders_breeze warning_color_backdrop_breeze warning_color_breeze
warning_color_insensitive_backdrop_breeze warning_color_insensitive_breeze""".split()


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def fallback_colours(mode):
    """Token values for every Breeze named colour (used when Plasma doesn't supply colors.css)."""
    t = TOKENS["modes"][mode]
    acc = TOKENS["accents"][TOKENS["accents"]["default"]]
    accent, on = acc[mode], acc["onDark" if mode == "dark" else "onLight"]
    status = {"error": t["negative"], "warning": t["neutral"], "success": t["positive"]}
    border = mix(t["chrome"], t["text"], 0.25)
    out = {}
    for n in BREEZE_NAMES:
        kind = next((k for k in status if n.startswith(k)), None)
        if n.startswith("tooltip"):
            v = {"background": t["tipBg"], "text": t["tipFg"], "border": mix(t["tipBg"], t["tipFg"], 0.2)}[n.split("_")[1]]
        elif kind:
            v = mix(status[kind], t["chrome"], 0.6) if "insensitive" in n else status[kind]
        elif "insensitive" in n:
            if "fg" in n or "foreground" in n:
                v = t["textDisabled"]
            elif "border" in n:
                v = mix(t["chrome"], t["text"], 0.15)
            elif "base" in n:
                v = t["contentAlt"]
            else:
                v = mix(t["chrome"], t["chrome2"], 0.5)
        elif "selected_fg" in n:
            v = on
        elif "selected_bg" in n or "decoration" in n:
            v = accent
        elif "border" in n:
            v = border
        elif "button_background" in n:
            v = t["raised"]
        elif "base" in n or "view_bg" in n:
            v = t["content"]
        elif "link_visited" in n:
            v = t["visited"]
        elif "link" in n:
            v = t["link"]
        elif "fg" in n or "foreground" in n or "text" in n:
            v = t["text"]
        else:
            v = t["chrome"]
        out[n] = v
    return out


# light/dark constants, mirroring Helper in src/kstyle/platinumneuehelper.cpp
VARIANT = {
    "light": {
        "pn_hi": "rgba(255, 255, 255, 0.95)",          # bevelHighlight
        "pn_shade": "rgba(40, 36, 30, 0.12)",           # bevelShade
        "pn_inset_top": "mix(@pn_window, @pn_text, 0.62)",
        "pn_sunken": "mix(@pn_window, @pn_text, 0.06)",
        "pn_pressed": "mix(@pn_window, @pn_text, 0.15)",
        "pn_pressed_edge": "mix(@pn_line, @pn_text, 0.25)",
        "pn_press_shade": "rgba(0, 0, 0, 0.18)",
        "pn_press_shade2": "rgba(0, 0, 0, 0.08)",
        "pn_button_hover": "mix(@pn_button, #ffffff, 0.35)",
        "pn_accent_edge": "mix(@pn_accent, #000000, 0.25)",
        "pn_popup_shadow": "rgba(0, 0, 0, 0.22)",
        "pn_destructive": "@error_color_breeze",
    },
    "dark": {
        "pn_hi": "rgba(255, 255, 255, 0.06)",
        "pn_shade": "rgba(0, 0, 0, 0.4)",
        "pn_inset_top": "#141312",
        "pn_sunken": "mix(@pn_window, #000000, 0.2)",
        "pn_pressed": "mix(@pn_window, #000000, 0.38)",
        "pn_pressed_edge": "mix(@pn_line, #000000, 0.35)",
        "pn_press_shade": "rgba(0, 0, 0, 0.43)",
        "pn_press_shade2": "rgba(0, 0, 0, 0.2)",
        "pn_button_hover": "mix(@pn_button, #ffffff, 0.06)",
        "pn_accent_edge": "mix(@pn_accent, #000000, 0.35)",
        "pn_popup_shadow": "rgba(0, 0, 0, 0.5)",
        "pn_destructive": "mix(@error_color_breeze, #000000, 0.35)",
    },
}

# palette roles (resolved from the Breeze names, so they follow the colour scheme)
ROLES = """
@define-color pn_window @theme_bg_color_breeze;
@define-color pn_text @theme_fg_color_breeze;
@define-color pn_button @theme_button_background_normal_breeze;
@define-color pn_button_fg @theme_button_foreground_normal_breeze;
@define-color pn_content @theme_base_color_breeze;
@define-color pn_content_fg @theme_text_color_breeze;
@define-color pn_accent @theme_selected_bg_color_breeze;
@define-color pn_on_accent @theme_selected_fg_color_breeze;
@define-color pn_focus @theme_button_decoration_focus_breeze;
@define-color pn_disabled_fg @theme_button_foreground_insensitive_breeze;
@define-color pn_line mix(@pn_window, @pn_text, 0.5);
@define-color pn_line_soft mix(@pn_window, @pn_text, 0.16);
@define-color pn_line_disabled mix(@pn_window, @pn_line, 0.6);
@define-color pn_separator mix(@pn_button, @pn_line, 0.55);
@define-color pn_grip mix(@pn_button, @pn_line, 0.8);
@define-color pn_tab_fg mix(@pn_text, @pn_window, 0.3);
@define-color pn_tab_line mix(@pn_window, @pn_line, 0.7);
"""

# Platinum restyle, shared by GTK 3 and GTK 4. FOCUS is :focus (GTK 3) or :focus-visible (GTK 4).
# Selectors repeat Breeze's own where Breeze is more specific, so these rules win.
RULES = """
/* ---------- buttons: raised, lit from above; pressed = sunken ---------- */
button {
  border: 1px solid @pn_line;
  border-radius: 3px;
  background: @pn_button;
  color: @pn_button_fg;
  box-shadow: inset 0 1px @pn_hi, 0 1px @pn_shade;
  padding: 4px 10px;
  min-height: 20px;
  outline-color: alpha(@pn_focus, 0.9); }
button.image-button { padding: 4px 6px; }
button:backdrop { background: @pn_button; box-shadow: inset 0 1px @pn_hi, 0 1px @pn_shade; }
button:hover, button:hover:not(:checked):not(:active) { background: @pn_button_hover; border-color: @pn_line; }
button:focus { border-color: @pn_line; }
button:active, button:checked, button:checked:backdrop {
  background: @pn_pressed; border-color: @pn_pressed_edge;
  box-shadow: inset 0 1px @pn_press_shade, inset 0 2px @pn_press_shade2, inset 1px 0 alpha(#000000, 0.06);
  padding-top: 5px; padding-bottom: 3px; }
button:disabled, button:disabled:backdrop {
  background: mix(@pn_button, @pn_window, 0.5); color: @pn_disabled_fg; border-color: @pn_line_disabled; box-shadow: none; }
button:disabled:checked { background: mix(@pn_sunken, @pn_window, 0.5); }

button.suggested-action, button.suggested-action:backdrop, button.suggested-action:hover,
button.suggested-action:hover:not(:checked):not(:active) {
  background: @pn_accent; color: @pn_on_accent; border-color: @pn_accent_edge;
  box-shadow: inset 0 1px alpha(#ffffff, 0.18), 0 1px @pn_shade; }
button.suggested-action:active { background: mix(@pn_accent, #000000, 0.12); box-shadow: inset 0 1px @pn_shade; }
button.destructive-action, button.destructive-action:backdrop, button.destructive-action:hover,
button.destructive-action:hover:not(:checked):not(:active) {
  background: @pn_destructive; color: #ffffff; border-color: mix(@pn_destructive, #000000, 0.25);
  box-shadow: inset 0 1px alpha(#ffffff, 0.18), 0 1px @pn_shade; }

/* flat (toolbar) buttons: no chrome until hovered */
button.flat, button.flat:backdrop, toolbar button, toolbar button:backdrop {
  background: transparent; border-color: transparent; box-shadow: none; }
button.flat:hover, button.flat:hover:not(:checked):not(:active), toolbar button:hover {
  background: @pn_button; border-color: @pn_line; box-shadow: inset 0 1px @pn_hi; }
button.flat:active, button.flat:checked, toolbar button:active, toolbar button:checked {
  background: @pn_pressed; border-color: @pn_pressed_edge;
  box-shadow: inset 0 1px @pn_press_shade, inset 0 2px @pn_press_shade2;
  padding-top: 5px; padding-bottom: 3px; }
button.flat:disabled { background: transparent; border-color: transparent; }

/* titlebar buttons are drawn by the window decoration theme */
button.titlebutton, button.titlebutton:hover, button.titlebutton:active, button.titlebutton:backdrop {
  border-color: transparent; background: none; box-shadow: none; }

/* linked groups share edges */
.linked:not(.vertical) > button, .linked:not(.vertical) > entry, .linked:not(.vertical) > spinbutton,
.linked:not(.vertical) > combobox > box > button.combo, .linked:not(.vertical) > menubutton > button {
  border-radius: 0; }
.linked:not(.vertical) > :first-child, .linked:not(.vertical) > :first-child > button,
.linked:not(.vertical) > combobox:first-child > box > button.combo {
  border-top-left-radius: 3px; border-bottom-left-radius: 3px; }
.linked:not(.vertical) > :last-child, .linked:not(.vertical) > :last-child > button,
.linked:not(.vertical) > combobox:last-child > box > button.combo {
  border-top-right-radius: 3px; border-bottom-right-radius: 3px; }
.linked:not(.vertical) > button:not(:first-child) { border-left-width: 0; }

/* ---------- text fields: inset ---------- */
entry, spinbutton:not(.vertical), spinbutton.vertical > entry, spinbutton.vertical > text {
  background: @pn_content;
  color: @pn_content_fg;
  border: 1px solid @pn_line;
  border-top-color: @pn_inset_top;
  border-radius: 3px;
  box-shadow: inset 0 1px @pn_shade;
  min-height: 20px; }
entry { padding: 4px 6px; }
entry:backdrop, spinbutton:not(.vertical):backdrop { background: @pn_content; border-color: @pn_line; border-top-color: @pn_inset_top; }
entry:focus, entry:focus-within, spinbutton:not(.vertical):focus, spinbutton:not(.vertical):focus-within {
  border-color: @pn_focus; box-shadow: inset 0 1px @pn_shade, 0 0 0 1px @pn_focus; }
entry:disabled, spinbutton:disabled {
  background: @pn_window; color: @pn_disabled_fg; border-color: @pn_line_disabled; box-shadow: none; }

/* spin box: a raised button column inside the field */
spinbutton:not(.vertical) { padding: 0; }
spinbutton:not(.vertical) > entry, spinbutton:not(.vertical) > entry:focus, spinbutton:not(.vertical) > text {
  border: none; box-shadow: none; background: transparent; min-height: 20px; padding: 4px 6px; }
spinbutton:not(.vertical) > button, spinbutton:not(.vertical) > button:hover:not(:checked):not(:active),
spinbutton:not(.vertical) > button:backdrop {
  border: none; border-left: 1px solid @pn_line; border-radius: 0; margin: 0;
  background: @pn_button; box-shadow: inset 0 1px @pn_hi; padding: 0 6px; min-height: 0; color: @pn_button_fg; }
spinbutton:not(.vertical) > button:last-child { border-top-right-radius: 2px; border-bottom-right-radius: 2px; }
spinbutton:not(.vertical) > button:active { background: @pn_sunken; box-shadow: inset 0 1px @pn_shade; }
spinbutton:not(.vertical) > button:disabled { background: mix(@pn_button, @pn_window, 0.5); color: @pn_disabled_fg; }

/* ---------- check boxes and radio buttons: inset wells, accent when on ---------- */
check, radio {
  min-width: 14px; min-height: 14px;
  border: 1px solid @pn_line;
  border-top-color: @pn_inset_top;
  background-color: @pn_content;
  background-image: none;
  box-shadow: inset 0 1px @pn_shade; }
check { border-radius: 2px; }
radio { border-radius: 100%; }
check:hover, radio:hover { border-color: @pn_line; border-top-color: @pn_inset_top; background-color: @pn_content; }
check:active, radio:active { background-color: @pn_sunken; }
check:checked, check:indeterminate, radio:checked, radio:indeterminate,
check:checked:backdrop, check:indeterminate:backdrop, radio:checked:backdrop, radio:indeterminate:backdrop {
  background-color: @pn_accent; border-color: @pn_accent_edge; color: @pn_on_accent;
  -gtk-icon-palette: fg @pn_on_accent; box-shadow: inset 0 1px alpha(#ffffff, 0.15); }
check:disabled, radio:disabled { background-color: @pn_window; border-color: @pn_line_disabled; box-shadow: none; }
check:checked:disabled, check:indeterminate:disabled, radio:checked:disabled, radio:indeterminate:disabled {
  background-color: mix(@pn_accent, @pn_window, 0.6); border-color: mix(@pn_accent_edge, @pn_window, 0.6); color: @pn_on_accent; }
menu menuitem check, menu menuitem radio, popover modelbutton check, popover modelbutton radio {
  box-shadow: none; }

/* ---------- switch: pill track, raised knob ---------- */
switch {
  border: 1px solid @pn_line; border-top-color: @pn_inset_top; border-radius: 9px;
  background: @pn_sunken; box-shadow: inset 0 1px @pn_shade; color: transparent;
  min-width: 30px; min-height: 16px; padding: 0; font-size: 0; }
switch:checked, switch:checked:backdrop { background: @pn_accent; border-color: @pn_accent_edge; box-shadow: none; }
switch:disabled { background: @pn_window; border-color: @pn_line_disabled; }
switch slider, switch:checked slider, switch slider:backdrop, switch:hover slider {
  min-width: 16px; min-height: 16px; margin: -1px; border-radius: 100%;
  border: 1px solid @pn_line; background: @pn_button; background-image: none;
  box-shadow: inset 0 1px @pn_hi, 0 1px @pn_shade; }
switch:checked slider { border-color: @pn_accent_edge; }
switch:disabled slider { background: mix(@pn_button, @pn_window, 0.5); border-color: @pn_line_disabled; box-shadow: none; }

/* ---------- sliders: inset groove, accent fill, 12x20 raised handle with a grip ---------- */
scale trough, scale trough:backdrop, scale trough:disabled {
  background: @pn_sunken; border: 1px solid @pn_line; border-top-color: @pn_inset_top;
  border-radius: 3px; box-shadow: inset 0 1px @pn_shade; outline: none; }
scale.horizontal trough { min-height: 4px; }
scale.vertical trough { min-width: 4px; }
scale highlight, scale highlight:backdrop { background: @pn_accent; border: none; border-radius: 2px; margin: 0; }
scale highlight:disabled { background: mix(@pn_accent, @pn_window, 0.5); }
scale slider, scale slider:hover, scale slider:active, scale slider:backdrop {
  border: 1px solid @pn_line; border-radius: 2px; background-color: @pn_button;
  box-shadow: inset 0 1px @pn_hi, 0 1px @pn_shade; outline: none;
  background-repeat: no-repeat; background-position: center; }
scale slider:hover { background-color: @pn_button_hover; }
scale.horizontal slider, scale.horizontal slider:hover, scale.horizontal slider:active {
  min-width: 10px; min-height: 18px; margin: -8px 0;
  background-image: linear-gradient(to right, @pn_grip, @pn_grip); background-size: 1px 8px; }
scale.vertical slider, scale.vertical slider:hover, scale.vertical slider:active {
  min-width: 18px; min-height: 10px; margin: 0 -8px;
  background-image: linear-gradient(to right, @pn_grip, @pn_grip); background-size: 8px 1px; }
scale slider:disabled { background-color: mix(@pn_button, @pn_window, 0.5); border-color: @pn_line_disabled; box-shadow: none; }
scale marks, scale mark indicator { color: @pn_line; }

/* ---------- progress bars: 8px inset well, accent fill ---------- */
progressbar trough, progressbar trough:backdrop {
  min-height: 6px; min-width: 6px; background: @pn_sunken; border: 1px solid @pn_line;
  border-top-color: @pn_inset_top; border-radius: 2px; box-shadow: inset 0 1px @pn_shade; }
progressbar progress, progressbar progress:backdrop {
  min-height: 6px; min-width: 6px; margin: 0; border: none; border-radius: 1px;
  background: @pn_accent; background-image: none; box-shadow: none; }

/* ---------- scrollbars: 20px, sunken track, gripped raised thumb ---------- */
scrollbar, scrollbar:backdrop { background-color: @pn_sunken; border-color: @pn_line_soft; padding: 0; }
scrollbar trough, scrollbar.horizontal trough { margin: 0; min-width: 0; min-height: 0; background: none; }
scrollbar slider, :not(webkitwebview) scrollbar slider, :not(webkitwebview) scrollbar.horizontal slider,
scrollbar:hover trough slider, scrollbar:hover trough slider:hover,
*:focus ~ scrollbar:hover slider, scrollbar ~ *:focus:hover slider {
  margin: 3px; border: 1px solid @pn_line; border-radius: 2px; background-clip: border-box;
  background-color: @pn_button; box-shadow: inset 0 1px @pn_hi;
  background-repeat: no-repeat; background-position: center; }
scrollbar:hover trough slider:hover, scrollbar slider:active { background-color: @pn_button_hover; }
scrollbar.vertical slider, scrollbar.vertical:hover trough slider, scrollbar.vertical:hover trough slider:hover {
  min-width: 12px; min-height: 22px;
  background-image: repeating-linear-gradient(to bottom, @pn_grip 0px, @pn_grip 1px, transparent 1px, transparent 2px);
  background-size: 8px 5px; }
scrollbar.horizontal slider, scrollbar.horizontal:hover trough slider, scrollbar.horizontal:hover trough slider:hover {
  min-width: 22px; min-height: 12px;
  background-image: repeating-linear-gradient(to right, @pn_grip 0px, @pn_grip 1px, transparent 1px, transparent 2px);
  background-size: 5px 8px; }
scrollbar slider:disabled { background-color: transparent; border-color: transparent; background-image: none; box-shadow: none; }
/* overlay scrollbars (when the toolkit setting asks for them) stay slim until hovered */
scrollbar.overlay-indicator:not(.dragging):not(.hovering) slider {
  margin: 3px; min-width: 4px; min-height: 4px; border: none; border-radius: 3px;
  background-color: alpha(@pn_text, 0.4); background-image: none; box-shadow: none; }
scrollbar.overlay-indicator.dragging, scrollbar.overlay-indicator.hovering { background-color: @pn_sunken; }

/* ---------- tabs: generated by tab_rules() ---------- */
@TABS@
notebook > stack:not(:only-child), notebook > stack:not(:only-child):backdrop {
  background-color: @pn_button; border: 1px solid @pn_tab_line; border-radius: 0 0 3px 3px; }
notebook > header.top + stack { border-top: none; }
notebook > header.left + stack { border-left: none; border-radius: 0 3px 3px 0; }
notebook > header.bottom, notebook > header.right { box-shadow: none; }
notebook > header.bottom > tabs > tab { margin-top: -1px; }
notebook > header.right > tabs > tab { margin-left: -1px; }
notebook > header.bottom > tabs > tab:checked { border-top: 1px solid @pn_button; }
notebook > header.right > tabs > tab:checked { border-left: 1px solid @pn_button; }
notebook.frame { border: none; }
frame > border, .frame { border-color: @pn_line; }

/* ---------- list headers ---------- */
treeview.view header button, treeview.view header button:hover, treeview.view header button:backdrop,
columnview > header > button, columnview > header > button:hover, columnview > header > button:backdrop {
  background: @pn_button; color: @pn_button_fg; border: none; border-radius: 0;
  border-right: 1px solid @pn_separator; border-bottom: 1px solid @pn_line;
  box-shadow: inset 0 1px @pn_hi; padding: 3px 6px; min-height: 18px; }
treeview.view header button:active, columnview > header > button:active {
  background: @pn_sunken; box-shadow: inset 0 1px @pn_shade; }

/* ---------- headerbars (client-side titlebars): chrome, lit edge, flat when inactive ---------- */
headerbar, .titlebar:not(headerbar) {
  background: @pn_window; background-image: none; color: @pn_text;
  border: none; border-bottom: 1px solid @pn_line; box-shadow: inset 0 1px @pn_hi;
  min-height: 34px; padding: 0 6px; }
headerbar:backdrop, .titlebar:backdrop:not(headerbar) { background: @pn_window; box-shadow: none; color: @pn_tab_fg; }
headerbar .title { font-weight: 600; }

/* ---------- toolbars and menubars ---------- */
toolbar, .toolbar, menubar { background: @pn_window; }
menubar > menuitem:hover, menubar > item:hover { background: @pn_accent; color: @pn_on_accent; box-shadow: none; }

/* ---------- menus and popovers: raised sheets ---------- */
menu, .menu, .context-menu {
  background: @pn_button; color: @pn_button_fg; border: 1px solid @pn_line; border-radius: 3px; padding: 4px 0; }
menu menuitem { padding: 4px 10px; min-height: 18px; }
menu menuitem:hover { background: @pn_accent; color: @pn_on_accent; }
menu menuitem:hover > *, menu menuitem:hover accelerator, menu menuitem:hover arrow { color: @pn_on_accent; }
menu separator { background: @pn_separator; margin: 4px 0; min-height: 1px; }
.csd.popup decoration, .popup decoration {
  border-radius: 3px; box-shadow: 0 2px 8px @pn_popup_shadow, 0 0 0 1px alpha(@pn_line, 0.5); }
"""

GTK3_RULES = """
popover.background {
  background: @pn_button; color: @pn_button_fg; border: 1px solid @pn_line; border-radius: 3px;
  box-shadow: 0 2px 8px @pn_popup_shadow; }
popover.background modelbutton.flat:hover { background: @pn_accent; color: @pn_on_accent; }
tooltip, tooltip.background, .csd tooltip.background {
  background-color: @tooltip_background_breeze; color: @tooltip_text_breeze; border: none; border-radius: 2px; box-shadow: none; }
tooltip decoration { background: none; }
tooltip * { background: transparent; color: @tooltip_text_breeze; }
"""

GTK4_RULES = """
switch image { color: transparent; opacity: 0; }
button:focus-visible, check:focus-visible, radio:focus-visible, switch:focus-visible,
scale:focus-visible slider, notebook > header > tabs > tab:focus-visible {
  outline: 2px solid alpha(@pn_focus, 0.9); outline-offset: 1px; }
popover > contents, popover.background > contents {
  background: @pn_button; color: @pn_button_fg; border: 1px solid @pn_line; border-radius: 3px;
  box-shadow: 0 2px 8px @pn_popup_shadow; }
popover > arrow { background: @pn_button; border: 1px solid @pn_line; }
popover.menu modelbutton:hover, popover.menu modelbutton:selected { background: @pn_accent; color: @pn_on_accent; }
dropdown > button, combobox > button { padding: 4px 8px; }
tooltip, tooltip.background {
  background-color: @tooltip_background_breeze; color: @tooltip_text_breeze; border: none; border-radius: 2px; box-shadow: none; }
tooltip * { color: @tooltip_text_breeze; }
"""


# Breeze styles tabs through selectors like "tab:checked:not(:first-child)" and "tab:checked + tab";
# every tab rule here is expanded over the same shapes so it is at least as specific, and wins by order.
TAB_SHAPES = ["", ":first-child", ":last-child", ":not(:first-child)", ":not(:last-child)"]


def tab_sel(pos, state=""):
    out = []
    for p in ([pos] if pos else ["top", "bottom", "left", "right"]):
        base = f"notebook > header.{p} > tabs > tab"
        out += [f"{base}{state}{s}" for s in TAB_SHAPES]
        out += [f"{base}:checked + tab{state}", f"{base}:checked + tab{state}:hover"]
    return ",\n".join(dict.fromkeys(out))


def tab_rules():
    edge = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}
    radius = {"top": "3px 3px 0 0", "bottom": "0 0 3px 3px", "left": "3px 0 0 3px", "right": "0 3px 3px 0"}
    r = [f"""notebook > header, notebook > header:backdrop {{ background-color: @pn_window; border: none; padding: 0 6px; }}
notebook > header.left, notebook > header.right {{ padding: 6px 0; }}
notebook > header.top {{ box-shadow: inset 0 -1px @pn_tab_line; }}
notebook > header.left {{ box-shadow: inset -1px 0 @pn_tab_line; }}
notebook > header.bottom, notebook > header.right {{ box-shadow: none; }}
notebook > header > tabs > tab > label {{ margin: 0; }}
{tab_sel(None)} {{
  margin: 0; min-height: 20px; border: 1px solid @pn_tab_line; outline: none;
  background-color: @pn_sunken; color: @pn_tab_fg; box-shadow: none; transition: none; }}
{tab_sel(None, ":hover")} {{ background-color: mix(@pn_sunken, @pn_button, 0.6); }}"""]
    for pos in ("top", "bottom", "left", "right"):
        horiz = pos in ("top", "bottom")
        e = edge[pos]
        pad = "3px 12px" if horiz else "6px 10px"
        # unselected tabs are shorter: inset 2px from the far side; neighbours overlap by 1px
        step = "margin-left: -1px;" if horiz else "margin-top: -1px;"
        # bottom/right headers come after the pane, so their tabs overlap its border
        overlap = {"bottom": "margin-top: -1px;", "right": "margin-left: -1px;"}.get(pos, "")
        grow = {"top": "padding-top: 5px;", "bottom": "padding-bottom: 5px;",
                "left": "padding-left: 12px;", "right": "padding-right: 12px;"}[pos]
        cover = f"border-{e}: 1px solid @pn_button;" if pos in ("bottom", "right") else f"border-{e}: none;"
        r.append(f"""{tab_sel(pos)} {{
  padding: {pad}; margin-{pos}: 2px; {overlap} border-{e}: none; border-radius: {radius[pos]}; }}
{tab_sel(pos, ":not(:first-child)")} {{ {step} }}
{tab_sel(pos, ":checked")} {{
  background-color: @pn_button; color: @pn_button_fg; margin-{pos}: 0; {grow} {cover}
  box-shadow: {"inset 0 1px @pn_hi" if pos != "bottom" else "none"}; }}""")
    return "\n".join(r)


def css(gtk, mode):
    parts = [
        f"/* Platinum Neue for GTK {gtk} ({mode}). Generated by tools/gen_gtk.py - edit that, not this file. */",
        f'@import url("file://{BREEZE}/gtk-{gtk}.0/{"gtk-dark" if mode == "dark" else "gtk"}.css");',
        "",
        "/* fallback colours; Plasma overrides these from the active colour scheme */",
    ]
    parts += [f"@define-color {n} {v};" for n, v in fallback_colours(mode).items()]
    parts.append(ROLES)
    parts += [f"@define-color {n} {v};" for n, v in VARIANT[mode].items()]
    rules = RULES
    if gtk == 3:  # GTK 3 drops a whole rule over one unknown pseudo-class
        rules = rules.replace("entry:focus, entry:focus-within, spinbutton:not(.vertical):focus, spinbutton:not(.vertical):focus-within",
                              "entry:focus, spinbutton:not(.vertical):focus")
    parts.append(rules.replace("@TABS@", tab_rules()))
    parts.append(GTK3_RULES if gtk == 3 else GTK4_RULES)
    return "\n".join(parts)


INDEX = """[Desktop Entry]
Type=X-GNOME-Metatheme
Name={name}
Comment=Platinum Neue for GTK applications
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme={dirname}
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    base = OUT / "Platinum-Neue"
    dark = OUT / "Platinum-Neue-Dark"
    for gtk in (3, 4):
        d = base / f"gtk-{gtk}.0"
        d.mkdir(parents=True)
        (d / "gtk.css").write_text(css(gtk, "light"))
        (d / "gtk-dark.css").write_text(css(gtk, "dark"))
        dd = dark / f"gtk-{gtk}.0"
        dd.mkdir(parents=True)
        (dd / "gtk.css").write_text(css(gtk, "dark"))
    (base / "index.theme").write_text(INDEX.format(name="Platinum Neue", dirname="Platinum-Neue"))
    (dark / "index.theme").write_text(INDEX.format(name="Platinum Neue Dark", dirname="Platinum-Neue-Dark"))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

#!/bin/bash
# Screenshot the GTK gallery with the Platinum Neue GTK theme straight from gtk/ (no install needed),
# in a headless nested KWin isolated from the real session.
# Usage: tools/gtk-test.sh [light|dark] [3|4] [outdir] [extra gallery args, e.g. --csd]
set -euo pipefail
mode="${1:-light}"; ver="${2:-3}"; out="$(realpath -m "${3:-/tmp/platinum-neue-gtk}")"; shift 3 || true
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$out/data/themes" "$out/cfg/gtk-3.0" "$out/cfg/gtk-4.0"
ln -sfn "$root/gtk/Platinum-Neue" "$out/data/themes/Platinum-Neue"
ln -sfn "$root/gtk/Platinum-Neue-Dark" "$out/data/themes/Platinum-Neue-Dark"
for v in 3 4; do
  printf '[Settings]\ngtk-font-name=Bricolage Grotesque 10\ngtk-overlay-scrolling=false\ngtk-application-prefer-dark-theme=%s\n' \
    "$([ "$mode" = dark ] && echo true || echo false)" > "$out/cfg/gtk-$v.0/settings.ini"
done
theme="Platinum-Neue"; [ "$mode" = dark ] && theme="Platinum-Neue:dark"
rm -f "$out/shot.png"
dbus-run-session bash -c '
  out="$0"; root="$1"; ver="$2"; theme="$3"; shift 4
  export XDG_CONFIG_HOME="$out/cfg"
  kwin_wayland --virtual --no-lockscreen --no-global-shortcuts --width 900 --height 560 --socket wayland-pn >"$out/kwin.log" 2>&1 &
  sleep 3
  # --scale only enlarges the virtual mode; set the real output scale so clients render scaled
  [ "${PN_SCALE:-1}" = 1 ] || { WAYLAND_DISPLAY=wayland-pn kscreen-doctor output.Virtual-0.scale.${PN_SCALE:-1} >/dev/null 2>&1; sleep 1; }
  WAYLAND_DISPLAY=wayland-pn GDK_BACKEND=wayland XDG_DATA_HOME="$out/data" GTK_THEME="$theme" GTK_OVERLAY_SCROLLING=0 \
    python3 "$root/tools/gtk-gallery.py" "$ver" "$@" >"$out/gallery.log" 2>&1 &
  sleep 4
  WAYLAND_DISPLAY=wayland-pn spectacle -b -n -f -o "$out/shot.png" >/dev/null 2>&1
  kill %1 %2 2>/dev/null || true
  wait
' "$out" "$root" "$ver" "$theme" -- "$@" >/dev/null 2>&1
echo "$out/shot.png"

#!/bin/bash
# Screenshot Platinum Neue in a headless nested KWin, isolated from the real session.
# Usage: tools/nested-test.sh [light|dark] [outdir]
# Uses the installed package (/usr). Writes <outdir>/shot.png. Needs: kwin, dolphin, konsole, spectacle.
set -euo pipefail
mode="${1:-light}"; out="$(realpath -m "${2:-/tmp/platinum-neue-test}")"
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$out/cfg"
scheme="PlatinumNeue${mode^}"
{ cat "$root/color-schemes/$scheme.colors"; cat <<EOC

[General]
font=Bricolage Grotesque,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1
ColorScheme=$scheme

[WM]
activeFont=Bricolage Grotesque,10,-1,5,600,0,0,0,0,0,0,0,0,0,0,1
EOC
} > "$out/cfg/kdeglobals"
printf '[org.kde.kdecoration2]\nlibrary=org.kde.platinumneue\ntheme=\nButtonsOnLeft=M\nButtonsOnRight=IAX\n' > "$out/cfg/kwinrc"
rm -f "$out/shot.png"
dbus-run-session bash -c '
  export XDG_CONFIG_HOME="$0/cfg"
  kwin_wayland --virtual --no-lockscreen --no-global-shortcuts --width 1100 --height 700 --socket wayland-pn >"$0/kwin.log" 2>&1 &
  sleep 3
  export WAYLAND_DISPLAY=wayland-pn QT_QPA_PLATFORM=wayland
  konsole >/dev/null 2>&1 &
  sleep 2
  dolphin --new-window "$HOME" >/dev/null 2>&1 &
  sleep 4
  spectacle -b -n -f -o "$0/shot.png" >/dev/null 2>&1
  kill %1 2>/dev/null || true
' "$out" >/dev/null 2>&1
echo "$out/shot.png"

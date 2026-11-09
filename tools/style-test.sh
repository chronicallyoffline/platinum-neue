#!/bin/bash
# Screenshot the widget gallery using the Platinum Neue style straight from build/ (no install needed),
# inside a headless nested KWin isolated from the real session.
# Usage: tools/style-test.sh [light|dark] [outdir] [scale]
set -euo pipefail
mode="${1:-light}"; out="$(realpath -m "${2:-/tmp/platinum-neue-style}")"; scale="${3:-1}"
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$out/cfg" "$out/plugins/styles"
ln -sf "$root/build/bin/platinumneue6.so" "$out/plugins/styles/platinumneue6.so"
# KWin loads the decoration from here first, so the test uses the build, not the installed copy
mkdir -p "$out/kwinplugins/org.kde.kdecoration3"
ln -sf "$root/build/bin/org.kde.platinumneue.so" "$out/kwinplugins/org.kde.kdecoration3/org.kde.platinumneue.so"
scheme="PlatinumNeue${mode^}"
{ cat "$root/color-schemes/$scheme.colors"; cat <<EOC

[General]
font=Bricolage Grotesque,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1
ColorScheme=$scheme

[KDE]
widgetStyle=PlatinumNeue

[WM]
activeFont=Bricolage Grotesque,10,-1,5,600,0,0,0,0,0,0,0,0,0,0,1
EOC
} > "$out/cfg/kdeglobals"
printf '[org.kde.kdecoration2]\nlibrary=org.kde.platinumneue\ntheme=\nButtonsOnLeft=M\nButtonsOnRight=IAX\n' > "$out/cfg/kwinrc"
rm -f "$out/shot.png"
dbus-run-session bash -c '
  out="$0"; root="$1"; scale="$2"
  export XDG_CONFIG_HOME="$out/cfg"
  QT_PLUGIN_PATH="$out/kwinplugins:/usr/lib/qt6/plugins" kwin_wayland --virtual --no-lockscreen --no-global-shortcuts --width 900 --height 720 --scale "$scale" --socket wayland-pn >"$out/kwin.log" 2>&1 &
  sleep 3
  # --scale only enlarges the virtual mode; set the real output scale so clients render scaled
  [ "$scale" = 1 ] || { WAYLAND_DISPLAY=wayland-pn kscreen-doctor output.Virtual-0.scale.$scale >/dev/null 2>&1; sleep 1; }
  export WAYLAND_DISPLAY=wayland-pn QT_QPA_PLATFORM=wayland QT_PLUGIN_PATH="$out/plugins" QT_STYLE_OVERRIDE=PlatinumNeue
  ${PN_APP:-"$root/build/gallery/pn-gallery"} >"$out/gallery.log" 2>&1 &
  sleep 4
  QT_PLUGIN_PATH= QT_STYLE_OVERRIDE= spectacle -b -n -f -o "$out/shot.png" >/dev/null 2>&1
  kill %1 %2 2>/dev/null || true
' "$out" "$root" "$scale" >/dev/null 2>&1
echo "$out/shot.png"

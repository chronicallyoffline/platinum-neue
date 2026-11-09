#!/bin/bash
# Screenshot a fresh plasmashell using the Platinum Neue desktop theme straight from plasma/ (no install),
# inside a headless nested KWin with throwaway config/data dirs.
# Usage: tools/plasma-test.sh [light|dark] [outdir] [width] [height]
set -euo pipefail
mode="${1:-light}"; out="$(realpath -m "${2:-/tmp/platinum-neue-plasma}")"; W="${3:-1100}"; H="${4:-700}"; S="${PN_SCALE:-1}"
root="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf "$out/cfg" "$out/data" "$out/cache"
mkdir -p "$out/cfg" "$out/data/plasma/desktoptheme" "$out/data/color-schemes"
ln -sf "$root/plasma/desktoptheme/platinum-neue-$mode" "$out/data/plasma/desktoptheme/"
mkdir -p "$out/data/plasma/look-and-feel"
ln -sf "$root/plasma/look-and-feel/org.platinumneue.$mode.desktop" "$out/data/plasma/look-and-feel/"
cp "$root"/color-schemes/*.colors "$out/data/color-schemes/"
# EB Garamond for the clock, if a copy is at hand (pkg/src after makepkg, or PN_SERIF=<ttf>)
serif="${PN_SERIF:-$root/pkg/src/EBGaramond.ttf}"
[ -f "$serif" ] && mkdir -p "$out/data/fonts" && cp "$serif" "$out/data/fonts/"
scheme="PlatinumNeue${mode^}"
{ cat "$root/color-schemes/$scheme.colors"; cat <<EOC

[General]
font=Bricolage Grotesque,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1
ColorScheme=$scheme

[KDE]
widgetStyle=Breeze
EOC
} > "$out/cfg/kdeglobals"
printf '[Theme]\nname=platinum-neue-%s\n' "$mode" > "$out/cfg/plasmarc"
printf '[Plugins]\nblurEnabled=false\n' > "$out/cfg/kwinrc"
# use the built decoration and style (not the installed copies) for any windows opened via PN_EXTRA
mkdir -p "$out/kwinplugins/org.kde.kdecoration3" "$out/plugins/styles"
ln -sf "$root/build/bin/org.kde.platinumneue.so" "$out/kwinplugins/org.kde.kdecoration3/org.kde.platinumneue.so"
ln -sf "$root/build/bin/platinumneue6.so" "$out/plugins/styles/platinumneue6.so"
printf '[org.kde.kdecoration2]\nlibrary=org.kde.platinumneue\ntheme=\n' >> "$out/cfg/kwinrc"
rm -f "$out/shot.png"
dbus-run-session bash -c '
  out="$0"; W="$1"; H="$2"; S="$3"
  export XDG_CONFIG_HOME="$out/cfg" XDG_DATA_HOME="$out/data" XDG_CACHE_HOME="$out/cache"
  QT_PLUGIN_PATH="$out/kwinplugins:/usr/lib/qt6/plugins" kwin_wayland --virtual --no-lockscreen --no-global-shortcuts --width "$W" --height "$H" --scale "$S" --socket wayland-pp >"$out/kwin.log" 2>&1 &
  sleep 3
  # --scale only enlarges the virtual mode; set the real output scale so clients render scaled
  [ "${PN_SCALE:-1}" = 1 ] || { WAYLAND_DISPLAY=wayland-pp kscreen-doctor output.Virtual-0.scale.${PN_SCALE:-1} >/dev/null 2>&1; sleep 1; }
  export WAYLAND_DISPLAY=wayland-pp QT_QPA_PLATFORM=wayland
  plasmashell --no-respawn >"$out/plasma.log" 2>&1 &
  sleep 9
  eval "${PN_EXTRA:-true}"
  spectacle -b -n -f -o "$out/shot.png" >/dev/null 2>&1
  kill %2 %1 2>/dev/null || true; wait 2>/dev/null || true
 ' "$out" "$W" "$H" "$S" >/dev/null 2>&1
echo "$out/shot.png"

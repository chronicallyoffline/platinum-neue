#!/usr/bin/env bash
# Install Platinum Neue for the current user (~/.local/share). Does not apply anything.
set -euo pipefail
cd "$(dirname "$0")"

python3 tools/gen.py

data="${XDG_DATA_HOME:-$HOME/.local/share}"
install -d "$data/color-schemes"
install -m644 color-schemes/PlatinumNeue*.colors "$data/color-schemes/"
echo "Installed colour schemes to $data/color-schemes"

python3 tools/gen_gtk.py
install -d "$data/themes"
rm -rf "$data/themes/Platinum-Neue" "$data/themes/Platinum-Neue-Dark"
cp -r gtk/Platinum-Neue gtk/Platinum-Neue-Dark "$data/themes/"
echo "Installed GTK themes to $data/themes (needs breeze-gtk)"

cat <<EOF

To apply:
  plasma-apply-colorscheme PlatinumNeueLight   # or PlatinumNeueDark
  System Settings > Colors & Themes > Application Style > Configure GNOME/GTK Application Style: Platinum Neue
VS Code (optional):
  python3 tools/gen_vscode.py && code --install-extension vscode/platinum-neue-0.1.0.vsix
To go back:
  plasma-apply-colorscheme BreezeLight
EOF

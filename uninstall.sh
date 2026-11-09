#!/usr/bin/env bash
# Remove Platinum Neue files from ~/.local/share. Switch away from the scheme first.
set -euo pipefail
data="${XDG_DATA_HOME:-$HOME/.local/share}"
rm -fv "$data"/color-schemes/PlatinumNeue*.colors
rm -rfv "$data/themes/Platinum-Neue" "$data/themes/Platinum-Neue-Dark"

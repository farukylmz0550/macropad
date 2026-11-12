#!/usr/bin/env sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
qmk_home=${QMK_HOME:-}

if [ -z "$qmk_home" ] || [ ! -f "$qmk_home/quantum/quantum.h" ]; then
    echo "Set QMK_HOME to a QMK 0.34.0 checkout." >&2
    exit 2
fi

qmk_version=$(git -C "$qmk_home" describe --tags --exact-match 2>/dev/null || true)
if [ "$qmk_version" != "0.34.0" ]; then
    echo "QMK_HOME must be exactly tag 0.34.0 (found: ${qmk_version:-unknown})." >&2
    exit 2
fi

keyboard_target="$qmk_home/keyboards/macropad_v3"
if [ -e "$keyboard_target" ] || [ -L "$keyboard_target" ]; then
    echo "Refusing to replace existing $keyboard_target" >&2
    exit 2
fi

cleanup() {
    rm -f "$keyboard_target"
}
trap cleanup EXIT HUP INT TERM
ln -s "$repo_dir/firmware/macropad_v3" "$keyboard_target"

mkdir -p "$repo_dir/build"
for keymap in via_latching via_toggle; do
    (cd "$qmk_home" && qmk lint -kb macropad_v3 -km "$keymap")
    (cd "$qmk_home" && qmk compile -kb macropad_v3 -km "$keymap")
    cp "$qmk_home/.build/macropad_v3_${keymap}.hex" "$repo_dir/build/${keymap}.hex"
done

"$repo_dir/scripts/report-size.sh" \
    "$qmk_home/.build/macropad_v3_via_latching.elf" \
    "$qmk_home/.build/macropad_v3_via_toggle.elf"

sha256sum "$repo_dir/build/via_latching.hex" "$repo_dir/build/via_toggle.hex"

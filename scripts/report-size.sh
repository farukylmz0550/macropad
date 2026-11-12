#!/usr/bin/env sh
set -eu

FLASH_LIMIT=28672
FLASH_WARNING=27648

if [ "$#" -eq 0 ]; then
    echo "usage: $0 firmware.elf [...]" >&2
    exit 2
fi

for elf in "$@"; do
    if [ ! -f "$elf" ]; then
        echo "missing ELF: $elf" >&2
        exit 2
    fi

    set -- $(avr-size "$elf" | awk 'NR == 2 {print $1, $2, $3}')
    text_bytes=$1
    data_bytes=$2
    bss_bytes=$3
    flash_bytes=$((text_bytes + data_bytes))
    sram_bytes=$((data_bytes + bss_bytes))
    name=$(basename "$elf")

    printf '%s: flash=%s/%s bytes, static SRAM=%s/2560 bytes (data=%s, bss=%s)\n' \
        "$name" "$flash_bytes" "$FLASH_LIMIT" "$sram_bytes" "$data_bytes" "$bss_bytes"

    if [ "$flash_bytes" -gt "$FLASH_LIMIT" ]; then
        echo "error: $name exceeds the Caterina application limit" >&2
        exit 1
    fi
    if [ "$flash_bytes" -gt "$FLASH_WARNING" ]; then
        echo "warning: $name exceeds the preferred 27 KiB target" >&2
    fi
done

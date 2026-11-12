# Reference build report

Built on 2026-11-12 from QMK tag `0.34.0` with QMK CLI 1.2.0 and the QMK AVR
toolchain (`avr-gcc` 15.2.0). Flash is `.text + .data`; static SRAM is
`.data + .bss`.

| Variant | Flash | Caterina limit | Static SRAM | HEX SHA-256 |
|---|---:|---:|---:|---|
| `via_latching` | 14,854 B | 28,672 B | 349 / 2,560 B | `de4cfb2b5021046ab333f81c5b3be87b95cd872af83af2d4d4c4f3c5dee9fe4c` |
| `via_toggle` | 14,864 B | 28,672 B | 349 / 2,560 B | `53f953514920e2173a165e47af7ab64a1d9e5b694aa69afcdabb0571e0c2b057` |

Both variants passed `qmk lint` and `qmk compile`. The generated HEX files are
CI artifacts and local `build/` outputs; they are intentionally ignored by Git.

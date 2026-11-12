# MacroPad V3

MacroPad V3 is an open-source, through-hole Arduino Leonardo shield with five
VIA-programmable macro buttons, a dedicated layer switch, a clickable rotary
encoder, and a 128×64 SSD1306 OLED.

> [!WARNING]
> **Untested hardware:** the PCB has not yet been manufactured or tested on a
> physical Arduino Leonardo. Review the schematic, polarity, connector pinout,
> and mechanical clearances before ordering. The firmware builds successfully,
> but USB, encoder direction, OLED operation, and switch polarity still require
> physical bring-up.

## Features

- ATmega32U4 / Caterina target (QMK 0.34.0)
- Two VIA layers stored in EEPROM
- Five configurable macro inputs: SW1–SW4 and SW6
- One VIA-configurable encoder and encoder click
- S5 is a fixed, hidden layer control (latching or toggle firmware)
- Bufferless SSD1306 driver showing only `LAYER 1` or `LAYER 2`
- No RGB, backlight, audio, mouse keys, NKRO, console, command, Unicode,
  tap-dance, combo, macro, or debug features

## Default controls

| Control | Layer 1 | Layer 2 |
|---|---|---|
| SW1 | F13 | Previous track |
| SW2 | F14 | Play / pause |
| SW3 | F15 | Next track |
| SW4 | F16 | Rewind |
| SW6 | F17 | Fast-forward |
| Encoder counter-clockwise / clockwise | Volume down / up | Volume down / up |
| Encoder click | Mute | Mute |

S5 does not appear in VIA. Flash `via_latching` when S5 is a maintained
switch (ON selects Layer 2; OFF selects Layer 1), or `via_toggle` when S5 is a
momentary button (each press changes layer).

## Pinout

The PCB net names follow Arduino Leonardo header labels. QMK uses the
ATmega32U4 port name shown in parentheses.

| Connector signal | Leonardo label | QMK pin | Other connector pin |
|---|---:|---:|---|
| SW1 | D7 | E6 | GND |
| SW2 | D8 | B4 | GND |
| SW3 | D9 | B5 | GND |
| SW4 | D12 | D6 | GND |
| S5 layer control | D11 | B7 | GND |
| SW6 | D10 | B6 | GND |
| Encoder CLK | D4 | D4 | — |
| Encoder DT | D5 | C6 | — |
| Encoder click | D6 | D7 | — |
| OLED SDA | D2 / SDA | D1 | — |
| OLED SCL | D3 / SCL | D0 | — |
| OLED / encoder power | 5V, GND | — | — |

See [the complete pinout](docs/pinout.md) before making cables. The PCB source
files are in `hardware/`; `schematic.json` and `pcb_easyeda.pcbdoc` are the
editable EasyEDA sources, and `schematic.pdf` is the review copy.

## Assembly

This is a through-hole design. Solder the low-profile shield headers and JST-XH
headers first, inspect for bridges, then mate the shield to an unpowered
Leonardo. Do not assume that similarly shaped OLED or KY-040 modules use the
same pin order. Follow [the assembly guide](docs/assembly.md).

## Firmware

The repository stores a QMK keyboard tree at `firmware/macropad_v3`. The build
helper requires an exact QMK 0.34.0 checkout:

```sh
QMK_HOME=/path/to/qmk_firmware ./scripts/build-firmware.sh
```

It runs `qmk lint` and `qmk compile` for both variants, copies the loadable
`.hex` files to `build/`, and rejects flash use over the Caterina limit of
28,672 bytes. Builds above 27 KiB emit a warning. Flash with QMK Toolbox or:

```sh
qmk flash -kb macropad_v3 -km via_latching
```

The `qmk flash` command requires `firmware/macropad_v3` to be copied or linked
as `keyboards/macropad_v3` in that QMK checkout. Alternatively, flash either
generated Intel HEX file with QMK Toolbox. Double-press RESET on the Leonardo
if Caterina does not enter the bootloader.
Load `via/macropad_v3.json` in VIA's Design tab if the keyboard definition is
not yet bundled. VIA changes to the six keys and encoder map persist in EEPROM.

S5 is read outside the 1×6 dynamic matrix. SW1–SW4, SW6, and encoder click are
the six VIA-visible keys. The SSD1306 driver writes its seven-character layer
label directly over I²C; `OLED_ENABLE` stays disabled so QMK's standard
1,024-byte framebuffer is not linked on the 2.5 KB SRAM ATmega32U4.

## Manufacturing

The ready-to-upload fabrication archive is
`production/gerber/macropad.zip`. See the [BOM](production/bom.csv) and
[`checksums.sha256`](production/checksums.sha256). The board is approximately
68.58 × 53.34 mm at its maximum extents. Paste and component-placement files
are intentionally absent because all fitted parts are through-hole.
EasyEDA Standard 6.5.61 reported zero DRC errors before the current Gerber was
exported; the result is recorded in
[`production/drc-report.md`](production/drc-report.md).

### Recommended order settings

| Item | Value |
|---|---|
| Maximum board extents | 68.58 × 53.34 mm |
| Layer count | 2 |
| Material / thickness | FR-4, 1.6 mm |
| Copper | 1 oz outer layers |
| Surface finish | Lead-free HASL or ENIG |
| Solder mask / silkscreen | Per Gerber archive |
| Electrical test | Recommended |
| Castellations / impedance control | Not required |

The outline is not a simple rectangle. Confirm its dimensions and every layer
in the fabricator's Gerber viewer before payment.

### Package contents

- `production/gerber/macropad.zip`: top/bottom copper, top/bottom solder mask,
  top silkscreen, outline, PTH drill, via drill, and NPTH drill exports.
- `production/bom.csv`: through-hole parts and matching JST-XH
  housings/contacts.
- `production/checksums.sha256`: integrity hashes for fabrication and source
  artifacts.
- `hardware/schematic.json` and `hardware/pcb_easyeda.pcbdoc`: editable EasyEDA
  sources.
- `hardware/schematic.pdf`: schematic review export.
- `docs/images/pcb_front.png` and `docs/images/pcb_back.png`: PCB previews.

There are no solder-paste or CPL/pick-and-place files. All fitted parts are
through-hole and intended for manual assembly.

### Release procedure

1. Run ERC and DRC in EasyEDA and save the results with the production record.
2. Re-export the schematic PDF, Gerbers/drills, BOM, and front/back images
   without changing the outline, routing, or footprint placement.
3. Inspect every archive layer in an independent Gerber viewer.
4. Run the repository tests shown below.
5. Regenerate `production/checksums.sha256` after final exports are frozen.

Run the package checks with:

```sh
python3 -m unittest discover -s tests -v
```

The existing electrical design, board outline, routing, and footprint
placements have not been changed by the firmware/documentation work.

## License

See [LICENSE](LICENSE).

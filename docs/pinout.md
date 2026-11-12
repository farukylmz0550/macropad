# MacroPad V3 pinout

This document uses connector pin numbers as drawn in `hardware/schematic.pdf`.
Verify the pin-1 mark on the physical connector and cable before applying power.

## Switch connectors

All six 2-pin JST-XH headers use the same convention:

| Connector | Pin 1 | Pin 2 | Firmware role |
|---|---|---|---|
| SW1 | GND | Leonardo D7 | VIA key 1 |
| SW2 | GND | Leonardo D8 | VIA key 2 |
| SW3 | GND | Leonardo D9 | VIA key 3 |
| SW4 | GND | Leonardo D12 | VIA key 4 |
| S5 | GND | Leonardo D11 | Hidden layer control |
| SW6 | GND | Leonardo D10 | VIA key 5 |

The firmware enables the ATmega32U4 internal pull-ups, so a closed switch pulls
the corresponding signal to GND. S5 is never exposed in the VIA matrix.

## OLED connector (SSD1306, 4-pin)

| Pin | Net | Leonardo function |
|---:|---|---|
| 1 | GND | Ground |
| 2 | VCC | 5 V |
| 3 | SCL | D3 / SCL / ATmega32U4 PD0 |
| 4 | SDA | D2 / SDA / ATmega32U4 PD1 |

The firmware expects a 128×64 SSD1306 at I²C address `0x3C`. Confirm that the
module accepts 5 V power and 5 V I/O before connecting it; otherwise use a
compatible module or level shifting.

## KY-040 connector (5-pin)

| Pin | Net | Leonardo function |
|---:|---|---|
| 1 | GND | Ground |
| 2 | VCC | 5 V |
| 3 | SW | D6 / encoder click |
| 4 | DT | D5 / encoder B |
| 5 | CLK | D4 / encoder A |

KY-040 board labels and cable order vary. Match signals rather than assuming a
color sequence. If rotation is reversed after physical testing, swap CLK and DT
in the cable or exchange `pin_a` and `pin_b` in `keyboard.json`.

## Arduino-to-QMK name translation

| Leonardo label | ATmega32U4 port / QMK pin |
|---:|---:|
| D2 | PD1 / D1 |
| D3 | PD0 / D0 |
| D4 | PD4 / D4 |
| D5 | PC6 / C6 |
| D6 | PD7 / D7 |
| D7 | PE6 / E6 |
| D8 | PB4 / B4 |
| D9 | PB5 / B5 |
| D10 | PB6 / B6 |
| D11 | PB7 / B7 |
| D12 | PD6 / D6 |

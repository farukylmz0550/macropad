# MacroPad V3 assembly and bring-up

## Before ordering

1. Open `hardware/schematic.json` and `hardware/pcb_easyeda.pcbdoc` in EasyEDA.
2. Run schematic/ERC and PCB/DRC checks using the design rules in the source.
3. Compare the generated Gerbers with `production/gerber/macropad.zip`, paying
   special attention to the outline, plated holes, masks, and header alignment.
4. Print the board preview at 1:1 and compare it with a physical Leonardo.

The repository package is structurally checked in CI, but that is not a
substitute for EasyEDA DRC or physical fit verification.

## Assembly order

1. Disconnect USB and inspect the bare PCB for shorts or damaged plating.
2. Fit the Arduino shield headers without solder. Use a Leonardo as an alignment
   fixture, keeping both boards parallel.
3. Solder one pin per header, recheck alignment, then solder the remaining pins.
4. Fit and solder the 2-, 4-, and 5-pin JST-XH board headers. Observe pin 1 and
   connector orientation from the silkscreen and Gerber viewer.
5. Check continuity from every signal to the matching Leonardo header and check
   that VCC is not shorted to GND.
6. Build each cable against `docs/pinout.md`; continuity-test both ends before
   attaching a switch, OLED, or encoder module.
7. Mate the shield to the unpowered Leonardo, then connect only USB for the
   first power-up. Stop immediately if either board heats up.

## Firmware and physical acceptance checklist

- [ ] `via_latching.hex` enumerates over USB and enters Caterina on reset.
- [ ] Layer 1 sends F13–F17 from SW1–SW4 and SW6.
- [ ] Layer 2 sends Previous, Play/Pause, Next, Rewind, and Fast-forward.
- [ ] `via_latching`: S5 ON selects Layer 2; OFF selects Layer 1.
- [ ] `via_toggle`: every debounced S5 press changes layer once.
- [ ] OLED shows only `LAYER 1` or `LAYER 2` and uses address `0x3C`.
- [ ] Encoder counter-clockwise/clockwise sends Volume Down/Up.
- [ ] Encoder click sends Mute.
- [ ] All six VIA keys and both encoder directions can be remapped.
- [ ] VIA mappings survive USB disconnect/reconnect.
- [ ] Encoder direction and every connector pin agree with the documented cable.

Record the tested PCB revision, Leonardo revision, OLED module, encoder module,
firmware variant, and firmware commit when completing this checklist.

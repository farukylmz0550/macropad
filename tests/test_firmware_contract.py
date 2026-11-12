import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/macropad_v3"


class FirmwareContractTest(unittest.TestCase):
    def test_target_and_pin_mapping(self):
        info = json.loads((FW / "keyboard.json").read_text())
        self.assertEqual(info["processor"], "atmega32u4")
        self.assertEqual(info["bootloader"], "caterina")
        self.assertEqual(info["dynamic_keymap"]["layer_count"], 2)
        self.assertEqual(
            info["matrix_pins"]["direct"][0],
            ["E6", "B4", "B5", "D6", "B6", "D7"],
        )
        self.assertEqual(info["encoder"]["rotary"][0]["pin_a"], "D4")
        self.assertEqual(info["encoder"]["rotary"][0]["pin_b"], "C6")

    def test_default_layers_and_encoder(self):
        source = (FW / "keymap_common.c").read_text()
        self.assertIn("KC_F13,  KC_F14,  KC_F15, KC_F16,  KC_F17,  KC_MUTE", source)
        self.assertIn("KC_MPRV, KC_MPLY, KC_MNXT, KC_MRWD, KC_MFFD, KC_MUTE", source)
        self.assertEqual(source.count("ENCODER_CCW_CW(KC_VOLD, KC_VOLU)"), 2)

    def test_variants_only_select_s5_mode(self):
        latching = (FW / "keymaps/via_latching/keymap.c").read_text().strip()
        toggle = (FW / "keymaps/via_toggle/keymap.c").read_text().strip()
        self.assertEqual(latching, toggle)
        self.assertEqual(
            (FW / "keymaps/via_latching/rules.mk").read_text(),
            (FW / "keymaps/via_toggle/rules.mk").read_text(),
        )
        self.assertIn("MACROPAD_S5_LATCHING", (FW / "keymaps/via_latching/config.h").read_text())
        self.assertFalse((FW / "keymaps/via_toggle/config.h").exists())
        common = (FW / "macropad_v3.c").read_text()
        self.assertIn("gpio_set_pin_input_high(MACROPAD_S5_PIN)", common)
        self.assertIn("layer_move(pressed ? 1 : 0)", common)

    def test_size_features_are_disabled(self):
        rules = (FW / "rules.mk").read_text()
        keymap_rules = (FW / "keymaps/via_latching/rules.mk").read_text()
        info = json.loads((FW / "keyboard.json").read_text())
        self.assertIn("VIA_ENABLE = yes", keymap_rules)
        self.assertIn("ENCODER_MAP_ENABLE = yes", keymap_rules)
        self.assertTrue(info["build"]["lto"])
        for feature in (
            "AUDIO_ENABLE",
            "BACKLIGHT_ENABLE",
            "OLED_ENABLE",
            "RGBLIGHT_ENABLE",
            "RGB_MATRIX_ENABLE",
            "UNICODE_ENABLE",
        ):
            self.assertIn(f"{feature} = no", rules)
        for feature in ("bootmagic", "command", "console", "mousekey", "nkro"):
            self.assertFalse(info["features"].get(feature, False))

    def test_oled_has_no_framebuffer_or_dynamic_allocation(self):
        source = (FW / "macropad_v3.c").read_text()
        self.assertIn('"i2c_master.h"', source)
        self.assertNotIn("malloc(", source)
        self.assertNotIn("calloc(", source)
        self.assertNotIn("oled_buffer", source)
        self.assertIn("uint8_t zeros[17]", source)
        self.assertIn("LAYER 1", source)
        self.assertIn("LAYER 2", source)

    def test_via_definition_matches_firmware(self):
        info = json.loads((FW / "keyboard.json").read_text())
        via = json.loads((ROOT / "via/macropad_v3.json").read_text())
        self.assertEqual(via["vendorId"], info["usb"]["vid"])
        self.assertEqual(via["productId"], info["usb"]["pid"])
        self.assertEqual(via["matrix"], {"rows": 1, "cols": 6})
        self.assertIn("e0", str(via["layouts"]["keymap"]))


if __name__ == "__main__":
    unittest.main()

// Copyright 2026 farukylmz0550
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

enum layer_names {
    _LAYER_1,
    _LAYER_2,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_LAYER_1] = LAYOUT(KC_F13,  KC_F14,  KC_F15, KC_F16,  KC_F17,  KC_MUTE),
    [_LAYER_2] = LAYOUT(KC_MPRV, KC_MPLY, KC_MNXT, KC_MRWD, KC_MFFD, KC_MUTE),
};

#ifdef ENCODER_MAP_ENABLE
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [_LAYER_1] = {ENCODER_CCW_CW(KC_VOLD, KC_VOLU)},
    [_LAYER_2] = {ENCODER_CCW_CW(KC_VOLD, KC_VOLU)},
};
#endif

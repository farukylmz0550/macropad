// Copyright 2026 farukylmz0550
// SPDX-License-Identifier: GPL-2.0-or-later

#include "quantum.h"

#include "i2c_master.h"

#define OLED_I2C_ADDRESS (MACROPAD_OLED_ADDRESS << 1)
#define OLED_TIMEOUT_MS 100
#define OLED_TEXT_PAGE 3
#define OLED_TEXT_COLUMN 43

// Only the glyphs required by "LAYER 1" and "LAYER 2" are stored. Each glyph
// is five columns wide and lives in flash, not SRAM.
static const uint8_t PROGMEM layer_font[][5] = {
    {0x7F, 0x40, 0x40, 0x40, 0x40}, // L
    {0x7E, 0x11, 0x11, 0x11, 0x7E}, // A
    {0x03, 0x04, 0x78, 0x04, 0x03}, // Y
    {0x7F, 0x49, 0x49, 0x49, 0x41}, // E
    {0x7F, 0x09, 0x19, 0x29, 0x46}, // R
    {0x00, 0x00, 0x00, 0x00, 0x00}, // space
    {0x00, 0x42, 0x7F, 0x40, 0x00}, // 1
    {0x62, 0x51, 0x49, 0x49, 0x46}, // 2
};

static uint8_t displayed_layer = 0xFF;
static bool    s5_candidate_pressed;
static bool    s5_stable_pressed;
static uint16_t s5_changed_at;

static bool oled_write(const uint8_t *data, uint8_t length) {
    return i2c_transmit(OLED_I2C_ADDRESS, data, length, OLED_TIMEOUT_MS) == I2C_STATUS_SUCCESS;
}

static bool oled_commands(const uint8_t *commands, uint8_t count) {
    uint8_t packet[17];

    if (count > 16) {
        return false;
    }

    packet[0] = 0x00;
    for (uint8_t i = 0; i < count; ++i) {
        packet[i + 1] = commands[i];
    }
    return oled_write(packet, count + 1);
}

static void oled_set_cursor(uint8_t page, uint8_t column) {
    const uint8_t commands[] = {
        (uint8_t)(0xB0 | (page & 0x07)),
        (uint8_t)(column & 0x0F),
        (uint8_t)(0x10 | (column >> 4)),
    };
    oled_commands(commands, sizeof(commands));
}

static void oled_clear(void) {
    uint8_t zeros[17] = {0x40};

    for (uint8_t page = 0; page < 8; ++page) {
        oled_set_cursor(page, 0);
        for (uint8_t block = 0; block < 8; ++block) {
            oled_write(zeros, sizeof(zeros));
        }
    }
}

static void oled_write_glyph(uint8_t glyph_index) {
    uint8_t packet[7] = {0x40};

    for (uint8_t column = 0; column < 5; ++column) {
        packet[column + 1] = pgm_read_byte(&layer_font[glyph_index][column]);
    }
    packet[6] = 0x00;
    oled_write(packet, sizeof(packet));
}

static void oled_draw_layer(uint8_t layer) {
    static const uint8_t PROGMEM text_prefix[] = {0, 1, 2, 3, 4, 5};

    if (layer == displayed_layer) {
        return;
    }

    oled_set_cursor(OLED_TEXT_PAGE, OLED_TEXT_COLUMN);
    for (uint8_t i = 0; i < sizeof(text_prefix); ++i) {
        oled_write_glyph(pgm_read_byte(&text_prefix[i]));
    }
    oled_write_glyph(layer == 0 ? 6 : 7);
    displayed_layer = layer;
}

static void oled_init_minimal(void) {
    static const uint8_t init_commands[] = {
        0xAE,       // display off
        0xD5, 0x80, // clock divide
        0xA8, 0x3F, // 1/64 multiplex
        0xD3, 0x00, // no vertical offset
        0x40,       // start line 0
        0x8D, 0x14, // charge pump on
        0x20, 0x02, // page addressing mode
        0xA1,       // segment remap
        0xC8,       // COM scan direction
        0xDA, 0x12, // COM pin configuration for 128x64
        0x81, 0x7F, // contrast
        0xD9, 0xF1, // pre-charge
        0xDB, 0x40, // VCOM detect
        0xA4,       // display follows RAM
        0xA6,       // normal display
        0xAF,       // display on
    };

    i2c_init();
    // The command helper intentionally caps packets at 16 payload bytes.
    oled_commands(init_commands, 16);
    oled_commands(init_commands + 16, sizeof(init_commands) - 16);
    oled_clear();
    oled_draw_layer(0);
}

static void apply_s5_state(bool pressed) {
#ifdef MACROPAD_S5_LATCHING
    layer_move(pressed ? 1 : 0);
#else
    if (pressed) {
        layer_move(get_highest_layer(layer_state) == 0 ? 1 : 0);
    }
#endif
}

void keyboard_post_init_kb(void) {
    gpio_set_pin_input_high(MACROPAD_S5_PIN);
    s5_candidate_pressed = !gpio_read_pin(MACROPAD_S5_PIN);
    s5_stable_pressed    = s5_candidate_pressed;
    s5_changed_at        = timer_read();

    oled_init_minimal();
    apply_s5_state(s5_stable_pressed);
    keyboard_post_init_user();
}

void housekeeping_task_kb(void) {
    const bool pressed = !gpio_read_pin(MACROPAD_S5_PIN);

    if (pressed != s5_candidate_pressed) {
        s5_candidate_pressed = pressed;
        s5_changed_at        = timer_read();
    } else if (pressed != s5_stable_pressed && timer_elapsed(s5_changed_at) >= MACROPAD_S5_DEBOUNCE_MS) {
        s5_stable_pressed = pressed;
        apply_s5_state(pressed);
    }
}

layer_state_t layer_state_set_kb(layer_state_t state) {
    const uint8_t layer = get_highest_layer(state);
    oled_draw_layer(layer == 0 ? 0 : 1);
    return layer_state_set_user(state);
}

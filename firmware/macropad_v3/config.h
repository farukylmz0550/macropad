// Copyright 2026 farukylmz0550
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

// S5 is separate from the VIA matrix and is debounced by macropad_v3.c.
#define MACROPAD_S5_PIN B7
#define MACROPAD_S5_DEBOUNCE_MS 5

// Minimal direct-write SSD1306 driver; QMK OLED_ENABLE stays disabled so no
// 1024-byte 128x64 framebuffer is allocated.
#define MACROPAD_OLED_ADDRESS 0x3C

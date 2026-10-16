#pragma once
#include <stdbool.h>
#include <furi_hal.h>
#include <furi_hal_resources.h>
/* External PC0 only. Never use RF/NFC/SWD/system pins as generic GPIO. */
typedef struct {
    const GpioPin* pin;
    bool initialized;
} SolGpioObserver;

bool sol_stm32wb_gpio_begin(SolGpioObserver* self);
bool sol_stm32wb_gpio_sample(const SolGpioObserver* self, bool* high);
void sol_stm32wb_gpio_end(SolGpioObserver* self);

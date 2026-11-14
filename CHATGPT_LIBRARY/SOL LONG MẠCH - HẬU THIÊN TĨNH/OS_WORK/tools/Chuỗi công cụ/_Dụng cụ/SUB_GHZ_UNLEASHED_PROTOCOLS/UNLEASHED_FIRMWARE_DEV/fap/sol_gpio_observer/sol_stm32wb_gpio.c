#include "sol_stm32wb_gpio.h"
#include <stddef.h>

/* Device-side STM32WB55 HAL driver. Source builds against full Flipper SDK. */
bool sol_stm32wb_gpio_begin(SolGpioObserver* self) {
    if(!self || self->initialized) return false;
    self->pin = &gpio_ext_pc0;
    furi_hal_gpio_init(self->pin, GpioModeInput, GpioPullNo, GpioSpeedLow);
    self->initialized = true;
    return true;
}

bool sol_stm32wb_gpio_sample(const SolGpioObserver* self, bool* high) {
    if(!self || !high || !self->initialized) return false;
    *high = furi_hal_gpio_read(self->pin);
    return true;
}

void sol_stm32wb_gpio_end(SolGpioObserver* self) {
    if(!self || !self->initialized) return;
    furi_hal_gpio_init(self->pin, GpioModeAnalog, GpioPullNo, GpioSpeedLow);
    self->initialized = false;
}

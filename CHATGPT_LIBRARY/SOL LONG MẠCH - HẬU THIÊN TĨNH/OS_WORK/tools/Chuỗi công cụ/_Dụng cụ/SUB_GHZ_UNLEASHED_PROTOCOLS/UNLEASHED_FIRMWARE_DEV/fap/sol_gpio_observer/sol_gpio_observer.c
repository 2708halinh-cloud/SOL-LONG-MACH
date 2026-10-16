#include <furi.h>
#include <furi_hal.h>
#include "sol_stm32wb_gpio.h"

/* A bounded, non-transmitting hardware test: 10 samples from external PC0. */
int32_t sol_gpio_observer_main(void* context) {
    UNUSED(context);
    SolGpioObserver observer = {0};
    if(!sol_stm32wb_gpio_begin(&observer)) return -1;
    for(unsigned i = 0; i < 10; ++i) {
        bool high = false;
        if(sol_stm32wb_gpio_sample(&observer, &high)) {
            FURI_LOG_I("SOLGPIO", "PC0 sample %u = %u", i, high ? 1U : 0U);
        }
        furi_delay_ms(200);
    }
    sol_stm32wb_gpio_end(&observer);
    return 0;
}

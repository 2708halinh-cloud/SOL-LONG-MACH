#pragma once
#include <stdbool.h>
typedef struct {int port;} GpioPin;
typedef enum {GpioModeInput, GpioModeAnalog} GpioMode;
typedef enum {GpioPullNo} GpioPull;
typedef enum {GpioSpeedLow} GpioSpeed;
void furi_hal_gpio_init(const GpioPin*,GpioMode,GpioPull,GpioSpeed);
bool furi_hal_gpio_read(const GpioPin*);

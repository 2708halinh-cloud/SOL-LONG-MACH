#pragma once
#include <stdint.h>
#define UNUSED(x) ((void)(x))
#define FURI_LOG_I(tag,format,...) ((void)0)
void furi_delay_ms(uint32_t ms);

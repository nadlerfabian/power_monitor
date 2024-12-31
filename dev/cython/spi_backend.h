#ifndef SPI_BACKEND_H
#define SPI_BACKEND_H

#include <stdint.h>

// Public functions
int spi_init();
void spi_close();
int spi_collect_samples(uint16_t *samples, uint64_t *timestamps, int max_samples, int duration_ms);

#endif // SPI_BACKEND_H

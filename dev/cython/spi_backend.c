#include "spi_backend.h"
#include <bcm2835.h>
#include <stdint.h>
#include <time.h>
#include <stdio.h>

// Get the current time in milliseconds (private function)
static uint64_t current_time_ms() {
    struct timespec spec;
    clock_gettime(CLOCK_MONOTONIC, &spec);
    return (uint64_t)(spec.tv_sec * 1000 + spec.tv_nsec / 1000000);
}

// Initialize SPI
int spi_init() {
    if (!bcm2835_init()) {
        printf("bcm2835_init() failed!\n");
        return 0; // Initialization failed
    }
    if (!bcm2835_spi_begin()) {
        printf("bcm2835_spi_begin() failed!\n");
        return 0; // SPI setup failed
    }
    bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_256); // 1.5625MHz
    printf("SPI initialized successfully!\n");
    return 1; // Success
}

// Cleanup SPI
void spi_close() {
    bcm2835_spi_end();
    bcm2835_close();
}

// Collect samples and their timestamps
int spi_collect_samples_with_timestamps(uint16_t *samples, uint64_t *timestamps, int max_samples, int duration_ms) {
    char tx_buf[2] = {0};
    char rx_buf[2] = {0};
    uint64_t start_time = current_time_ms();
    uint64_t current_time;
    int sample_count = 0;

    while ((current_time = current_time_ms()) - start_time < (uint64_t)duration_ms) {
        if (sample_count >= max_samples) {
            break; // Avoid exceeding buffer size
        }

        bcm2835_spi_transfernb(tx_buf, rx_buf, 2);
        samples[sample_count] = ((rx_buf[0] & 0x1F) << 7) | (rx_buf[1] >> 1); // 12-bit ADC value
        timestamps[sample_count] = current_time;
        sample_count++;
    }

    return sample_count; // Return the number of collected samples
}

import numpy as np
cimport numpy as np

cdef extern from "spi_backend.h":
    int spi_init()
    void spi_close()
    int spi_collect_samples(unsigned short *samples, int max_samples, int duration_ms)

def initialize_spi():
    if not spi_init():
        raise RuntimeError("Failed to initialize SPI")

def close_spi():
    spi_close()

def collect_samples(int max_samples, int duration_ms):
    """
    Collect as many samples as possible within the given duration (ms).
    :param max_samples: Maximum buffer size for samples.
    :param duration_ms: Time duration to collect samples in milliseconds.
    :return: List of collected samples.
    """
    cdef np.ndarray[np.uint16_t, ndim=1] samples = np.zeros(max_samples, dtype=np.uint16)
    cdef unsigned short *data_ptr = <unsigned short *>np.PyArray_DATA(samples)
    cdef int collected = spi_collect_samples(data_ptr, max_samples, duration_ms)
    return samples[:collected].tolist()

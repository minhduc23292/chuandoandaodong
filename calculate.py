import math
import numpy as np
def rmsValue(arr):
    square = 0
    mean = 0.0
    rms = 0.0
    n = len(arr)
    # Calculate square
    for i in range(0, n):
        square += (arr[i] ** 2)

        # Calculate Mean
    mean = (square / (float)(n))
    # Calculate Root
    rms = math.sqrt(mean)
    return rms
def find_max(arr):
    pos=0
    n=len(arr)
    max=arr[0]
    for i in range(1,n):
        if(arr[i]>max):
            max=arr[i]
            pos=i
    return pos

def hamming(M):
    """Return an M + 1 point symmetric hamming window."""
    if M % 2:
        raise Exception('M must be even')
    return 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(M + 1) / M)


def blackman(M):
    """Return an M + 1 point symmetric point hamming window."""
    if M % 2:
        raise Exception('M must be even')
    return (0.42 - 0.5 * np.cos(2 * np.pi * np.arange(M + 1) / M) +
            0.08 * np.cos(4 * np.pi * np.arange(M + 1) / M))


def sinc_filter(M, fc):
    """Return an M + 1 point symmetric point sinc kernel with normalised cut-off
    frequency fc 0->0.5."""
    if M % 2:
        raise Exception('M must be even')
    return np.sinc(2 * fc * (np.arange(M + 1) - M / 2))


def build_filter(M, fc, window=None):
    """Construct filter using the windowing method for filter parameters M
    number of taps, cut-off frequency fc and window. Window defaults to None
    i.e. a rectangular window."""
    if window is None:
        h = sinc_filter(M, fc)
    else:
        h = sinc_filter(M, fc) * window(M)
    return h / h.sum()
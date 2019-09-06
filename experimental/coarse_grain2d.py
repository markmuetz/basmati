# coding: utf-8
import numpy as np
from scipy import ndimage

def coarse_grain2d(arr, grain_size):
    assert arr.shape[0] % grain_size[0] == 0
    assert arr.shape[1] % grain_size[1] == 0
    num0 = arr.shape[0] // grain_size[0]
    num1 = arr.shape[1] // grain_size[1]
    num_grains = num0 * num1
    index = np.arange(num_grains)
    labels = index.reshape((num0, num1)).repeat(grain_size[1], axis=1).repeat(grain_size[0], axis=0)
    return ndimage.mean(arr, labels=labels, index=index).reshape(num0, num1)
    
    

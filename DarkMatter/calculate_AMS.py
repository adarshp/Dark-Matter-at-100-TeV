#!/usr/bin/env python

from __future__ import division
import numpy as np

def calculate_AMS(s, b):
    br = 3
    return np.sqrt(2*((s+b+br)*np.log(1+(s/(b+br)))-s))

if __name__ == '__main__':
    significance = calculate_AMS(50, 30)
    print(significance, 50/np.sqrt(30+3))

#!usr/bin/env python
import os
import numpy as np
import itertools as it
import contextlib
import untangle

def razor_combinations():
    # Making a list of razor variable combinations
    m_Rs = np.arange(0.0, 4000.0, 100.0)
    m_T_Rs = np.arange(0.0, 2000.0, 100.0)
    razor_combinations = list(it.product(m_Rs, m_T_Rs))
    return razor_combinations

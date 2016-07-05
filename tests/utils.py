"""
Various testing utilities
"""

import math
import random


def random_float():
    abs_val = math.exp(random.uniform(-200, 200))
    return abs_val if random.random() < 0.5 else -abs_val

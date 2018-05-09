import numpy as np

eps = 1e-4

def SMAPE(actual, pred):
    p = pred
    p[pred < 0] = 0
    return np.mean(np.abs(actual - p) / ((actual + p + eps) / 2.0))

from scipy.stats import levy_stable
import numpy as np
import torch
from levy_stable_pytorch import LevyStable
from levy_gaussian_combined import LevyGaussian
import time
import util

def test_cache_improvement():
    alpha = 1.7
    x = torch.arange(-10, 10, 0.00001) # size = 2000000

    start = time.time()
    levy_gaussian = LevyGaussian(alpha=alpha, sigma_1=1, sigma_2=1, type="cft")
    tmp = levy_gaussian.score(x)
    print("\n")
    print(f"first computation takes {time.time() - start}s")

    start = time.time()
    levy_gaussian = LevyGaussian(alpha=alpha, sigma_1=1, sigma_2=1, type="cft")
    tmp = levy_gaussian.score(x)
    print(f"second computation takes {time.time() - start}s")

    start = time.time()
    levy_gaussian = LevyGaussian(alpha=alpha, sigma_1=1, sigma_2=1, type="cft")
    tmp = levy_gaussian.score(x)
    print(f"third computation takes {time.time() - start}s")

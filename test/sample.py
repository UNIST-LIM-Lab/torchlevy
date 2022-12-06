from scipy.stats import levy_stable
import random
from torchlevy import LevyStable
import matplotlib.pyplot as plt
import numpy as np
import torch


def test_rejection_sampling():
    for threshold in range(2, 100):
        levy = LevyStable()
        y2 = levy.sample(alpha=1.7, size=(100, 100, 100), reject_threshold=threshold)
        assert (not torch.any(y2 > threshold))


def compare_scipy_and_torch():
    alphas = [1.7]  # [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    beta = 1

    for alpha in alphas:
        scale = random.uniform(1, 10)

        scipy_sample = levy_stable.rvs(alpha, beta, loc=0., scale=scale, size=100000)
        scipy_sample = np.clip(scipy_sample, -100, 100)

        plt.figure(figsize=(12, 6))
        plt.subplot(121)
        plt.hist(scipy_sample, bins=2000, facecolor='y', alpha=0.5, label="scipy_sample")
        plt.xlim(-50, 100)
        plt.legend()

        levy = LevyStable()
        torch_sample = levy.sample(alpha, beta, loc=0., scale=scale, size=100000).cpu()
        torch_sample = torch.clip(torch_sample, -100, 100)
        plt.subplot(122)
        plt.hist(torch_sample, bins=2000, facecolor='blue', alpha=0.5, label="torch_sample")
        plt.xlim(-50, 100)
        plt.legend()
        plt.show()


def plot_isotropic():
    levy = LevyStable()

    alpha = 1.5
    e = levy.sample(alpha, size=[10000, 2, 1000], is_isotropic=False).cpu()
    e = torch.sum(e, dim=-1) / 32
    plt.xlim([-200, 200])
    plt.ylim([-200, 200])
    plt.scatter(e[:, 0], e[:, 1], marker='.')
    plt.gca().set_aspect('equal')
    plt.show()

def test_isotropic():

    levy = LevyStable()
    alpha = 1.8
    e = levy.sample(alpha, size=[100, 3, 128, 128], is_isotropic=False).cpu()
    print("isotropic: ", e.max(), e.min())
    e = levy.sample(alpha, size=[100, 3, 128, 128], is_isotropic=True).cpu()
    print("non-isotropic: ", e.max(), e.min())

def test_nan():

    levy = LevyStable()
    alphas = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
    # for alpha in alphas:
    #     for i in range(1000):
    #         e = levy.sample(alpha, size=(100, 100, 100))
    #         assert torch.all(torch.isfinite(e))
    #
    #         e = levy.sample(alpha, size=(100, 100, 100), is_isotropic=True, clamp_threshold=20)
    #         assert torch.all(torch.isfinite(e))
    for i in range(1000):
        e = levy.sample(1.2, size=(50000, 2), is_isotropic=True)
        assert not torch.any(torch.isnan(e))
    print("test nan passed")


def test_beta1():
    levy = LevyStable()

    alphas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for alpha in alphas:
        for i in range(1000):
            x = levy.sample(alpha, beta=1, size=(50000,))
            if torch.any(x < 0):
                print(alpha)
                print(1111, x[x < 0])
                # raise RuntimeError()


def test_scipy_beta1():
    # levy = LevyStable()

    alphas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for alpha in alphas:
        for i in range(1000):
            x = levy_stable.rvs(alpha, beta=1, size=50000)
            if torch.any(torch.from_numpy(x < 0)):
                print(alpha)
                print(1111, x[x < 0])


if __name__ == "__main__":
    # test_sample_clamp()
    # compare_scipy_and_torch()
    # plot_isotropic()
    plot_isotropic()


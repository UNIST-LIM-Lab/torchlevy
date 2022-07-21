
import torch
import scipy
import numpy as np
from Cython import inline
from scipy.stats import levy_stable
from functools import partial
from torchquad import set_up_backend  # Necessary to enable GPU support
from torchquad import Trapezoid, Simpson, Boole, MonteCarlo, VEGAS # The available integrators

from scipy.stats import levy_stable
from scipy import optimize

from scipy import integrate
import scipy.special as sc

def gaussian_pdf(x, mu=0, sigma=np.sqrt(2)):
    return 1 / (sigma * np.sqrt(2*np.pi)) * np.exp(-1/2 * ((x-mu) / sigma) ** 2)

def gaussian_score(x, mu=0, sigma=np.sqrt(2)):
    return (mu - x) / (sigma ** 2)



def alpha_stable_score_fourier_transform(x, alpha):
    """
        get alpha stable score through fourier transform
        unfortunately, not working properly
    """
    N = 100
    diff_q = torch.tensor(0, dtype=torch.complex128)
    q = torch.tensor(0, dtype=torch.complex128)
    i = torch.complex(torch.tensor(0, dtype=torch.float64), torch.tensor(1, dtype=torch.float64))

    for t in range(0, N):
        tmp = torch.exp(-(torch.abs(torch.tensor(2*torch.pi*t/N)) ** alpha) - i * 2*torch.pi * x * t / N)
        diff_q += -2 * torch.pi * i * t / N * tmp
        q += tmp

    return diff_q / q


def alpha_stable_score_finite_diff(x, alpha):
    """
        calculate alpha stable score through finite difference
    """
    def grad_approx(func, x, h=0.001):
        # https://arxiv.org/abs/1607.04247
        if type(x) is np.ndarray and type(h) is not np.ndarray:
            h = np.array(h)

        return (-func(x+2*h) + 8*func(x+h) - 8*func(x-h) + func(x-2*h)) / (12*h)

    levy_logpdf = partial(levy_stable.logpdf, alpha=alpha, beta=0)

    return grad_approx(levy_logpdf, x)


def alpha_stable_pdf_zolotarev(x, alpha, beta=0):
    """
        get alpha stable score through zolotarev thm
        ref. page 7, https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2894444_code545.pdf?abstractid=2894444&mirid=1
    """
    pi = torch.tensor(torch.pi)
    zeta = -beta * torch.tan(pi * alpha / 2.)
    if alpha != 1:
        x0 = x + zeta  # convert to S_0 parameterization
        xi = torch.arctan(-zeta) / alpha

        def V(theta):
            return torch.cos(alpha * xi) ** (1 / (alpha - 1)) * \
                   (torch.cos(theta) / torch.sin(alpha * (xi + theta))) ** (alpha / (alpha - 1)) * \
                   (torch.cos(alpha * xi + (alpha - 1) * theta) / torch.cos(theta))

        if x0 > zeta:
            @inline
            def g(theta):
                return V(theta) * (x0 - zeta) ** (alpha / (alpha - 1))

            @inline
            def f(theta):
                g_ret = g(theta)
                g_ret = torch.nan_to_num(g_ret, posinf=0, neginf=0)

                return g_ret * torch.exp(-g_ret)

            # spare calculating integral on null set
            # use isclose as macos has fp differences
            if torch.isclose(-xi, pi / 2, rtol=1e-014, atol=1e-014):
                return 0.

            simp = Simpson()
            intg = simp.integrate(f, dim=1, N=101, integration_domain=[[-xi + 1e-7, torch.pi / 2 - 1e-7]])

            return alpha * intg / np.pi / torch.abs(torch.tensor(alpha - 1)) / (x0 - zeta)

        elif x0 == zeta:
            # couldn't find gamma function in pytorch
            return torch.exp(torch.special.gammaln(1 + 1 / alpha)) * np.cos(xi) / np.pi / ((1 + zeta ** 2) ** (1 / alpha / 2))
        else:
            return alpha_stable_pdf_zolotarev(-x, alpha, -beta)
    else:
        raise NotImplementedError("This function can't handle when alpha==1")


def alpha_stable_pdf_zolotarev_simple(x, alpha):
    """
        simplified version of alpha_stable_pdf_zolotarev,
        assume alpha > 1 and beta = 0
    """

    x_ = x.clone().detach()
    inverse_operand = - 2 * (x_ < 0) + 1
    x = x * inverse_operand


    def V(theta):
        return (torch.cos(theta) / torch.sin(alpha * theta)) ** (alpha / (alpha - 1)) * \
               (torch.cos((alpha - 1) * theta) / torch.cos(theta))

    def g(theta):
        return V(theta) * x ** (alpha / (alpha - 1))


    def f(theta):
        g_ret = g(theta)
        g_ret = torch.nan_to_num(g_ret, posinf=0, neginf=0)

        return g_ret * torch.exp(-g_ret)


    simp = Simpson()
    intg = simp.integrate(f, dim=1, N=100, integration_domain=[[1e-7, torch.pi / 2 - 1e-7]])

    return alpha * intg / np.pi / torch.abs(torch.tensor(alpha - 1)) / x


def alpha_stable_score_zolotarev_autograd(x, alpha):

    x.requires_grad_()
    log_likelihood = torch.log(alpha_stable_pdf_zolotarev_simple(x, alpha))
    grad = torch.autograd.grad(log_likelihood.sum(), x)[0]

    return grad



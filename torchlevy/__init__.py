from .levy_gaussian import LevyGaussian
from .levy import LevyStable
from .approx_score import get_approx_score, rectified_tuning_score, real_linear_tuning_score, fitting_gen_gaussian_score, generalized_gaussian_score

from torchquad import set_up_backend  # Necessary to enable GPU support
import torch

if torch.cuda.is_available():
    set_up_backend("torch")
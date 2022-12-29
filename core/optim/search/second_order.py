import sys, os
sys.path.insert(1, os.getcwd())
from HesScale.hesscale import HesScale
from torch.nn import functional as F
import torch

# Utility-based Search Optimizers
class SecondOrderSearchNormal(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-5, beta_utility=0.0, temp=1.0):
        defaults = dict(lr=lr, beta_utility=beta_utility, temp=temp)
        super(SecondOrderSearchNormal, self).__init__(params, defaults)

    def step(self):
        for group in self.param_groups:
            for p in group["params"]:
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["avg_utility"] = torch.zeros_like(p.data)
                state["step"] += 1
                bias_correction = 1 - group["beta_utility"] ** state["step"]
                noise = torch.randn_like(p.grad)
                avg_utility = state["avg_utility"]
                hess_param = getattr(p, group["method_field"])
                utility = 0.5 * hess_param * p.data ** 2 - p.grad.data * p.data
                avg_utility.mul_(group["beta_utility"]).add_(
                    utility, alpha=1 - group["beta_utility"]
                )
                p.data.add_(
                    noise
                    * (
                        1
                        - torch.tanh_(
                            F.normalize(avg_utility / bias_correction, dim=-1)
                            / group["temp"]
                        )
                    ),
                    alpha=-group["lr"],
                )


class SecondOrderSearchAntiCorr(torch.optim.Optimizer):
    method = HesScale()
    def __init__(self, params, lr=1e-5, beta_utility=0.0, temp=1.0, sigma=1.0):
        defaults = dict(lr=lr, beta_utility=beta_utility, temp=temp, sigma=sigma, method_field=type(self).method.savefield)
        super(SecondOrderSearchAntiCorr, self).__init__(params, defaults)

    def step(self, loss):
        for group in self.param_groups:
            for p in group["params"]:
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["avg_utility"] = torch.zeros_like(p.data)
                    state["prev_noise"] = torch.zeros_like(p.data)
                state["step"] += 1
                bias_correction = 1 - group["beta_utility"] ** state["step"]
                new_noise = torch.randn_like(p.grad) * group["sigma"] * torch.tanh(loss)
                noise = new_noise - state["prev_noise"]
                state["prev_noise"] = new_noise
                avg_utility = state["avg_utility"]
                hess_param = getattr(p, group["method_field"])
                utility = 0.5 * hess_param * p.data ** 2 - p.grad.data * p.data
                avg_utility.mul_(group["beta_utility"]).add_(
                    utility, alpha=1 - group["beta_utility"]
                )
                p.data.add_(
                    noise
                    * (
                        1
                        - torch.tanh_(
                            F.normalize(avg_utility / bias_correction, dim=-1)
                            / group["temp"]
                        )
                    ),
                    alpha=-group["lr"],
                )

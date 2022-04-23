import numpy as np
import pandas as pd
import pdb

class model(object):
    """
    Class that provides methods to model different processes.
    Processes available so far:
        - Black-Scholes (default)
        - Heston
    """

    def __init__(self, process = 'black-scholes', r = .05, vol = .2, S0 = 100):

        self.process = process
        self.m = 10
        self.n = 252
        self.dt = 1/self.n
        self.S0 = S0
        self.r = r
        self.vol = vol

    def create_path(self, model_specification='no-jump', *args):
        path = np.zeros(shape=(self.m, self.n))
        path[:, 0] = self.S0

        if self.process == 'black-scholes':
            path[:, 1:] = np.exp((self.r - (self.vol ** 2) / 2) * self.dt + self.vol * self.dt ** (0.5) * \
                                 np.random.normal(size=(self.m, self.n - 1)))
            if model_specification == 'no-jump':
                """
                log(St/St-1) = (r-vol2/2) * dt + vol * dt**(0.5) * Wt
                """
                pass
            elif model_specification == 'merton':
                """
                log(St/St-1) = (r-vol2/2) * dt + vol * dt**(0.5) * Wt + JtNt
                args = (lambda, mu_j, vol_j)
                """
                Nt, Jt = np.zeros(shape=(self.m,self.n)), np.zeros(shape=(self.m,self.n))
                Nt[:, 1:] = np.random.poisson(lam=self.dt*args[0],size=(self.m,self.n-1))
                Jt[:, 1:] = np.random.normal(loc=args[1],scale=args[2], size=(self.m, self.n - 1))
                jump_t = Nt*Jt
                path = path+jump_t

        elif self.process == 'heston':
            cov = np.array([[1, args[0]], [args[0], 1]])
            """
            args = (rho, k, eta, theta)
            """
            """
            cov --> cholesky decomposition --> chol*Mx2 N(0,1)
            """
            vol_t = np.zeros(shape=(self.m, self.n))
            vol_t[:, 0] = self.vol
            for i in range(1, self.n):
                W = np.random.multivariate_normal(mean=[0, 0], cov=cov, size=self.m)
                Wt, W_tilde_t = W[:, 0], W[:, -1]
                vol_t[:, i] = vol_t[:, i - 1] + args[1] * (args[2] - vol_t[:, i - 1]) * self.dt + \
                              args[3] * np.sqrt(abs(vol_t[:, i - 1])) * W_tilde_t
            vol_t = np.sqrt(np.abs(vol_t))
            if model_specification == 'no-jump':
                path[:, 1:] = np.exp((self.r - (vol_t[:, 1:] ** 0.5) / 2) * self.dt + vol_t[:, 1:]**0.5 \
                                     * self.dt ** (0.5) * np.random.normal(size=(self.m, self.n - 1)))
            elif model_specification == 'bates':
                """
                args = (rho, k, eta, theta, l_poisson, mu_j, vol_j)
                """
                Nt, Jt = np.zeros(shape=(self.m, self.n)), np.zeros(shape=(self.m, self.n))
                Nt[:, 1:] = np.random.poisson(lam=self.dt * args[4], size=(self.m, self.n - 1))
                Jt[:, 1:] = np.exp(np.random.normal(loc=np.log(args[4]+1)-args[5]**2/2, scale=args[5]**2,\
                                             size=(self.m, self.n - 1)))-1

                path[:, 1:] = np.exp((self.r - ((vol_t[:, 1:] ** 0.5) / 2) - args[4]*args[5]) * self.dt + vol_t[:, 1:] \
                                     ** 0.5 * self.dt ** (0.5) * np.random.normal(size=(self.m, self.n - 1)))

                jump_t = Nt * Jt
                path = path + jump_t
            else:
                pass
        path = pd.DataFrame(path).cumprod(axis=1)
        path = path.round(4).transpose().rename(columns={col:''.join(['path',str(col+1)]) for col in path.columns})
        return path


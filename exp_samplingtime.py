"""
Measure the sampling time
"""

import os
import sys
import random
import time
import math

import numpy as np
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# import u_time

from sampling_util import load_G
from models.model_RSSs import RSS, RSS2

# from Model_MCMC import MCMCSampling
# from Model_PSRW import PSRW


if __name__ == "__main__":

    # load arguments
    if len(sys.argv) < 3:
        print('please run like "python3 main.py ba10 3 RSS"')
        exit(0)

    # load
    data_name = sys.argv[1]
    k = int(sys.argv[2])
    model_name = sys.argv[3]
    n_samples = int(sys.argv[4]) if len(sys.argv) > 4 else 10

    # load graph data
    G = load_G(data_name + '.edg')

    n = len(G)
    m = len(nx.edges(G))

    # error parameter
    e = 0.05

    # load model
    if model_name == "RSS":
        sampler = RSS(G, e)
    elif model_name == "RSS+" or model_name == "RSS2":
        sampler = RSS2(G, e)
    elif model_name == "MCMC":
        sampler = MCMCSampling(G, e, use_buffer=False)
    elif model_name == "PSRW":
        sampler = PSRW(G, e, use_buffer=False)
    else:
        raise ValueError("%s is not implemented" % model_name)

    print('data set:', data_name)
    print("n=", n, ", m=", len(nx.edges(G)), ", k=", k, ", e=", e)
    print("model_name:", model_name)
    print("n_samples:", n_samples)

    # sampling start

    ts = []
    for l in range(n_samples):
        start = time.time()
        v = sampler.uniform_state_sample(k)
        t = time.time() - start
        ts.append(t)
        if l % int(n_samples / 10) == 0:
            print('%7d/%d %12.8f[s]' % (l, n_samples, t), ' sample:', v)

    averagetime = np.mean(ts)
    stdv = np.std(ts)
    print("Sampling time:", averagetime, ' +-', stdv, '[s]')

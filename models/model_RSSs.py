import math
import random
import networkx as nx
import numpy as np

from sampling_util import ln, binom, choose_one, degree, neighbor_states, diff, state_merge, num_edges_yields




class RSS:

    def __init__(self, G, e=0.01, mixing_time_ratio=1.0):
        self.G = G
        self.e = e
        self.mixing_time_ratio = mixing_time_ratio

        self.delta = max([nx.degree(G, n) for n in G.nodes()])

        # for uniform 2-subgraph sampling
        self.edges = [tuple(e) if e[0] < e[1] else (e[1], e[0]) for e in G.edges()]

        # for degree-prop 2-subgraph sampling
        self.edge_prob = [nx.degree(G, e[0]) + nx.degree(G, e[1]) - 2 for e in G.edges()]
        self.edge_prob = self.edge_prob / np.sum(self.edge_prob)
        self.edge_arange = np.arange(0, len(self.edges))

        self.n = len(self.G.nodes())

    def t_k(self, k):
        if self.mixing_time_ratio == 0:
            return 0
        e = self.e
        delta = self.delta
        n = len(self.G.nodes())

        rho = 2 * k * delta
        tau = rho * (ln(binom(n, k)) + ln(k) + ln(delta) + ln(1 / e))
        t = int(math.ceil(tau * self.mixing_time_ratio))
        return t

    def degree_prop_state_sample(self, k):
        if k == 2:
            return self.edges[np.random.choice(self.edge_arange, 1, p=self.edge_prob)[0]]

        curr_s = self.uniform_state_sample(k)
        curr_d = degree(self.G, curr_s)

        # MH Sampling
        for _ in range(self.t_k(k)):
            if random.random() < 1 / 2:
                continue

            next_s = self.uniform_state_sample(k)
            next_d = degree(self.G, next_s)

            if random.random() < next_d / curr_d:
                # accept
                curr_s = next_s
                curr_d = next_d
        return curr_s

    def uniform_state_sample(self, k):
        """
        :param G:
        :param k:
        :return: tuple
        """
        if k == 2:
            return choose_one(self.edges)

        while True:
            s = self.degree_prop_state_sample(k - 1)
            # print(s)
            s_neighbor = neighbor_states(self.G, s)
            n = choose_one(s_neighbor)
            m = num_edges_yields(s, n, s_neighbor)
            if random.random() < 1 / m:
                return state_merge(s, n)



class RSS2(RSS):
    """
    Only use degree_prop_sampling
    """

    def t_k(self, k):
        if self.mixing_time_ratio == 0:
            return 0
        e = self.e
        delta = self.delta
        n = self.n

        rho = 2 * k * delta
        tau = rho * (ln(binom(n, k)) + 3 * ln(k) + ln(delta) + ln(1 / e))
        t = int(math.ceil(tau * self.mixing_time_ratio))
        return t

    def estimate_degree(self, s, u, v, neighbors):
        """
        estimate degree of e in G_k, f in the paper
        :param e:
        :param neighbors: neighbors of e[0]
        :return:
        """
        return degree(self.G, s) / num_edges_yields(u, v, neighbors)

    def degree_prop_state_sample(self, k):
        if k == 2:
            return self.edges[np.random.choice(self.edge_arange, 1, p=self.edge_prob)[0]]

        u = self.degree_prop_state_sample(k - 1)
        neighbor_of_u = neighbor_states(self.G, u)
        v = choose_one(neighbor_of_u)
        curr_s = state_merge(u, v)
        curr_f = self.estimate_degree(curr_s, u, v, neighbor_of_u)

        # MH Sampling
        for _ in range(self.t_k(k)):
            if random.random() < 1 / 2:
                continue

            u = self.degree_prop_state_sample(k - 1)
            neighbor_of_u = neighbor_states(self.G,u)
            v = choose_one(neighbor_of_u)
            next_s = state_merge(u, v)
            next_f = self.estimate_degree(next_s, u, v, neighbor_of_u)

            if random.random() < min(1, next_f / curr_f):
                # accept
                curr_s = next_s
                curr_f = next_f
        return curr_s

import igraph as ig
import random

fname = ""
g = ig.Read_GraphML(fname)

g = ig.Graph.GRG(100, 0.2)
for node in range(100):
    g.vs[node]['opinion'] = random.sample([-1,1], 1)[0]

maxtstep = 200000
nocopy_prob = 0.05
nocopy_vals = [0.01, 0.05, 0.1]

Nnodes = len(g.vs())
for nocopy_prob in nocopy_vals:
    for t in range(maxtstep):
        node = random.randrange(1, Nnodes)
        rnum = random.random()
        if rnum <= nocopy_prob/2:
            g.vs[node]["opinion"] *= -1
        elif rnum > nocopy_prob:
            target_neighbor = random.sample(g.neighbors(node), 1)[0]
            g.vs[node]["opinion"] = g.vs[target_neighbor]["opinion"]
        
    dest_fname = "simulated_dynamic_" + str(nocopy_prob) + "_noise_" + str(maxtstep) + ".graphml"
    g.write_graphml(dest_fname)

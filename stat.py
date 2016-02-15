import matplotlib.pyplot as plt

def similars_hist(vertices_map):
    counts = []
    for v in train_vertices_map:
        counts.append(len(vertices_map[v]['similars']))
    plt.hist(counts, bins=40)
    plt.show()

def text_hist_clusters(graph):
    return Counter([len(g.vertices[x].vertices) for x in g.vertices])


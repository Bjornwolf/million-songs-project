
def dist(x, y):
    return 1/similarity[x][y]

def check_part(v, vertices):
    members = set([v])
    to_visit = map(lambda x: x[0], vertices[v].similars)
    while to_visit != []:
        v = to_visit[0]
        to_visit = to_visit[1:]
        if v not in members:
            members |= set([v])
            to_visit += list(set(map(lambda x: x[0], vertices[v].similars)) - members)
    return members

def check_graph(vertices):
    unvisited_ids = set(vertices.keys())
    for v in vertices:
        if v in unvisited_ids:
            members = check_part(v, vertices)
            print len(members)
            unvisited_ids -= members

class V:
    def __init__(self, ident, neighbours):
        self.similars = map(lambda x: (x, 1.), neighbours)
        self.track_id = ident

if __name__ == '__main__':
    vertices = {}
    vertices["1"] = V("1", ["3", "5"])
    vertices["2"] = V("2", ["4", "8"])
    vertices["3"] = V("3", ["1", "7"])
    vertices["4"] = V("4", ["2", "8"])
    vertices["5"] = V("5", ["1", "7"])
    vertices["6"] = V("6", [])
    vertices["7"] = V("7", ["3", "5"])
    vertices["8"] = V("8", ["4", "2"])

    check_graph(vertices)

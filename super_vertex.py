class SuperVertex(object):
    NEXT_SV_ID = 0

    def __init__(self, vertex):
        self.identity = SuperVertex.NEXT_SV_ID
        self.members = [vertex]
        self.tags = vertex['tags']
        # TODO: Use an external object for that.
        # TODO: You should have at least
        self.edges = self._similars_to_edges(vertex)

        SuperVertex.NEXT_SV_ID += 1

    def similars_to_edges(self, vertex):
        edges = set() 
        for similar in vertex['similars']:
            # TODO: Use an external object for that.
            # (Computing distance out of similarity is not the responsibility of
            # this object)
            edges.add((vertex['track_id'], similar[0], 1 / similar[1]))

    def similars_from_edges(self):
        edges_list = sorted(self.edges, lambda x: x[2])
        return [[tid, similarity] for _, tid, similarity in edges_list]

    def append(self, new_member):
        # TODO: Implement this method.
        pass

    def member_count(self):
        return len(self.members)
    
    def __getitem__(self, key, val):
        if key in ['tags', 'similars']:
            return { 'tags': self.tags,
                     'similars': self.similars_from_edges() 
                   }[key]
        else
            raise KeyError

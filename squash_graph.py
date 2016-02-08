class Graph(object):
    def __init__(self, vertices):
        self.sorted_edges = self._build_edge_list(vertices.values())
        self.vertices = []
        self.sv_map = {}
        self.edges = {}
        self.singular_vertices = 0

        for v in vertices:
            sv = SuperVertex(vertices[v])
            self.supervertex_mapping[v] = sv.identity
            self.vertices.append(sv)
            self.singular_vertices += 1
        for (v1, v2, weight) in self.sorted_edges:
            try:
                self.edges[sv_map[v1]].append((sv_map[v2], weight))
            except KeyError:
                self.edges[sv_map[v1]] = [(sv_map[v2], weight)]

        self.max_edge = self.sorted_edges[-1][2] 

        self.within_cluster_distance = 0.
        self.cluster_edginess = 
        self.between_cluster_distance = 

    def size(self):
        return len(self.vertices)

    def _build_edges_list(self, train_data):
        edges = set()
        for track in train_data:
            self._edges_from_similars(track, edges)

        return sorted(edges, lambda x: x[2])

    def _edges_from_similars(self, track, edges): 
        for similar in track['similars']:
            edges.add(self._edge(track, similar))

    def _edge(self, track, similar):
        return (min(track['trackid'], similar[0]), 
                max(track['trackid'], similar[0]),
                self._edge_weight(similar[1]))

    def _edge_weight(self, similarity):
        return 1 / similarity

class GraphSquasher(object):
    def __init__(self, radius):
        self.membership_lookup = dict() 
        self.members = []
        self.radius = radius
        self.next_supervertex_id = 1        

    def run(self, train_data, vertices):
        for edge in self._build_edges_list(train_data):
            v1 = vertices.get(edge[0], None)
            v2 = vertices.get(edge[1], None)
            weight = edge[2]

            if not v1 or not v2:
                continue

            if self._merge_target(v1, v2, weight):
                

    def _should_merge(self, v1, v2, weight):
        pass


    def _merge_target(self, v1, v2, weight):
       sv1 = self.membership_lookup.get(v1['track_id'], v1)
       sv2 = self.membership_lookup.get(v2['track_id'], v2)

       sv1_loss_delta = float("inf")
       sv2_loss_delta = float("inf")

       if sv1.get('supervertex?', False):
         sv1_loss_delta = sv1.loss() - sv1.loss_change(sv2)
       if sv2.get('supervertex?', False):
         sv2_loss_delta = sv2.loss() - sv2.loss_change(sv1)

       sv1_potential = None
       sv2_potential = None
       if not sv1.get('supervertex?', False) and not sv2.get('supervertex?', False):
           sv1_potential = SuperVertex(sv1['track_id'], 
                                       self._edges_from_similars(sv1),
                                       sv1['tags'])

           sv2_potential = SuperVertex(sv2['track_id'],
                                       self._edges_from_similars(sv2),
                                       sv2['tags'])

           sv1_loss_delta = sv1_potential.loss_change(sv2_potential)
           sv2_loss_delta = sv2_potential.loss_change(sv1_potential)

        # TODO: Ogarnij jakis threshold filip?
        if sv1_loss_delta < sv2_loss_delta:
            if sv1_potential:
                self.membership_lookup[sv1['track_id']] = sv1_potential
                sv1 = sv1_potential
            return sv1

        if sv2_loss_delta > sv1_loss_delta:
            if sv1_potential:
                self.membership_lookup[sv2['track_id']] = sv2_potential
                sv2 = sv2_potential
            return sv2

        return None

class SuperVertex(object):
    NEXT_SV_ID = 1

    def __init__(self, track_id, edges, tags):
        self.identity = SuperVertex.NEXT_SV_ID
        self.members = []
        self.edges = edges 
        self.tags = tags
        SuperVertex.NEXT_SV_ID += 1

    def loss(self):
        max_dist = sorted(self.edges, lambda x: x[2])[-1] 

    def loss_changed(self, v):

    def similars_from_edges(self):
        edges_list = sorted(self.edges, lambda x: x[2])
        return [[tid, similarity] for _, tid, similarity in edges_list]

    def append(self, new_member):
    
    def __getitem__(self, key, val):
        if key in ['tags', 'similars', 'supervertex?']:
            return { 'tags': self.tags.items(),
                     'similars': self.similars_from_edges(),
                     'supervertex?': True }[key]
        else
            raise KeyError

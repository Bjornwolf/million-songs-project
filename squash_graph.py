from super_vertex import SuperVertex

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


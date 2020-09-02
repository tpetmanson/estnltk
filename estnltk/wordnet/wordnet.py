import sqlite3
import os.path
import math
import networkx as nx
from typing import Union
from estnltk.wordnet.synset import Synset

MAX_TAXONOMY_DEPTHS = {'a': 2, 'n': 13, 'r': 0, 'v': 10}


class WordnetException(Exception):
    pass


class WordnetIterator:
    def __init__(self, wordnet):
        self._wordnet = wordnet
        self._index = 1

    def __next__(self):
        if self._index < len(self._wordnet._synsets_dict):
            result = self._wordnet._synsets_dict[self._index]
            self._index += 1
            return result
        raise StopIteration


class Wordnet:
    '''
    Wordnet class which implements sqlite database connection.
    Attributes
    ----------
    version: str
        Version of Wordnet to use. Currently only version 2.3.2 (default) is supported
    _graph: Networkx.MultiDiGraph
        Graph where nodes are synset ids and edges are relations between nodes.
    '''

    def __init__(self, version: str ='2.3.2', load_graph: bool = False) -> None:
        self.conn = None
        self.cur = None
        self.version = version
        self._synsets_dict = dict()
        self._graph = None

        wn_dir = '{}/data/estwn-et-{}'.format(os.path.dirname(os.path.abspath(__file__)), self.version)
        wn_entry = '{}/wordnet_entry.db'.format(wn_dir)
        wn_relation = '{}/wordnet_relation.db'.format(wn_dir)
        wn_example = '{}/wordnet_example.db'.format(wn_dir)
        wn_definition = '{}/wordnet_definition.db'.format(wn_dir)

        if not os.path.exists(wn_dir):
            raise WordnetException("Invalid wordnet version: missing directory: {}".format(wn_dir))
        if not os.path.exists(wn_entry):
            raise WordnetException("Invalid wordnet version: missing file: {}".format(wn_entry))
        if not os.path.exists(wn_relation):
            raise WordnetException("Invalid wordnet version: missing file: {}".format(wn_relation))

        try:
            self.conn = sqlite3.connect(wn_entry)
            self.cur = self.conn.cursor()
            self.conn.execute("ATTACH DATABASE ? AS wordnet_relation", (wn_relation,))
            self.conn.execute("ATTACH DATABASE ? AS wordnet_example", (wn_example,))
            self.conn.execute("ATTACH DATABASE ? AS wordnet_definition", (wn_definition,))

        except sqlite3.OperationalError as e:
            raise WordnetException("Invalid wordnet file: sqlite connection error: {}".format(e))

        except Exception as e:
            raise WordnetException("Unexpected error: {}: {}".format(type(e), e))

        self.cur.execute(
            "SELECT id, synset_name, estwn_id, pos, sense, literal FROM wordnet_entry WHERE is_name = 1")
        synset_entries = self.cur.fetchall()
        for row in synset_entries:
            self._synsets_dict[row[0]] = Synset(self, row)

        if load_graph:
            self.graph

    def __iter__(self):
        return WordnetIterator(self)

    @property
    def graph(self) -> Union[None, nx.DiGraph]:
        """
        If not created already, creates Networkx graph from the database. The graph includes
        Synset id's as nodes and relations as edges between them. Otherwise returns the graph.

        Returns
        -------
        Networkx graph if it has been created beforehand, None otherwise.
        """
        if self._graph is None:
            self.cur.execute("SELECT start_vertex, end_vertex, relation FROM wordnet_relation")
            wn_relations = self.cur.fetchall()
            self._graph = nx.MultiDiGraph()
            for i, r in enumerate(wn_relations):
                self._graph.add_edge(r[0], r[1], relation=r[2])
        else:
            return self._graph

    def __del__(self) -> None:
        self.conn.close()

    def __getitem__(self, key: Union[tuple, str]) -> Union[Synset, list, None]:
        """Returns synset object or list of synset objects with the provided key.

        Parameters
        ----------
        key : string or tuple
          If key is a string, it is a lemma.
          If key is a tuple, it is either (lemma, pos) or (lemma, index)

        Returns
        -------
        Synset if second element of tuple is index.
            The synset returned is on the place of the index in the list of all synsets with provided lemma.
        List of synsets which contain lemma and pos if provided if key is string or second element of key is pos.
        None, if no match was found.
        """
        if isinstance(key, tuple) and len(key) == 2:
            if isinstance(key[1], int):
                synset_name, id = key
                self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ?", (synset_name,))
                synsets = self.cur.fetchall()
                if synsets is not None and id <= len(synsets) and id - 1 >= 0:
                    return Synset(self, synsets[id - 1][0])
            else:
                synset_name, pos = key
                self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ? AND pos = ?", (synset_name, pos))
        else:
            self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ?", (key,))
        synsets = self.cur.fetchall()
        if synsets is not None:
            return [Synset(self, entry[0]) for entry in synsets]
        return

    def synsets_with_pos(self, pos: str):
        """Return all the synsets which have the provided pos.

        Notes
        -----
        Function returns a generator which yields synsets. They can be retrieved with a for-cycle.

        Parameters
        ----------
        pos : str
          Part-of-speech of the sought synsets.
          Possible part-of-speech tags are: 'n' for noun, 'v' for verb, 'a' for adjective and 'r' for adverb.

        Yields
        ------
        Synset objects with specified part-of-speech tag.
        """
        self.cur.execute(
            "SELECT id, synset_name, estwn_id, pos, sense, literal FROM wordnet_entry WHERE pos = ? AND is_name = 1",
            (pos,))
        synset_entries = self.cur.fetchall()

        for row in synset_entries:
            yield Synset(self, row)

    def _shortest_path_distance(self, start_synset: Synset, target_synset: Synset) -> int:
        """Finds minimum path length from the target synset.

        Notes
        -----
          Internal method. Do not call directly.

        Parameters
        ----------
          target_synset : Synset
        Synset from where the shortest path length is calculated.

        Returns
        -------
          int
        Shortest path distance from `target_synset`. Distance to the synset itself is 0, -1 if no path exists between the two synsets,
        >0 otherwise.

        """

        if self._graph is None:
            self.graph

        if "distances" not in start_synset.__dict__:
            start_synset.__dict__["distances"] = {}

        if "distances" not in target_synset.__dict__:
            target_synset.__dict__["distances"] = {}

        if target_synset in start_synset.__dict__["distances"]:
            return start_synset.__dict__["distances"][target_synset]

        graph = self._graph
        distance = 0
        visited = set()
        neighbor_synsets = set([start_synset.id])

        while len(neighbor_synsets) > 0:
            neighbor_synsets_next_level = set()

            for synset in neighbor_synsets:
                if synset in visited:
                    continue

                if synset == target_synset.id:
                    return distance
                relations = list(graph.in_edges(synset, data=True))
                hypernyms = [r[0] for r in relations if r[2]['relation'] == 'hypernym']
                hyponyms = [r[0] for r in relations if r[2]['relation'] == 'hyponym']
                neighbor_synsets_next_level |= set(hypernyms)
                neighbor_synsets_next_level |= set(hyponyms)
                visited.add(synset)
            distance += 1
            neighbor_synsets = set(neighbor_synsets_next_level)

        return -1

    def _min_depth(self, synset):
        """Finds minimum path length from the root.
        Notes
        -----
          Internal method. Do not call directly.

        Returns
        -------
          int
        Minimum path length from the root.
        """

        if self._graph is None:
            self.graph

        if type(synset) is not int:     # vt üle see (ehk et vb muuda et synset oleks hoopis synset id)
            synset = synset.id

        min_depth = 0
        relations = self.graph.in_edges(synset, data=True)
        hypernyms = [r[0] for r in relations if r[2]['relation'] == 'hypernym']
        if hypernyms:
            min_depth = 1 + min(self._min_depth(h) for h in hypernyms)

        return min_depth

    def _recursive_hypernyms(self, synset, hypernyms):
        """Finds all the hypernyms of the synset transitively.
        Notes
        -----
          Internal method. Do not call directly.
        Parameters
        ----------
          hypernyms : set of Synsets
        An set of hypernyms met so far.
        Returns
        -------
          set of Synsets
        Returns the input set.
        """

        hypernyms |= set(synset.hypernyms)

        for s in synset.hypernyms:
            hypernyms |= self._recursive_hypernyms(s, hypernyms)
        return hypernyms

    def lowest_common_hypernyms(self, start_synset: Synset, target_synset: Synset) -> Union[list, None]:
        """Returns the common hypernyms of the synset and the target synset, which are furthest from the closest roots.

        Parameters
        ----------
          start_synset  : Synset
          target_synset : Synset
        Synset with which the common hypernyms are sought.

        Returns
        -------
          list of Synsets
        Common synsets which are the furthest from the closest roots.

        """
        self_hypernyms = self._recursive_hypernyms(start_synset, set())
        other_hypernyms = self._recursive_hypernyms(target_synset, set())
        common_hypernyms = self_hypernyms.intersection(other_hypernyms)

        annot_common_hypernyms = [(hypernym, self._min_depth(hypernym)) for hypernym in common_hypernyms]

        annot_common_hypernyms.sort(key=lambda annot_hypernym: annot_hypernym[1], reverse=True)

        max_depth = annot_common_hypernyms[0][1] if len(annot_common_hypernyms) > 0 else None

        if max_depth != None:
            return [annot_common_hypernym[0] for annot_common_hypernym in annot_common_hypernyms if
                    annot_common_hypernym[1] == max_depth]
        return None

    def path_similarity(self, start_synset: Synset, target_synset: Synset) -> Union[float, None]:
        """Calculates path similarity between the two synsets.

        Parameters
        ----------
          target_synset : Synset
        Synset from which the distance is calculated.

        Returns
        -------
          float
        Path similarity from `target_synset`. Similarity with the synset itself is 1,
        similarity with ureachable synset is None, 1/(shortest_path_distance + 1) otherwise.

        """

        """if self._graph is None:
            self.graph

        try:
            distance = nx.shortest_path_length(self.graph, start_synset.id, target_synset.id)
            return 1.0 / (distance + 1)
        except:
            return None"""
        distance = self._shortest_path_distance(start_synset, target_synset)
        if distance >= 0:
            return 1.0 / (distance + 1)
        return None

    def lch_similarity(self, start_synset: Synset, target_synset: Synset) -> Union[float, None]:
        """Calculates Leacock and Chodorow's similarity between the two synsets.
        Notes
        -----
          Similarity is calculated using the formula -log( (dist(synset1,synset2)+1) / (2*maximum taxonomy depth) ).
        Parameters
        ----------
          target_synset : Synset
        Synset from which the similarity is calculated.
        Returns
        -------
          float
        Leacock and Chodorow's from `synset`.
        None, if synsets are not connected via hypernymy/hyponymy relations. Obvious, if part-of-speeches don't match.

        """

        """if self._graph is None:
            self.graph

        if start_synset.pos != target_synset.pos:
            return None

        depth = MAX_TAXONOMY_DEPTHS[start_synset.pos]

        try:
            distance = nx.shortest_path_length(self.graph, start_synset.id, target_synset.id)
            return -math.log((distance + 1) / (2.0 * depth))
        except:
            return None"""

        if start_synset.pos != target_synset.pos:
            return None

        depth = MAX_TAXONOMY_DEPTHS[start_synset.pos]

        distance = self._shortest_path_distance(start_synset, target_synset)

        if distance >= 0:
            return -math.log((distance + 1) / (2.0 * depth))
        return None

    def wup_similarity(self, start_synset: Synset, target_synset: Synset) -> Union[float, None]:
        """Calculates Wu and Palmer's similarity between the two synsets.

        Notes
        -----
          Similarity is calculated using the formula ( 2*depth(least_common_subsumer(synset1,synset2)) ) / ( depth(synset1) + depth(synset2) )

        Parameters
        ----------
          target_synset : Synset
        Synset from which the similarity is calculated.

        Returns
        -------
          float
        Wu and Palmer's similarity from `synset`.

        """

        lchs = self.lowest_common_hypernyms(start_synset, target_synset)
        lcs_depth = self._min_depth(lchs[0]) if lchs and len(lchs) else None
        self_depth = self._min_depth(start_synset)
        other_depth = self._min_depth(target_synset)
        if lcs_depth is None or self_depth is None or other_depth is None:
            return None

        return (2.0 * lcs_depth) / (self_depth + other_depth)

    def __str__(self):
        return "Wordnet version {}".format(self.version)

    def __repr__(self):
        return "Wordnet version {}".format(self.version)

    def _html_repr(self):
        return "Wordnet version {}".format(self.version)

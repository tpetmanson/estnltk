from typing import Sequence, Union
from collections import defaultdict
import regex as re
import networkx as nx

_search_parenthesis = re.compile('\(|\)').search


def contains_parenthesis(s):
    return _search_parenthesis(s) is not None

_match_SEQ_pattern = re.compile('(SEQ|REP)\((.*)\)$').match


class Grammar:
    _internal_attributes = frozenset({'name', 'text', 'start', 'end', '_terminals_', '_support_', '_priority_', '_group_'})

    def __init__(self, *,
                 start_symbols: Sequence,
                 rules: list=None,
                 depth_limit: int=float('inf'),
                 width_limit: int=float('inf'),
                 legal_attributes=None):
        if legal_attributes is None:
            self.legal_attributes = frozenset()
        else:
            legal_attributes = frozenset(legal_attributes)
            assert not legal_attributes & self._internal_attributes, 'legal attributes contain internal attributes'
            self.legal_attributes = legal_attributes
        if rules is None:
            self._rules = []
        else:
            self._rules = rules
        self.start_symbols = start_symbols
        self.depth_limit = depth_limit
        self.width_limit = width_limit

        self._setup = False
        self._setup_grammar()

    @property
    def rules(self):
        self._setup_grammar()
        return self._rules

    @property
    def rule_map(self):
        self._setup_grammar()
        return self._rule_map

    @property
    def hidden_rule_map(self):
        self._setup_grammar()
        return self._hidden_rule_map

    def has_finite_max_depth(self):
        """
        grammar is finite if there is a finite number of rules that can be applied before getting all terminals
        when applied standard rules introduce a tree
        A -> REP(B)

        Returns False if there is a cycle in the rules,
        that is the case when there are rules e.g. A -> B, B -> C, C -> A,
        but the rule A -> A A alone does not form a cycle in this sense.
        Returns True otherwise.
        """
        rule_graph = nx.DiGraph()
        for rule in self._rules:
            for r in rule.rhs:
                rule_graph.add_edge(rule.lhs, r)
        return nx.is_directed_acyclic_graph(rule_graph)

    def _terminals_and_nonterminals(self):
        self.nonterminals = frozenset(r['lhs'] for r in self._rules)
        terminals = set()
        for i in (set(i.rhs) for i in self._rules):
            terminals.update(i)
        self.terminals = frozenset(terminals - self.nonterminals)

    def _rule_maps(self):
        self._rule_map = defaultdict(list)
        plus_symbols = set()
        for rule in self._rules:
            for pos, rhs in enumerate(rule.rhs):
                self._rule_map[rhs].append((rule, pos))
                m = _match_SEQ_pattern(rhs)
                if m is not None:
                    plus_symbols.add((rhs, m.group(2)))

        self._hidden_rule_map = {}
        for ps, s in plus_symbols:
            self._hidden_rule_map[ps] = [(Rule(ps, (ps, ps)), 0),
                                         (Rule(ps, (ps, ps)), 1)]
            self._hidden_rule_map[s] = [(Rule(ps, s), 0)]

    def _setup_grammar(self):
        if self._setup:
            return
        assert len(self._rules) == len({(r.lhs, r.rhs) for r in self._rules}), 'repetitive rules'
        assert (self.depth_limit < float('inf') or
                self.width_limit < float('inf') or
                self.has_finite_max_depth()), 'infinite grammar without depth or width limit'
        self._terminals_and_nonterminals()
        self._rule_maps()
        self._setup = True

    def add(self, rule):
        self._rules.append(rule)
        self._setup = False

    def __getitem__(self, key):
        if key in self.nonterminals:
            return [i for i in self.rules if i.lhs == key]
        else:
            return self.rules[key]

    def __str__(self):
        self._setup_grammar()
        rules = '\n\t'.join([str(i) for i in self.rules])
        terminals = ', '.join(sorted(self.terminals))
        nonterminals = ', '.join(sorted(self.nonterminals))
        return '''
Grammar:
\tstart: {start}
\tterminals: {terminals}
\tnonterminals: {nonterminals}
\tlegal attributes: {self.legal_attributes}
\tdepth_limit: {self.depth_limit}
\twidth_limit: {self.width_limit}
Rules:
\t{rules}
'''.format(start=', '.join(self.start_symbols), rules=rules, terminals=terminals,
           nonterminals=nonterminals, self=self)

    def __repr__(self):
        return str(self)


class Rule:
    @staticmethod
    def default_validator(x):
        return True

    @staticmethod
    def default_decorator(x):
        return {}

    def __init__(self, lhs: str, rhs: Union[str, Sequence[str]], priority: int=0, group=None, decorator=None, validator=None):
        assert not contains_parenthesis(lhs) or _match_SEQ_pattern(lhs), 'parenthesis not allowed: ' + lhs
        self.lhs = lhs
        if isinstance(rhs, str):
            rhs = rhs.split()
        for r in rhs:
            assert isinstance(r, str), 'rhs must be a str or sequence of str'
            if contains_parenthesis(r):
                assert _match_SEQ_pattern(r) is not None, 'parenthesis only allowed with SEQ or REP: ' + rhs
        self.rhs = tuple(rhs)

        self.priority = priority
        self.group = group
        if group is None:
            self.group = hash((self.lhs, self.rhs))

        if decorator:
            self.decorator = decorator
        else:
            self.decorator = self.default_decorator

        if validator:
            self.validator = validator
        else:
            self.validator = self.default_validator

    def __lt__(self, other):
        return self.priority < other.priority

    def __getitem__(self, key):
        if key == 'lhs':
            return self.lhs
        elif key == 'rhs':
            return self.rhs
        else:
            raise AssertionError

    def __str__(self):
        return '{self.lhs} -> {rhs}\t: {self.priority}, val: {self.validator.__name__}, dec: {self.decorator.__name__}'.format(self=self, rhs=' '.join(self.rhs))

    def __repr__(self):
        return str(self)

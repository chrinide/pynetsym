import argparse
import random
import networkx as nx
import itertools as it
from .. import core

__author__ = 'enrico'

def make_parser(parent):
    parser = argparse.ArgumentParser(parents=[parent,])
    parser.add_argument('-n', '--network-size', default=100, type=int)
    parser.add_argument('--death-probability', default=0.01, type=float)
    return parser


def make_setup(network_size, death_probability):
    def setup(network_manager):
        generation_seed = it.izip(
            it.repeat(Node),
            xrange(network_size),
            it.repeat(dict(death_probability=death_probability)))
        for cls, identifier, node_params in generation_seed:
            network_manager.create_node(cls, identifier, node_params)

    return setup


class Node(core.Node):
    def __init__(self, identifier, address_book, graph, death_probability):
        self.death_probability = death_probability
        super(Node, self).__init__(identifier, address_book, graph)

    def activate(self):
        graph = self.graph
        neighbors = nx.neighbors(graph, self.id)

        possible_links = [link for link in it.combinations(neighbors, 2)
                                if not graph.has_edge(*link)]
        if possible_links:
            node_a, node_b = random.choice(possible_links)
            self.send(node_a, make_introduce(node_b))
        else:
            core.introduce_self_to_popular(self)

#        n = graph.number_of_nodes()
#        m = graph.number_of_edges()
#        print m, float(m)/(n*n), len(possible_links)


def make_introduce(target_node):
    def introduce(node):
        graph = node.graph
        if graph.has_edge(node.id, target_node):
            return introduction_failed
        else:
            node.send(target_node, core.make_accept_link(node.id))

    return introduce


def introduction_failed(node):
    core.introduce_self_to_popular(node)
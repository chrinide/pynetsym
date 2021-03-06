'''
Created on Jun 5, 2012

@author: enrico
'''

from pynetsym import configurators
from pynetsym import core
from pynetsym import simulation
import pytest

import networkx as nx
from pynetsym.nodes import Node


class Node(Node):
    def activate(self):
        pass


class Simulation(simulation.Simulation):
    class configurator_type(configurators.NXGraphConfigurator):
        node_type = Node
        node_options = {}


def run_simulation(graph):
    sim = Simulation()
    sim.run(starting_graph=graph)
    return sim.handle


GRAPHS = [
    nx.erdos_renyi_graph(1000, 0.1),
#    nx.erdos_renyi_graph(1000, 0.1, directed=True),
#    nx.erdos_renyi_graph(1000, 0.5),
#    nx.erdos_renyi_graph(1000, 0.5, directed=True),
#    nx.erdos_renyi_graph(1000, 0.9),
#    nx.erdos_renyi_graph(1000, 0.9, directed=True),
#    nx.barabasi_albert_graph(1000, 8),
#    nx.barabasi_albert_graph(10000, 20),
#    nx.watts_strogatz_graph(1000, 4, 0.1)
]


@pytest.mark.parametrize(("original_graph", "recreated_graph"),
    [(graph, run_simulation(graph)) for graph in GRAPHS])
def test_same_graph(original_graph, recreated_graph):
    assert isinstance(original_graph, nx.Graph)
    assert isinstance(recreated_graph, type(original_graph))
    assert original_graph.number_of_nodes(), recreated_graph.number_of_nodes()
    assert original_graph.number_of_edges(), recreated_graph.number_of_edges()

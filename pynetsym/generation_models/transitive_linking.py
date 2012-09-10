from traits.trait_types import Float, Function

import random

from pynetsym import Node, Activator, Simulation, BasicConfigurator


class Node(Node):
    MAX_TRIALS = 10

    death_probability = Float
    criterion = Function

    def can_be_collected(self):
        return False

    def introduction(self):
        graph = self.graph.handle
        neighbors = graph.neighbors(self.id)
        if len(neighbors) > 1:
            for _ in xrange(Node.MAX_TRIALS):
                node_a, node_b = random.sample(neighbors, 2)
                if not graph.has_edge(node_a, node_b):
                    self.send(node_a, 'introduce_to', target_node=node_b)
                    break
            else:
                self.link_to(self.criterion)
        else:
            self.link_to(self.criterion)

    def activate(self):
        if random.random() < self.death_probability:
            self.regenerate()
        else:
            self.introduction()
        return id

    def introduce_to(self, target_node):
        self.send(target_node, 'accept_link', originating_node=self.id)

    def regenerate(self):
        target_node = self.graph.random_node()
        self.link_to(target_node)


class TL(Simulation):
    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const=lambda graph: graph.preferential_attachment_node(),
            default=lambda graph: graph.random_node())))

    class configurator_type(BasicConfigurator):
        node_cls = Node
        node_options = {"death_probability", "criterion"}

if __name__ == '__main__':
    sim = TL()
    sim.run()

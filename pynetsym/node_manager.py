from gevent.pool import Group
from traits.trait_types import   Instance

from pynetsym import core

from pynetsym.identifiers_manager import IntIdentifierStore

class NodeManager(core.Agent):
    """
    The class responsible to create nodes.

    """
    name = 'manager'
    """
    the registered name in the L{address book<AddressBook>}
    """

    def __init__(self, graph, mongo_client):
        """
        Creates a new node_manager

        @param graph: the graph to pass to the agents
        @type graph: storage.GraphWrapper
        """
        self.graph = graph
        self.mongo_client = mongo_client
        self.failures = []
        self.group = Group()

    def setup_node(self, node, greenlet):
        greenlet.link_value(node.deactivate_node)
        node.graph = self.graph
        node.mongo_client = self.mongo_client
        self.group.add(greenlet)
        if hasattr(node, 'setup_mongo'):
            node.setup_mongo()

    def unset_node(self, node, greenlet):
        del node.graph
        del node.mongo_client
        self.group.discard(greenlet)

        if isinstance(greenlet.value, core.GreenletExit):
            self.graph.remove_node(node.id)
            print 'Removing', node.id

    def create_node(self, cls, parameters, time=None):
        """
        Creates a new node.

        @param cls: the factory creating the new node.
            Usually the node class.
        @type cls: callable
        @param parameters: the parameters that are forwarded to the node for
            creation
        @type parameters: dict
        @return: the actual identifier
        @rtype: int | str
        """
        node = cls(**parameters)
        identifier = self.graph.add_node()
        node.start(self._address_book, self._node_db, identifier)
        return identifier

    def simulation_ended(self, time):
        self.group.join()



import traits.api as t

import pynetsym.core as core
from pynetsym import graph
from pynetsym.node_manager import NodeManager

__all__ = [
    'Node'
]


class Node(core.Agent):
    """
    A Node in the social network.
    """

    graph = t.Trait(graph.IGraph, transient=True, allow_none=False)
    _node_manager = t.Trait(NodeManager, transient=True, allow_none=False)

    #_ = t.Disallow()

    def __init__(self, **attributes):
        """
        Create a Node in the network.
        :param graph: the graph backing the social network
        :type graph: storage.GraphWrapper
        :return: the Node
        """
        self.set(**attributes)

    def deactivate_node(self, greenlet):
        self._node_manager.unset_node(self, greenlet)

    def start(self, address_book, agent_db, identifier=None):
        super(Node, self).start(address_book, agent_db, identifier)
        self._node_manager =  self._resolve(NodeManager.name)
        self._node_manager.setup_node(self, self._greenlet)
        return self

    def __str__(self):
        return 'Node-%s' % (self.id, )

    def link_to(self, criterion_or_node):
        """
        Sends an 'accept_link' message to the specified node.

        :param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        :type criterion_or_node:
            id | callable(Graph -> Node)
        :return: an asynchronous value representing whether the
            connection succeeded or not.
        """
        if callable(criterion_or_node):
            target_node = criterion_or_node(self.graph)
        else:
            target_node = criterion_or_node
        return self.send(target_node, 'accept_link',
                         originating_node=self.id)

    def unlink_from(self, criterion_or_node):
        """
        Sends a 'drop_link' message to the specified node.

        :param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        :type criterion_or_node:
            id | callable(Graph -> Node)
        """
        if callable(criterion_or_node):
            target_node = criterion_or_node(self.graph.handle)
        else:
            target_node = criterion_or_node
        self.send(target_node, 'drop_link',
                  originating_node=self.id)

    def accept_link(self, originating_node):
        """
        Accepts an 'accept_link' message (modifying the network).

        :param originating_node: the node that required the connection
        :type originating_node: int
        """
        self.graph.add_edge(originating_node, self.id)
        return True

    def drop_link(self, originating_node):
        """
        Accepts a 'drop_link' message (modifying the network).

        :param originating_node: the node that required the drop
        :type originating_node: int
        """
        self.graph.remove_edge(originating_node, self.id)
        return True

    def neighbors(self):
        """
        Return an iterable with the neighbors.
        """
        return self.graph.neighbors(self.id)

    def can_be_collected(self):
        """
        Return whether this agent can be collected.

        .. warning::
            Defaults to true, do not override unless you know what
            you are doing.
        """
        return True

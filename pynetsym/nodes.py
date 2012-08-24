import traits.api as t

import pynetsym.core as core
import pynetsym.storage as storage

from pynetsym.node_manager import NodeManager

__author__ = 'enrico'

class Node(core.Agent):
    """
    A Node in the social network.
    """

    graph = t.Trait(storage.GraphWrapper, transient=True)
    _node_manager = t.Trait(NodeManager, transient=True)

    #_ = t.Disallow()

    def __init__(self, identifier, address_book, graph):
        """
        Create a Node in the network.
        @param identifier: the identifier to bind the Node to
        @type identifier: int|str
        @param address_book: the address book where we want to register
        @type address_book: AddressBook
        @param graph: the graph backing the social network
        @type graph: storage.GraphWrapper
        @return: the Node
        """
        super(Node, self).__init__(identifier, address_book)
        self.graph = graph

    def _link_to_node_manager(self):
        self._node_manager = self._address_book.resolve(NodeManager.name)
        self.link_value(self._node_manager.node_terminated_hook)
        self.link_exception(self._node_manager.node_failed_hook)

    def establish_agent(self, address_book):
        super(Node, self).establish_agent(address_book)
        self._link_to_node_manager()

    def free_agent(self):
        super(Node, self).free_agent()
        self.unlink(self._node_manager._greenlet)

    def __str__(self):
        return 'Node-%s' % (self.id, )

    def link_to(self, criterion_or_node):
        """
        Sends an 'accept_link' message to the specified node.

        @param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        @type criterion_or_node:
            id | callable(L{graph<graph.Graph>}) -> L{Node<Node>}
        @return: an asyncronous value representing whether the
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

        @param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        @type criterion_or_node:
            id | callable(L{graph<graph.Graph>}) -> L{Node<Node>}
        @return: None
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

        @param originating_node: the node that required the connection
        @type originating_node: int
        """
        self.graph.add_edge(originating_node, self.id)
        return True

    def drop_link(self, originating_node):
        """
        Accepts a 'drop_link' message (modifying the network).

        @param originating_node: the node that required the drop
        @type originating_node: int
        """
        self.graph.remove_edge(originating_node, self.id)
        return True

    def can_be_collected(self):
        """
        Override this if the Agent should not be collected
        """
        return True

    def run_loop(self):
        while 1:
            try:
                message, result = self.read(timeout=0.01)
                self.process(message, result)
                del message, result
                self.cooperate()
            except core.NoMessage:
                if self.can_be_collected():
                    return self
        return self
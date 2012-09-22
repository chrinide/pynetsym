from traits.api import Interface, Enum


class IGraph(Interface):
    def add_node(self):
        """
        Add a node to the graph.
        @return The index of the newly created node.
        @rtype int
        """

    def add_edge(self, source, target):
        """
        Add edge to the graph

        @param source: the node from where the edge starts
        @type source: int
        @param target: the node to which the edge arrives
        @type target: int
        @warning: the actual behavior depends on the implementation being
            directed or undirected
        """

    def remove_edge(self, source, target):
        """
        Removes edge from the graph

        @param source: the node from where the edge starts
        @type source: int
        @param target: the node to which the edge arrives
        @type target: int
        @warning: the actual behavior depends on the implementation being
            directed or undirected
        """
        pass

    def __contains__(self, identifier):
        """
        True if the graph contains the specified identifier.
        @param identifier: the identifier to seek
        @type identifier: int
        @return: True if identifier is in graph
        @rtype: bool
        """
        pass

    def has_node(self, identifier):
        """
        True if the graph contains the specified identifier.
        @param identifier: the identifier to seek
        @type identifier: int
        @return: True if identifier is in graph
        @rtype: bool
        @raise ValueError: if identifier is not convertible to a non negative integer.
        """
        pass

    def has_edge(self, source, target):
        """
        True if the graph contains the specified identifier.
        @param source: the node from where the edge starts
        @type source: int
        @param target: the node to which the edge arrives
        @type target: int
        @return: True if edge is in graph
        @rtype: bool
        @raise ValueError: if identifier is not convertible to a non negative integer.
        """
        pass

    def neighbors(self, identifier):
        """
        Return the neighbors of the specified node.
        """
        pass

    def successors(self, identifier):
        """
        Return the ...
        @param identifier:
        @return:
        """

    def number_of_nodes(self):
        """
        Return the number of nodes in the network.

        @return: The number of edges in the network
        @rtype: int
        @warning: the default implementation is not efficient, as it calls self.nodes()
        """
        return len(self.nodes())

    def number_of_edges(self):
        """
        Return the number of edges in the network.
        @return: The number of edges in the network.
        @rtype: int
        """

    def is_directed(self):
        """
        Return true if the graph is directed.
        @return: True if the graph is directed, False otherwise.
        @rtype: bool
        """

    def to_nx(self, copy=False):
        """
        Return corresponding NetworkX graph.
        @param copy: whether the graph should be copied.
        @type copy: bool
        @return: A networkx graph.
        @rtype: networkx.Graph

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to servere malfunctions, unless the simulation has already
          stopped.
        """

    def to_scipy(self, copy=False, sparse_type=None, minimize=False):
        """
        Return corresponding NetworkX graph.
        @param copy: whether the graph should be copied.
        @type copy: bool
        @param sparse_type: the kind of sparse matrix that is returned
        @param minimize: whether we want the returned sparse matrix to be
          reshaped so that it contains only the minimum possible number
          of nodes
        @return: A scipy sparse matrix.
        @rtype: scipy.sparse.spmatrix

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to servere malfunctions, unless the simulation has already
          stopped.

          In general, if the type of sparse matrix requested is different from
          the underlying representation or if a minimization is requested, a copy
          is made.
        """

    def to_numpy(self, copy=False, minimize=True):
        """
        Return corresponding NetworkX graph.
        @param copy: whether the graph should be copied.
        @type copy: bool
        @param minimize: determines if the returned matrix is as small
          as possible considering the nodes.
        @return: A numpy dense matrix.
        @rtype: numpy.ndarray

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to servere malfunctions, unless the simulation has already
          stopped.
        """

    def copy_into(self, matrix):
        """
        Copies the adjacency matrix inside the argument, if big enough.
        Otherwise a ValueError exception is thrown.
        @param matrix: the matrix where data is copied
            Typically it should be something that acts like a numpy array.
        """
        pass

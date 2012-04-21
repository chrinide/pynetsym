import abc
import sys
import collections
import numbers
import decorator

import gevent

import gevent.queue as queue
import gevent.event as event

from pynetsym import util

_M = collections.namedtuple('Message', 'sender payload parameters')

Priority = util.enum(
        URGENT=2**2, HIGH=2**8, NORMAL=2**16, ANSWER=2**15,
        LOW=2**24, LAST_BUT_NOT_LEAST=sys.maxint)

class Message(_M):
    """
    An immutable object that is used to send a message among agents.
    """


class AddressingError(Exception):
    """
    Error signaling that something with the addressing of
    a message went wrong.

    """

    def __init__(self, *args, **kwargs):
        super(AddressingError, self).__init__(*args, **kwargs)


class AddressBook(object):
    """
    The Address book holds information on every agent in the system.

    An agent that is not in the AddressBook is virtually unreachable.

    @todo: Change the API so that the identifier is not chosen from outside.
        The API change should take into account:
            1. how it works with different Graph implementations
                (e.g., igraph)
            2. how it works with different back-ends (e.g., asside)
    """

    def __init__(self, graph):
        self.name_registry = {}
        self.graph = graph

    def register(self, identifier, agent):
        """
        Binds the identifier with the agent

        @param identifier: the identifier to bind the agent to
        @type identifier: int | str
        @param agent: the agent to bind
        @type agent: Agent
        @raise AddressingError: if identifier is numeric and bound
        @raise TypeError: if the identifier is not a string or a integer
        """
        if isinstance(identifier, basestring):
            if (identifier in self.name_registry
                    and self.name_registry[identifier] is not agent):
                raise AddressingError(
                    "Could not rebind agent %r to identifier %r." % (
                        agent, identifier))
            else:
                self.name_registry[identifier] = agent
        elif isinstance(identifier, numbers.Integral):
            if identifier in self.graph:
                raise AddressingError(
                    ("Could not rebind agent "
                        "%r to identifier %r.") % (agent, identifier))
            else:
                self.graph.add_node(identifier, agent)
        else:
            raise TypeError("Identifiers must be strings or integers")

    def resolve(self, identifier):
        """
        Resolves :param: identifier to the actual agent.

        @raise AddressingError: if the agent is not registered.
        """
        if isinstance(identifier, basestring):
            try:
                return self.name_registry[identifier]
            except KeyError:
                raise AddressingError(
                    "Could not find node with address %r." % identifier)
        elif isinstance(identifier, numbers.Integral):
            try:
                return self.graph[identifier]
            except RuntimeError as e:
                raise AddressingError(e.message)

def answers(message, priority=Priority.ANSWER, **kw):
    """
    Use this decorator to specify the message that shall be answered.

    @parameter message: the name of the message

    Additionally we can specify paramters that map attributes of the
    current node to additional parameters that must be passed to the
    message::

        @answers('foo', node_id='id')
        def bar(self, ...)
            pass

    means that after bar is called, it shall answer a message back
    with a parameter node_id that is the id attribute of the current
    agent.

    """
    def answers(f, self, *args, **kwargs):
        answer = f(self, *args, **kwargs)
        if answer is None:
            additional_parameters = {k: getattr(self, v, v)
                    for k, v in kw.iteritems()}
            additional_parameters.setdefault('priority', priority)
            return message, additional_parameters
        else:
            return answer
    return decorator.decorator(answers)

class Agent(gevent.Greenlet):
    """
    An Agent is the basic class of the simulation. Agents communicate
    asynchronously with themselves.
    """

    __metaclass__ = abc.ABCMeta

    IGNORE = 0
    LOG_ERROR = 1
    EXCEPTION = 2

    def __init__(self, identifier, address_book, error_level=LOG_ERROR):
        """
        Initializes the Agent object setting variables and registering
        the agent in the address book.

        @param identifier: the identifier the agent has in the system
        @type identifier: int|str
        @param address_book: the address book where we want to register
        @type address_book: AddressBook
        @param error_level: describe what should happen when a message
            cannot be delivered
        @type error_level: int (IGNORE|LOG_ERROR|EXCEPTION)
        @return: the Agent
        """
        super(Agent, self).__init__()
        self._id = identifier
        self._address_book = address_book
        self._err_level = error_level
        self._address_book.register(identifier, self)
        self._default_queue = queue.PriorityQueue()
        self._queue = self._default_queue

    def deliver(self, message, priority, result):
        """
        Delivers message to this agent.
        @param message: the message
        @type message: Message
        @param result: dataflow-like object we use to feed-back answers
        @type result: event.AsyncResult
        """
        self._default_queue.put((priority, message, result))

    def _sync_deliver(self, message):
        pass

    def cooperate(self):
        """
        Release control
        """
        gevent.sleep()

    def sleep(self, seconds):
        gevent.sleep(seconds)

    def _run(self):
        self.run_loop()

    def read(self):
        """
        Reads the next message that was sent to this agent.
        @attention: It is not really meant to be called directly.
        @return: priority, Message
        """
        return self._default_queue.get()

    @property
    def id(self):
        """
        The node identifier.
        @rtype: int
        @attention: In fact, the only requirement is that it is hashable
        """
        return self._id

    def send(self, receiver_id, message_name, priority=Priority.NORMAL,
            **additional_parameters):
        """
        Send a message to the specified agent.

        @param receiver_id: the id of the receiving agent
        @param message_name: the name of the receiving agent method or
            a function taking the agent as its first argument (unbound
            methods are just perfect).
        @param additional_parameters: additional parameters to be passed
            to the function
        @param priority: can be used to specify a priority
        """
        receiver = self._address_book.resolve(receiver_id)
        message = Message(self.id, message_name, additional_parameters)
        # self.log_message(message_name, receiver, priority)
        result = event.AsyncResult()
        receiver.deliver(message, priority, result)
        return result

    def build_unsupported_method_message(
            self, receiver_class, payload, additional_parameters):
        additional_parameters = dict(name=payload,
            additional_parameters=additional_parameters)
        return getattr(receiver_class, 'unsupported_message')

    def log_message(self, payload, receiver, priority):
        print 'Sending', payload, 'from', self.id, 'to', receiver.id,
        print 'with priority', priority

    def process(self, message, result):
        """
        Processes the message. This means calling the message payload with
        self as argument.

        """
        action_name = message.payload
        try:
            bound_method = getattr(self, action_name)
        except AttributeError:
            value = self.unsupported_message(action_name, **message.parameters)
        else:
            value = bound_method(**message.parameters)
        # TODO: decide how to deal with exceptions
        result.set(value)

    def run_loop(self):
        """
        Agent main run loop.

            1. read a message from the queue
            2. process the message and elaborate the answer
            3. if the answer is not None, send it to the original message
            4. release control

        The format of answer shall be either:
            1. a string indicating the message name to be send
            2. a tuple where the first element is the name of the
                message to be sent and the second element is a
                dictionary of additional parameters that will be
                passed along.


        @attention: checks regarding message_processor and similar
            are not made
        """
        while 1:
            message_priority, message, result = self.read()
            self.process(message, result)
            self.cooperate()

    def unsupported_message(self, name, additional_parameters):
        """
        Prints out something if we received a message we could not process.
        """
        print (
            ('%s received "%s" message with parameters %s: '
                'could not process.') %
            (self, name, additional_parameters))

    def __str__(self):
        return '%s(%s)' % (type(self), self.id)

class AgentIdUpdatableContext(object):
    """
    Agent ids are normally not settable because doing so could prevent
    the system from functioning correctly. However, in certain
    circumstances it makes sense to change a node identifier instead of
    destroying the old node and creating a new one.

    In this context agent ids become settable. Notice that the changes
    are *not* automatically reflected in the address book.
    """
    def __enter__(self):
        def id_setter(self, new_id):
            self._id = new_id

        self.old_property = Agent.id
        Agent.id = property(
            fget=self.old_property,
            fset=id_setter)

    def __exit__(self, *args):
        Agent.id = self.old_property

class Node(Agent):
    """
    A Node in the social network.
    """

    def __init__(self, identifier, address_book, graph):
        """
        Create a Node in the network.
        @param identifier: the identifier to bind the Node to
        @type identifier: int|str
        @param address_book: the address book where we want to register
        @type address_book: AddressBook
        @param graph: the graph backing the social network
        @type graph: networkx.Graph
        @return: the Node
        """
        super(Node, self).__init__(identifier, address_book)
        self.graph = graph

    def link_to(self, criterion_or_node, priority=Priority.NORMAL):
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
                priority=priority,
                originating_node=self.id)

    def unlink_from(self, criterion_or_node, priority=Priority.NORMAL):
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
                priority=priority,
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

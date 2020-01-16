import abc
import json
import socket
import threading
import queue
from ezcoach.exception import Disconnected
import ezcoach.json_utils as json_utils
from ezcoach.log import log


class MessageAttributes:
    """
    The class conveniently aggregating all attribute names that are used in the messages between
    the Training Module and the game engine Plugin.
    """
    TYPE = 'type'
    NAME = 'name'
    DESCRIPTION = 'description'
    PLAYERS = 'players'
    METRICS_NAMES = 'metrics_names'
    ACTIONS = 'actions'
    STATES = 'states'
    ACCUMULATED_REWARDS = 'acc_rewards'
    RUNNING = 'running'
    METRICS = 'metrics'


class OutgoingMessageTypes:
    """
    The class aggregating message types sent from the Learning Module to the game engine Plugin.
    """
    CONNECT = 'connect'
    START = 'start'
    STOP = 'stop'
    ACTION = 'action'


class IncomingMessageTypes:
    """
    The class aggregating message types sent from the Plugin to the Learning Module.
    """
    MANIFEST = 'manifest'
    STATE = 'state'
    STOPPED = 'stopped'
    DISCONNECTED = 'disconnected'


DISCONNECTED_MESSAGE_JSON = json.dumps({MessageAttributes.TYPE: IncomingMessageTypes.DISCONNECTED})


class BaseCommunication(abc.ABC):
    """
    The abstract class encapsulating communication. Messages are received on the separate thread
    and passed to the main thread using queue. Messages are sent in the main thread.
    This class relies on the provided connection to actually send and receive messages.
    Messages are encoded in JSON and can be obtained using get_messages method.
    This method clears the received messages so each message can be received only once.
    """
    def __init__(self, connection, verbose=None):
        """
        Initializes the communication with the connection (eg. TCPConnection).

        :param connection: an object sed to send and receive messages
        :param verbose: a number indicating the frequency of logged information
        """
        self._connection = connection
        self._verbose = verbose

        self._thread = None
        self._connected = False
        self._messages = queue.Queue()
        self._running = False
        self._last_partial_message = None

    def start(self):
        """
        Starts the thread responsible for receiving messages.
        The method does not start a new thread if the thread has already been started.
        """
        if self._running:
            log('Communication thread already started', 2)
            return

        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        """
        Starts the loop for checking if new messages have been received.
        Loop is performed while the _running attribute is True.
        """
        while self._running:
            self.update()

    def stop(self):
        """
        Stops the thread responsible for receiving messages.
        """
        self._running = False
        self._connection.close()

    def connect(self):
        """
        Connects to the other end of the communication.
        This may be ignored depending on the connection provided in the constructor.
        """
        self._connection.connect()
        self._connected = True

    def disconnect(self):
        """
        Disconnects the communication and stops the thread responsible for receiving messages.
        """
        self._running = False
        self._connected = False
        self._connection.close()

    def update(self):
        """
        Receives the messages from the connection instance. Requires the connection to be connected.
        Typically this method is invoked in the separate thread managed by the class but can be
        alternatively invoked manually if the start method has not been invoked.
        Messages are put to the _messages queue and can be obtained using get_messages method.
        """
        if not self._connected:
            return

        try:
            message = self._connection.recv()
        except Disconnected:
            self._report_disconnected()
            self._running = False
        else:
            self._messages.put(message)

    def send(self, message):
        """
        Sends the message using the connection. Message is a dictionary and is encoded as a json string first.
        Requires the connection to be connected.

        :param message: a string keyed dictionary representing a message to be sent
        """
        log(f'Communication sending message: {message}', self._verbose, 3)
        self._assert_connected()
        self._connection.send(json.dumps(message))

    def get_messages(self):
        """
        Obtains the messages received from the connection and put into a queue. The queue is emptied after
        this method is invoked. If a message is received only partially it will be returned only after
        it is fully received. messages are returned as a list of dictionaries.

        :return: a list of messages as a dictionaries
        """
        messages = []
        while True:
            raw_message = self._messages.get(block=True)
            try:
                message_json = json.loads(raw_message)
                messages.append(message_json)
            except json.decoder.JSONDecodeError:
                if self._last_partial_message is not None:
                    raw_message = self._last_partial_message + raw_message
                    self._last_partial_message = None

                for m in json_utils.split_jsons(raw_message):
                    try:
                        m_json = json.loads(m)
                        messages.append(m_json)
                    except json.decoder.JSONDecodeError:
                        self._last_partial_message = m

            self._messages.task_done()

            if self._messages.empty() and len(messages) > 0:
                break

        log(f'Communication receiving messages: {messages}', self._verbose, 3)
        return messages

    def _report_disconnected(self):
        """
        Informs the object that the connection was disconnected.
        """
        self._connected = False

    def _assert_connected(self):
        """
        Asserts that the connection is connected.
        """
        assert self._connected, 'Connection not established.'

    @property
    def connected(self):
        """
        Returns if the communication is connected.

        :return: bool value representing if the communication is connected
        """
        return self._connected


class Communicator(BaseCommunication):
    """
    The class representing the communication between the Training Module and the game engine Plugin.
    It must be initiated with the connection and two class methods are provided to construct this object
    with TCP and Pipe connection. TCP connection is used by default in the framework.
    The messages can be sent by the methods provided by this class.
    """

    @classmethod
    def with_tcp_connection(cls, ip: str = '127.0.0.1', port: int = 6666, buffer_size=1024, verbose=None):
        """
        Creates Communicator class with the TCP connection.

        :param ip: a string representing IP address of the game
        :param port: a port of the TCP connection as an integer
        :param buffer_size: the buffer size of the TCP connection
        :param verbose: the value indicating the frequency of the logging
        :return: Communicator class initiated with the TCP connection
        """
        tcp_connection = TCPConnection(ip, port, buffer_size, verbose)
        return cls(tcp_connection, verbose)

    @classmethod
    def with_pipe_connection(cls, connection, verbose=None):
        """
        Creates Communicator class with the pipe connection.

        :param connection: the pipe connection
        :param verbose: the value indicating the frequency of the logging
        :return: Communicator class initiated with the pipe connection
        """
        def connect(): pass
        connection.connect = connect
        return cls(connection, verbose)

    def __init__(self, connection, verbose=None):
        """
        Initializes the Communicator class with the connection.

        :param connection: the connection used by the Communicator
        :param verbose: the value indicating the frequency of the logging
        """
        super(Communicator, self).__init__(connection, verbose)

    def connect(self):
        super(Communicator, self).connect()
        connect_message = {'type': OutgoingMessageTypes.CONNECT}
        self.send(connect_message)

    def send_start(self, players, options=None):
        """
        Sends start message to the game. Options dictionary can optionally be provided to be sent
        as a part of the start message.

        :param players: a number of players that will be simultaneously interacting with the game
        :param options: an optional dictionary of options sent to the game
        """
        start_message = {'type': OutgoingMessageTypes.START,
                         'players': players,
                         'options': options}
        self.send(start_message)

    def send_stop(self):
        """
        Sends stop message to the game that will stop current episode.
        """
        start_message = {'type': OutgoingMessageTypes.STOP}
        self._connection.send(json.dumps(start_message))

    def send_actions(self, actions):
        """
        Sends actions selected by the algorithms reacting to the state of the environment to the game.

        :param actions: a list of actions selected by the agents
        """
        action_message = {'type': OutgoingMessageTypes.ACTION,
                          'actions': list(actions)}
        self.send(action_message)

    def _report_disconnected(self):
        super(Communicator, self)._report_disconnected()
        self._messages.put(DISCONNECTED_MESSAGE_JSON)


class TCPConnection:
    """
    The class representing TCP or socket connection.
    """
    def __init__(self, ip: str, port: int, buffer_size: int = 4096, verbose=None):
        """
        Initiates the TCP Connection with the IP address, port and buffer size.

        :param ip: a string representing the IP address
        :param port: a port number
        :param buffer_size: a size of the buffer
        :param verbose: the value representing the frequency of the logging
        """
        self._ip = ip
        self._port = port
        self._buffer_size = buffer_size
        self._verbose = verbose

        self._socket = None
        self._connected = False

    def connect(self):
        """
        Connects the socket using IP address and port provided in the constructor.
        """
        self._socket = socket.socket()
        self._socket.connect((self._ip, self._port))
        self._socket.setblocking(True)
        self._connected = True

    def recv(self) -> str:
        """
        Receives the string message from the socket. Waits (blocking) if not connected.
        Can throw Disconnected error.

        :return: the received message as a string
        """
        while not self._connected:
            # print(f'TCP connection, recv(), connected: {self._connected}')
            pass

        try:
            message = self._socket.recv(self._buffer_size)
            if message is None or message == b'':
                log(f'TCP Connection disconnected', self._verbose, level=1)
                self._socket = None
                self._connected = False
                raise Disconnected()

        except (ConnectionResetError, ConnectionAbortedError):
            log(f'TCP Connection disconnected', self._verbose, level=1)
            self._socket = None
            self._connected = False
            raise Disconnected()

        else:
            return message.decode('UTF-8')

    def send(self, message: str):
        """
        Sends the string message.

        :param message: a message as a string
        """
        self._socket.send(message.encode('UTF-8'))

    def close(self):
        """
        Closes the socket.
        """
        self._connected = False
        self._socket.close()

    @property
    def connected(self):
        """
        Returns if the socket is connected.

        :return: bool value indicating if the socket is connected
        """
        return self._connected


class PipeConnectionWrapper:
    """
    The class wrapping the pipe connection to be used as a connection in BaseCommunication or Communicator classes.
    """

    def __init__(self, connection):
        """
        Initializes the class with the pipe connection.

        :param connection: pipe connection
        """
        self._connection = connection
        self._connected = True

    def connect(self):
        """
        Empty method for compliance with the interface used by BaseCommunication class.
        """

    def recv(self) -> str:
        """
        Receives the message from the pipe.

        :return: a message received from the pipe
        """
        return self._connection.recv()

    def send(self, message: str):
        """
        Sends the string message through the pipe.

        :param message: a string message to be sent
        """
        self._connection.send(message)

    def close(self):
        """
        Closes the pipe.
        """
        self._connected = False
        self._connection.close()

    @property
    def connected(self):
        """
        Returns if the socket is connected.

        :return: bool value indicating if the socket is connected
        """
        return self._connected

# src/UDP-listener/UDP_sender.py
import socket

def get_local_ip() -> str:
    """
    A function to get your local IP on just about any port.
    :return: Local IP-address: 'v.x.y.z'
    :rtype: str
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        s.close()
        del s

def _check_port(port) -> bool:
    if not 0 < port <= 65535:
        raise ValueError(f"Invalid port number '{port}'")
    return True

_used_ports = set()

class UDPSocket:
    # States for debugging, checking and, potentially, statemachine.
    STATE_CLOSED = -1
    STATE_OPEN = 0
    STATE_SUCCESS = 1

    def __init__(self, address=None, port=None, encoding='ascii'):
        self._timeout = 5  # sec
        self._addr = '0.0.0.0'
        self._port = None
        self.__bound = False
        if address:
            self.address = address
        self.port = port
        self.encoding = encoding
        self._sock: socket.socket|None = None
        self.__state = self.STATE_CLOSED

    def init(self) -> None:
        print(f"Opening socket on {self.address}:{self.port}") # Debugging
        if self.socket and not self.state == self.STATE_CLOSED:
            self.close()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__state = self.STATE_OPEN

        # Either do
        self.socket.settimeout(self.timeout)
        # Or
        # self._sock.setblocking(False)

        self.socket.bind((self._addr, self.port))
        self.__bound = True

    def close(self) -> int:
        print("Closing socket") # Debugging
        self.socket.close()
        state = self.__state
        self.__state = self.STATE_CLOSED
        return state

    def sendto(self, data:str|bytes, addr:tuple[str, int]):
        print(f"Sending data '{data}' to {addr[0]}:{addr[1]}") # Debugging
        # Check the given port
        if isinstance(data, str):
            data = data.encode(self.encoding)
        # Send data
        self.socket.sendto(data, addr)
        self.__state = self.STATE_SUCCESS

    def recv(self, bufsize=1024, raise_timeout_error=True) -> tuple|None:
        print("Listening on", self._sock) # Debugging

        try:
            msg = self.socket.recvfrom(bufsize)
            print("Received data:", *msg)
        except TimeoutError as e:
            if raise_timeout_error:
                raise e
            print(f"Timed out while listening on {self.address}:{self.port}")
            msg = None
        self.__state = self.STATE_SUCCESS
        return msg

    @property
    def address(self) -> str:
        if self._addr == "0.0.0.0":
            return get_local_ip()
        return self._addr
    @address.setter
    def address(self, addr:str):
        if ':' in addr:
            addr, self.port = addr.split(":")
        if not addr.count('.') == 3 or not all(0 <= int(d) <= 255 for d in addr.split('.')):
            raise ValueError(f"IP-address must me of the format 'x.x.x.x' with 0 <= x <= 255. Got {addr}")
        self._addr = addr
    @property
    def port(self) -> int:
        return self._port
    @port.setter
    def port(self, port:int|None):
        if port is None:
            port = 50000
            while port in _used_ports:
                # Could potentially hit upper limit. But that's unlikely
                port += 1
        else:
            _check_port(port)
            if port in _used_ports:
                raise ValueError(f"Port '{port}' already in use")
        if self.port is not None:
            _used_ports.discard(port)
        self._port = port
        _used_ports.add(port)
    @property
    def bound(self):
        return self.__bound
    @property
    def state(self):
        return self.__state
    @property
    def socket(self):
        return self._sock
    @property
    def timeout(self):
        return self._timeout
    @timeout.setter
    def timeout(self, timeout):
        if self.socket:
            self.socket.settimeout(timeout)
        self._timeout = timeout

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, *_):
        return self.close() == self.STATE_SUCCESS

    def __del__(self):
        try:
            self.socket.close()
        except:
            pass
        try:
            _used_ports.discard(self.port)
        except:
            pass

if __name__ == '__main__':
    print(get_local_ip())

    with UDPSocket() as sender, UDPSocket() as receiver:
        sender.sendto("Hello", (get_local_ip(), receiver.port))
        print(receiver.recv())

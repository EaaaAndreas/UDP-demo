# src/UDP-listener/UDP_sender.py
import socket

def get_local_ip():
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
    timeout = 5 # sec
    _port = None
    __bound = False
    def __init__(self, address='0.0.0.0', port=None, encoding='ascii'):
        self.address = address
        self.port = port
        self.encoding = encoding
        self._sock: socket.socket|None = None
        self.__state = self.STATE_CLOSED

    def init(self) -> None:
        print(f"Opening socket on {self._addr}:{self._port}") # Debugging
        if self._sock:
            self.close()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__state = self.STATE_OPEN

        # Either do
        self._sock.settimeout(self.timeout)
        # Or
        # self._sock.setblocking(False)

        self._sock.bind((self._addr, self._port))
        self.__bound = True

    def close(self) -> int:
        print("Closing socket") # Debugging
        self._sock.close()
        state = self.__state
        self.__state = self.STATE_CLOSED
        return state

    def sendto(self, data:str|bytes, addr:tuple[str, int]):
        print("Sending data:", data) # Debugging
        # Check the given port
        if isinstance(data, str):
            data = data.encode(self.encoding)
        # Send data
        self._sock.sendto(data, addr)
        self.__state = self.STATE_SUCCESS

    def recv(self, bufsize=1024) -> tuple:
        print("Listening on", self._sock) # Debugging

        # Setup socket

        msg = self._sock.recvfrom(bufsize)

        self.__state = self.STATE_SUCCESS
        return msg

    @property
    def address(self) -> tuple[str, int]:
        return self._addr, self._port
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

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, *_):
        return self.close() == self.STATE_SUCCESS

    def __del__(self):
        try:
            self._sock.close()
        except:
            pass
        try:
            _used_ports.discard(self._port)
        except:
            pass

if __name__ == '__main__':
    print(get_local_ip())

    #with UDPSocket() as sender, UDPSocket() as receiver:
    #    sender.sendto("Hello", ('192.168.0.26', receiver.port))
    #    print(receiver.recv())

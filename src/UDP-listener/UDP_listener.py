# src/UDP-listener/UDP_listener.py
import socket

STATUS_CLOSED = 0
STATUS_BOUND = 1
STATUS_LISTENING = 2

_used_ports = set()

class UDPListener:
    _addr = '0.0.0.0'
    _status = STATUS_CLOSED
    def __init__(self, port:int|None=None, buff_size:int|None=None, addr:str|None=None):
        if port is None:
            port = 50000
            while port in _used_ports:
                port += 1
        self.set_port(port)
        self.set_buffsize(buff_size)
        if addr:
            self.addr = addr
        self._start_socket()

    def close(self) -> None:
        self.socket.close()
        _used_ports.remove(self.port)
        self._status = STATUS_CLOSED

    def recv(self, buff_size:int|None=None):
        return self.socket.recvfrom(buff_size | self.buffsize)

    def _start_socket(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.addr, self.port))
        self._status = STATUS_BOUND

    def set_buffsize(self, buffsize:int|None) -> None:
        """
        Set the buffer size for the bitstream. This determines how much data can be received on the socket.
        :param buffsize: The max buffersize.
        :type buffsize: int | None
        :return: None
        """
        if isinstance(buffsize, int):
            if buffsize == 0:
                buffsize = None
            elif buffsize < 0:
                raise ValueError(f"Buffer size must be greater than 0. Got '{buffsize}'")
        elif buffsize is not None:
            raise TypeError(f"Buffer must be integer or None. Got '{type(buffsize)}'")
        self._buff_size = buffsize

    def set_port(self, port:int) -> None:
        if not isinstance(port, int):
            raise TypeError(f"Port must be integer. Got '{type(port)}'")
        if port == self.port:
            return
        if not 0 < port <= 65535:
            raise ValueError(f"Port out of range. '{port}'. Port must be 0 < port <= 65535")
        if port in _used_ports:
            raise ValueError(f"Port '{port}' is already in use")
        _used_ports.remove(self.port)
        _used_ports.add(port)
        self._port = port

    def status(self) -> int:
        return self._status

    @property
    def port(self) -> int:
        return self._port
    @port.setter
    def port(self, *args) -> None:
        self.set_port(*args)
    @property
    def buffsize(self) -> int|None:
        return self._buffsize
    @buffsize.setter
    def buffsize(self, *args):
        self.set_buffsize(*args)
    @property
    def addr(self) -> str:
        return self._addr
    @addr.setter
    def addr(self, addr:str):
        if not isinstance(addr, str):
            raise TypeError(f"Address must be string. Got '{type(addr)}'")
        self._addr = addr
    @property
    def socket(self) -> socket.socket:
        return self._sock

    def __repr__(self) -> str:
        return f"<class 'UDPListener' (on '{self.addr}:{self.port}')>"

    def __del__(self) -> None:
        try:
            self.close()
        except:
            pass
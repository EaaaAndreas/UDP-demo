# src/UDP-listener/UDP_listener.py
import socket
import re
import gc
gc.collect()

STATUS_CLOSED = 0
STATUS_BOUND = 1
STATUS_LISTENING = 2

_used_ports = set()

class UDPListener:
    _addr = '0.0.0.0'
    _status = STATUS_CLOSED
    _port = None
    _callbacks = {}
    def __init__(self, port:int|None=None, buff_size:int=1024, addr:str|None=None):
        gc.collect()
        if port is None:
            port = 50000
            while port in _used_ports:
                port += 1
        self.set_port(port)
        self.buffsize = buff_size
        if addr:
            self.addr = addr
        self._start_socket()

    def close(self) -> None:
        self.socket.close()
        _used_ports.remove(self.port)
        self._status = STATUS_CLOSED

    def start_listening(self) -> tuple[bytes, str]:
        data, sender = self.recv()
        data = data.decode('ascii')
        for cmd in self._callbacks.keys():
            command = re.search(cmd + r'\s+(\S+)(?:\s|\Z)', data.lower())
            if command:
                self._callbacks[cmd](command.group(1), sender)
        return data, sender

    def recv(self, buff_size:int|None=None):
        if not self.status() == STATUS_BOUND:
            self._start_socket()
        print("Listening on port", self.port)
        if buff_size is None:
            if self.buffsize:
                buff_size = self.buffsize
            else:
                return self.socket.recvfrom(1024)
        try:
            ans = self.socket.recvfrom(buff_size)
        finally:
            self.socket.close()
            self._status = STATUS_CLOSED
        return ans

    def _start_socket(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.addr, self.port))
        self._status = STATUS_BOUND

    def set_port(self, port:int) -> None:
        if not isinstance(port, int):
            raise TypeError(f"Port must be integer. Got '{type(port)}'")
        if port == self.port:
            return
        if not 0 < port <= 65535:
            raise ValueError(f"Port out of range. '{port}'. Port must be 0 < port <= 65535")
        if port in _used_ports:
            raise ValueError(f"Port '{port}' is already in use")
        if self.port:
            _used_ports.remove(self.port)
        _used_ports.add(port)
        self._port = port

    def status(self) -> int:
        return self._status

    def add_command(self, command:str, callback:object) -> None:
        self._callbacks[command.strip().lower()] = callback

    def remove_command(self, command:str) -> None:
        command = command.strip().lower()
        if command in self._callbacks.keys():
            self._callbacks.pop(command)
        else:
            raise IndexError(f"The command '{command}' was not found.")

    @property
    def port(self) -> int:
        return self._port
    @property
    def buffsize(self) -> int|None:
        return self._buffsize
    @buffsize.setter
    def buffsize(self, buffsize:int|None):
        if buffsize is None:
            buffsize = 1024
        elif isinstance(buffsize, int):
            if buffsize < 0:
                raise ValueError(f"Buffer size must be greater than 0. Got '{buffsize}'")
        elif buffsize is not None:
            raise TypeError(f"Buffer must be integer or None. Got '{type(buffsize)}'")
        self._buffsize = buffsize
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
        except Exception as e:
            raise e
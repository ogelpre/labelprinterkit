from __future__ import annotations

import socket
from typing import Type

from ..commands.BaseCommand import BaseCommand

try:
    from pysnmp.hlapi import SnmpEngine, getCmd, UdpTransportTarget, Udp6TransportTarget, \
        ContextData, ObjectType, ObjectIdentity, CommunityData
except ImportError:
    SnmpEngine = None
    getCmd = None
    UdpTransportTarget = None
    Udp6TransportTarget = None
    ContextData = None
    ObjectType = None
    ObjectIdentity = None
    CommunityData = None

from . import UniDirectionalBackend, Command


class TCPBackend(UniDirectionalBackend):
    def __init__(self, host, port=9100, timeout=10):
        self._timeout = timeout
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
        except (socket.gaierror, ConnectionError):
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
            except (socket.gaierror, ConnectionError):
                raise ConnectionError(f"Connection to {host} failed.")
        self._sock = sock

    def write(self, data: bytes | Type[Command]):
        if issubclass(type(data), BaseCommand):
            data = data.to_bytes()
        sent = self._sock.send(data)
        if sent == 0:
            raise IOError("Socket connection broken")


class NetworkBackend(TCPBackend):
    def __init__(self, host, port=9100, timeout=10, snmp_community='public', snmp_port=161):
        if getCmd is None:
            raise RuntimeError('Bidirectional network communication is not supported. Pacakge pysnmp is missing.')
        self._snmp_community = snmp_community
        self._snmp_port = snmp_port
        super().__init__(host, port, timeout)

    def get_status(self):
        remote_address = self._sock.getpeername()[0]

        if self._sock.family == socket.AF_INET6:
            transport = Udp6TransportTarget((remote_address, 161), timeout=self._timeout)
        else:
            transport = UdpTransportTarget((remote_address, 161), timeout=self._timeout)

        iterator = getCmd(
            SnmpEngine(),
            CommunityData('public'),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity('.1.3.6.1.4.1.2435.3.3.9.1.6.1.0'))
        )

        error_indication, _, _, variables = next(iterator)
        if error_indication:
            return None
        else:
            status_data = bytes(variables[0][1])
            return status_data

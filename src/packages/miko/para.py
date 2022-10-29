# para.py  (c)2021  Henrique Moreira
#
# Paramiko main wrapper

"""
Wraps main Paramiko classes.
"""

# pylint: disable=missing-function-docstring, unused-argument

import paramiko

IO_BUFFER_SIZE = 4096


class Validator():
    """ Basic validation methods. """
    def __init__(self, name):
        self._name = name

    def get_name(self) -> str:
        return self._name

    @staticmethod
    def validate_host(host, port) -> bool:
        is_ok = isinstance(host, str) and host
        if not is_ok:
            return False
        return 0 < int(port) <= 65535

class Connector(Validator):
    """ paramiko Connector class """
    _client = None
    _session = None

    def __init__(self, host):
        a_port = 22
        if isinstance(host, tuple):
            a_host, a_port = host
        elif isinstance(host, str):
            a_host = host
        else:
            assert False, f"Invalid host: {host}"
        super().__init__(a_host)
        assert Validator.validate_host(a_host, a_port)
        client = paramiko.Transport((a_host, a_port))
        assert client
        self._client = client

    def client(self):
        assert self._client is not None
        return self._client

    def session(self):
        assert self._session is not None
        return self._session

    def connect(self, username:str, password:str):
        self._client.connect(username=username, password=password)

    def new_session(self) -> bool:
        self._session = self._client.open_channel(kind='session')
        return True

    def dribble(self, command:str) -> tuple:
        """ Returns a triple: msg, stdout_data, stderr_data
        """
        nbytes = IO_BUFFER_SIZE
        stdout_data, stderr_data = [], []
        session = self._session
        if not session:
            return ("No session", [], [])
        session.exec_command(command)
        while not session.exit_status_ready():
            if session.recv_ready():
                stdout_data.append(session.recv(nbytes))
            if session.recv_stderr_ready():
                stderr_data.append(session.recv_stderr(nbytes))
        del self._session
        self._session = None
        return ("", stdout_data, stderr_data)


# Main script
if __name__ == "__main__":
    print("Please import me!")
    # Short examples follow:
    #
    # abc = Connector("pena")
    # abc.connect("guest", mypass); abc.new_session(); abc.dribble("ls -la /")

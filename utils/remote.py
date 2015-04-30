import errno
import re
import logging

import paramiko


DefaultTimeout = 120

class Remote(object):
    """
    Over-engineered class to wrap some simple paramiko tasks
    """

    StandardMachines = {
        'blade_dev01' : {
            'hostname' : 'blade_dev01.agrf.org.au',
            'username' : 'dubrova',
            'timeout' : 20
        }
    }

    @classmethod
    def standard_machine(cls, name):
        details = cls.StandardMachines[name]
        return cls(**details)


    def __init__(self, hostname, username, password=None, timeout=DefaultTimeout):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

        self._connection = None
        self._sftp = None
        self._client = None


    def __del__(self):
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None

        if self._client is not None:
            self._client.close()
            self._client = None

        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @property
    def connection(self):
        if self._connection is None:

            self._connection = paramiko.Transport(self.hostname)
            self._connection.connect(username=self.username, password=self.password)

        return self._connection

    @property
    def ssh_client(self):
        """
        Returns ssh client to destination
        """
        if self._client is None:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.hostname, username=self.username, password=self.password, timeout=self.timeout)
            self._client = client
            logging.info("Created ssh client")
        return self._client


    @property
    def sftp(self):
        if self._sftp is None:
            self._sftp = self.ssh_client.open_sftp()
            logging.info("Opened sftp channel")
        return self._sftp


    def close(self):
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None

        if self._connection is not None:
            self._connection.close()
            self._connection = None


    def exists(self, path):
        """
        os.path.exists for paramiko's SCP object
        """
        try:
            self.sftp.stat(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            else:
                raise
        else:
            return True


    def process_running(self, process_id):
        """
        Check if a process with the given id is running
        """
        return self.exists("/proc/%s" % process_id)


    _find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

    @classmethod
    def quote_parameter(cls, s):
        """
        (Taken from Python 3's shlex module)
        Return a shell-escaped version of the string *s*.
        """
        if not s:
            return "''"
        if cls._find_unsafe(s) is None:
            return s

        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        return "'" + s.replace("'", "'\"'\"'") + "'"


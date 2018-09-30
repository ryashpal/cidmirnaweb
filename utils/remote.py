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
        'bioinformaticslab' : {
             'hostname' : 'bioinformaticslab',
             'username' : 'cidmirna',
             'port' : 11022
        },
 

    }

    @classmethod
    def standard_machine(cls, name):
        if name == 'localhost':
            return Local()
        details = cls.StandardMachines[name]
        return cls(**details)


    def __init__(self, hostname, username, password=None, port=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

        self._ssh_client = None
        self._sftp = None


    def __del__(self):
        self.close()


    @property
    def ssh_client(self):
        """
        Returns ssh client to destination
        """

        # HACKish: Private _transport is set to None whenever the SSHClient object is closed
        if self._ssh_client_is_closed():
            self._ssh_client = self.open_ssh_client()
        return self._ssh_client


    @property
    def sftp(self):
        if self._sftp is None or self._ssh_client_is_closed():
            try:
                self._sftp = self.ssh_client.open_sftp()
            except paramiko.SFTPError as error:
                # convert to something more easily catchable
                raise IOError("%s" % error)
        return self._sftp


    def _ssh_client_is_closed(self):
        return self._ssh_client is None or self._ssh_client._transport is None

    def close(self):
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None

        if self._ssh_client is not None:
            self._ssh_client.close()
            self._ssh_client = None


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

    def open_ssh_client(self):
        """
        Returns ssh client to destination
        """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.hostname, username=self.username, password=self.password, port=self.port)
        return client

    _find_unsafe = re.compile(r'[^\w@%+=:,./-]').search


class Local(object):

    hostname = 'localhost'

    @property
    def sftp(self):
        return self

    def put(self, source_file, target_file):
        """
        Emulate SFTP copying locally
        """

        import shutil

        return shutil.copyfile(source_file, target_file)

    get = put

    def exists(self, filename):
        return os.path.exists(filename)
import pexpect

from climatic.CoreCli import CoreCli
from climatic.connections.Ssh import Ssh, PTY_WINSIZE_COLS
from typing import List, Optional


####################################################################################################
## Python3shell

class Python3Shell(CoreCli):
    """ Extend CoreCli with Python3Shell customizations.
    """

    def __init__(self, connection, **opts):
        """ Initialize OcNOS CLI.
        @param connection  The connection object to be used for accessing the CLI.
        @param opts        Same options as CoreCli initializer.
        """
        if not 'marker' in opts:
            self.marker = '>>>|...'
        if not 'error_marker' in opts:
            self.error_marker = 'Error'
        if not 'strip_cmds' in opts:
            self.strip_cmds = False

        CoreCli.__init__(self,
                         connection,
                         **opts)

####################################################################################################
## SshPython3Shell

class SshPython3Shell(Python3Shell):
    """ Connects to a remote Python3 Shell using SSH.
    Core implementation is done by Ssh and Python3Shell.
    """

    def __init__(self,
                 ip: str,
                 username: str,
                 password: str,
                 port: Optional[int]=22,
                 sh_markers: Optional[List[str]]=['#', '>'],
                 **opts):
        """ Initialize Python3 Shell.
        @param ip          IP address of target. Ex: '234.168.10.12'
        @param username    username for opening SSH connection
        @param password    password for authentication in SSH connection
        @param port        Port used for SSH connection. Defaults to 22
        @param sh_markers  List of accepted markers for the shell when the SSH is established and
                           before launching python3 interpreter
        @param opts        Same options as CoreCli initializer.
        """
        self.sh_markers = sh_markers
        self.name = "Python3.SSH"
        ssh = Ssh(ip, username, port=port)
        Python3Shell.__init__(self,
                              ssh,
                              username=username,
                              password=password,
                              pty_winsize_cols=PTY_WINSIZE_COLS,
                              **opts)

    def login(self):
        """ Login to CLI interface.
        """
        while True:
            index = self.connection.terminal.expect(
                ['Are you sure you want to continue connecting', '.assword'] + self.sh_markers, timeout=10)

            if index == 0:
                self.connection.terminal.sendline('yes')
            if index == 1:
                self.connection.terminal.waitnoecho()
                self.connection.terminal.sendline(self.password)
            if index >= 2:
                break

        # Enter to python3 interpreter
        self.connection.terminal.sendline("python3")
        # Wait for prompt
        self.connection.terminal.expect('>>>')

    def logout(self):
        """ Logout from CLI interface.
        """
        # Ctrl+d to exist python3 shell and exit to end remote session shell
        self.connection.terminal.sendcontrol('d')
        self.connection.terminal.expect(self.sh_markers, timeout=5)
        self.connection.terminal.sendline('exit')

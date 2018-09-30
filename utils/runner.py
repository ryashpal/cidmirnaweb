"""
Simple abstraction over running processes
"""

import os, sys, logging, shlex
import subprocess

class Runner(object):
    ExitCodeFileMissing = -1
    ExitCodeNotFound = -2

    def __init__(self, logger=None):
        self.logger = logger

    def run(self, command):
        raise NotImplementedError

    def still_running(self, process_id):
        raise NotImplementedError

    def process_exit_code(self, process_id):
        raise NotImplementedError


class Local(Runner):
    """
    Runs processes locally
    """

    # exit code thrown by subprocess.call when it cannot find the script/executable to call
    CannotFindExecutableExitCode = -1

    DefaultPollingPeriod = 30

    def __init__(self, logger=None, exit_codes_directory=None):
        super().__init__(logger=logger)

        self.exit_codes_directory = exit_codes_directory


    def run(self, command, environment=None, directory=None):
        """
        Run a command on the local machine. 

        Return the subprocess's id or -1 if the call failed (eg the command wasn't found)
        """

        exit_code_directory_parts = []
        if directory:
            exit_code_directory_parts.append(directory)
        if self.exit_codes_directory:
            exit_code_directory_parts.append(self.exit_codes_directory)
        if not exit_code_directory_parts:
            exit_code_directory_parts.append(os.path.normpath(os.getcwd()))

        exit_code_directory = os.path.normpath(os.path.join(*exit_code_directory_parts))


        # parameters that we will pass to the Popen calls
        parameters = {
            'close_fds' : True,
            'stdout' : subprocess.PIPE
        } 
        if environment:
            parameters['env'] = environment

        if directory:
            parameters['cwd'] = directory

        command_line = ' '.join(shlex.quote(parameter) for parameter in command)
        exit_code_filename = 'exitcode$$.txt'
        exit_code_filename = os.path.join(shlex.quote(exit_code_directory), exit_code_filename)
        command_line += '; echo $? > %s' % exit_code_filename

        full_command = """nohup bash -c %(command_line)s > /dev/null 2>&1 < /dev/null & echo $!"""  % {
            'command_line' : shlex.quote(command_line)   
        }

        full_command = 'mkdir -p %s; %s' % (shlex.quote(exit_code_directory), full_command)

        logging.debug("Running %s" % full_command)
        if self.logger:
            self.logger(full_command)
        try:
            proc = subprocess.Popen(['/bin/bash', '-c', full_command], **parameters)
            process_id = int(proc.stdout.read())   #capture the PID
        except OSError as error:
            logging.error("Problem calling %s: %s" % (full_command, error))
            return self.CannotFindExecutableExitCode
        except ValueError as error:
            logging.error("Problem capturing the PID from running %s: %s" % (full_command, error))
            return None
        else:
            full_exit_code_filename = 'exitcode%s.txt' % process_id
            full_exit_code_filename = os.path.join(exit_code_directory, full_exit_code_filename)

        return process_id, full_exit_code_filename



    def still_running(self, process_id):
        process_id, _ = process_id
        return os.path.exists("/proc/%s" % process_id)

    def process_exit_code(self, process_id):
        process_id, exit_code_filename = process_id        

        try:
            with open(exit_code_filename, 'r') as file:
                first_line = file.readline()
                exit_code = int(first_line)
        except ValueError:
            logging.error("Exit code file not a number for process %s: %s" % (process_id, first_line))
            exit_code = self.ExitCodeNotFound
        except (IOError, OSError):
            # file not there. Assume it failed
            logging.error("No exit code file %s for job: %s" % (exit_code_filename, process_id))
            exit_code = self.ExitCodeFileMissing

        return exit_code


class SSH(Runner):
    def __init__(self, remote, logger=None, exit_codes_directory=None):
        super().__init__(logger=logger)
        self.remote = remote
        self.exit_codes_directory = exit_codes_directory

    def run(self, command, directory=None):
        command_line = ' '.join(shlex.quote(parameter) for parameter in command)
        full_command = """cd %(directory)s; nohup bash -lc %(command_line)s > /dev/null 2>&1 < /dev/null & echo $!"""  % {
            'directory' : directory,
            'command_line' : shlex.quote(command_line)   
        }
        command = ['/usr/bin/ssh']
        if self.remote.port:
            command.extend(['-p', str(self.remote.port)])
        command.extend(['%s@%s' % (self.remote.username, self.remote.hostname), full_command])
        logging.info("Running: '%s' in '%s'" % (' '.join(command), self.remote.hostname))
        proc = subprocess.Popen(command, close_fds=True, stdout=subprocess.PIPE)
        process_id = int(proc.stdout.read())   #capture the remote PID
        return process_id 
        
    def still_running(self, process_id):
        return self.remote.process_running(process_id)

    def process_exit_code(self, process_id):
        pass

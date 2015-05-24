from __future__ import print_function
from IPython.kernel.zmq.kernelbase import Kernel
import socket
from .parser import RedisParser
from .constants import *
import sys
import traceback
import re
import sqlite3
import uuid

try:
    # check if we have defined these variables, if not default
    from redis_kernel_config import *
    if 'PORT' not in locals() and 'PORT' not in globals():
        PORT = None
    if 'HOST' not in locals() and 'HOST' not in globals():
        HOST = None
    if 'HISTORY_DB' not in locals() and 'HISTORY_DB' not in globals():
        HISTORY_DB = None
    # print HOST , PORT
except:
    # if the config isnt found at all
    HOST = None
    PORT = None
    HISTORY_DB = None


class RedisKernel(Kernel):
    # these are required for the kernel to identify itself
    implementation = NAME
    implementation_version = VERSION
    language = LANGUAGE

    # history
    history = {}
    results = {}
    history_db_ready = False

    # the database connection
    redis_socket = None
    connected = False

    # required for the kernel
    @property
    def language_version(self):
        return VERSION

    @property
    def banner(self):
        return BANNER
        
    language_info = {
        'name': NAME,
        'version': VERSION,
        'mimetype': 'text',
        'file_extension': '.txt',
    }

    # handle all init logic here
    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.start_redis(**kwargs)
        self.get_commands()
        self.start_history()

    def start_redis(self, **kwargs):
        if self.redis_socket is None:
            host = HOST or DEFAULT_HOST
            port = PORT or DEFAULT_PORT
            # loop through all connection options
            for res in socket.getaddrinfo(host, port):
                try:
                    family, stype, protocol, name, address = res
                    sock = socket.socket(family, stype, protocol)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.connect(address)
                    # just half a second timeout
                    sock.settimeout(0.25)
                    self.redis_socket = sock
                    self.connected = True
                    # and return on the first successful one
                    return
                except:
                    self.connected = False
                    if sock is not None:
                        sock.close()

    def start_history(self):
        db_name = HISTORY_DB or DEFAULT_DB_NAME
        try:
            self.history_db  = sqlite3.connect(db_name)
            c = self.history_db.cursor()
            c.execute('create table if not exists history (session text, execution_count int, code text, result text)')
            self.history_db_ready = True
        except:
            print(sys.exc_info()[0])
            traceback.print_tb(sys.exc_info()[2])
        
    def record_history(self,session,count,code,data):
        try:
            result = data._repr_text_()
            if type(result)==list:
                result = str(result)
            c = self.history_db.cursor()
            c.execute('insert into history values (?,?,?,?)',(session,count,code,result))
            self.history_db.commit()
        except:
            print(sys.exc_info()[0])
            traceback.print_tb(sys.exc_info()[2])
            
    def recv_all(self):
        total_data = []
        while True:
            try:
                data = self.redis_socket.recv(1024)
            except socket.timeout:
                # sink any timeout here
                break
            if data is None:
                break
            total_data.append(data)
        return ''.encode('utf-8').join(total_data)

    def get_commands(self):
        if self.connected:
            self.commands = RedisParser('')
            try:
                self.redis_socket.send('command count\r\n'.encode('utf-8'))
                count_response = self.recv_all()
                self.command_count = RedisParser(
                    count_response.decode('utf-8'))
                self.redis_socket.send('command\r\n'.encode('utf-8'))
                response = self.recv_all()
                self.commands = RedisParser(response.decode('utf-8'), True)
            except:
                pass
                # print(sys.exc_info()[0])
                # traceback.print_tb(sys.exc_info()[2])
                #self.commands = []

    # the core of the kernel where the work happens
    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not code.strip():
            # we got blank code
            return {'status': 'ok',
                    # The base class increments the execution count
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {},
                    }

        if not self.connected:
            # we are not connected
            return {'status': 'error',
                    'ename': '',
                    'error': 'Unable to connect to Redis server. Check that the server is running.',
                    'traceback': ['Unable to connect to Redis server. Check that the server is running.'],
                    # The base class increments the execution count
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {},
                    }
        # record the code executed
        if store_history:
            self.history[self.execution_count] = code

        # check and fix CRLF before we do anything
        code = self.validate_and_fix_code_crlf(code)
        # print code
        data = None
        try:
            # execute the code and get the result
            self.redis_socket.send(code.encode('utf-8'))
            response = self.recv_all()
            data = RedisParser(response.decode('utf-8'))
            # record the response
            if store_history:
                self.results[self.execution_count] = data
            self.record_history(self.session.session,self.execution_count,code,data)
        except:
            return {'status': 'error',
                    'ename': '',
                    'error': 'Error executing code ' + str(sys.exc_info()[0]),
                    'traceback': 'Error executing code ' + str(sys.exc_info()[0]),
                    # The base class increments the execution count
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {},
                    }

        # if you want to send output
        if not silent:
            # create the output here

            # using display data instead allows to show html
            #stream_content = {'name': 'stdout', 'text':data._repr_text_()}
            #self.send_response(self.iopub_socket, 'stream', stream_content)

            display_content = {
                'source': 'kernel',
                'data': {
                    'text/plain': data._repr_text_(),
                    'text/html': data._repr_html_()
                }, 'metadata': {}
            }

            self.send_response(
                self.iopub_socket, 'display_data', display_content)

        # must return this always
        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
                }

    def do_shutdown(self, restart):
        if self.redis_socket is not None:
            try:
                self.redis_socket.close()
            except:
                pass

    def do_is_complete(self, code):
        # for now always return true - need to add something here
        # later if we decide not to send multi to redis immediately
        return True

    def do_complete(self, code, cursor_pos):
        options = []
        for command in self.commands.result:
            if command.startswith(code):
                options.append(command)

        return {
            'matches': options,
            'metadata': {},
            'status': 'ok',
            'cursor_start': 0,
            'cursor_end': len(code)
        }

    def do_history(self, hist_access_type, output, raw, session=None, start=None, stop=None,
                   n=None, pattern=None, unique=False):
        if hist_access_type == 'tail':
            hist = self.get_tail(
                n,
                raw=raw,
                output=output,
                include_latest=True)
        elif hist_access_type == 'range':
            hist = self.get_range(session, start, stop, raw=raw, output=output)
        elif hist_access_type == 'search':
            hist = self.search(
                pattern,
                raw=raw,
                output=output,
                n=n,
                unique=unique)
        else:
            hist = []

        return {'history': list(hist)}

    def get_tail(self, n, raw, output, include_latest):
        n = n or self.history.__len__()
        key_range = list(self.history.keys())[-n:]
        result = []
        for key in key_range:
            r = (key + 1, self.history[key], self.results[key]._repr_text_())
            result.append(r)
        return result

    def get_range(self, session, start, stop, raw, output):
        start = start or 0
        stop = stop or self.history.__len__()
        start = start if start == 0 else start - 1
        key_range = list(self.history.keys())[start:stop]
        result = []
        for key in key_range:
            r = (key + 1, self.history[key], self.results[key]._repr_text_())
            result.append(r)
        return result

    def search(self, pattern, raw, output, n, unique):
        pattern = pattern or '.*'
        result = []
        for key in list(self.history.keys()):
            if re.search(pattern,self.history[key]):
                r = (key+1, self.history[key], self.results[key]._repr_text_())
                result.append(r)
        return result

    def validate_and_fix_code_crlf(self, code):
        if not (code[-2:] == '\r\n'):
            code = code.strip() + '\r\n'
        return code

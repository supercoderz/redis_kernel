from __future__ import print_function
from IPython.kernel.zmq.kernelbase import Kernel
import socket
from .parser import RedisParser
from .constants import *
import sys,traceback

try:
	#check if we have defined these variables, if not default
	from redis_kernel_config import *
	if 'PORT' not in locals() and 'PORT' not in globals():
		PORT = None
	if 'HOST' not in locals() and 'HOST' not in globals():
		HOST = None
	#print HOST , PORT
except:
	#if the config isnt found at all
	HOST = None
	PORT = None

class RedisKernel(Kernel):
	#these are required for the kernel to identify itself
	implementation = NAME
	implementation_version = VERSION
	language = LANGUAGE		  

	#the database connection
	redis_socket = None
	connected = False
	
	#required for the kernel
	@property
	def language_version(self):
		return VERSION

	@property
	def banner(self):
		return BANNER
	
	
	#handle all init logic here
	def __init__(self,**kwargs):
		Kernel.__init__(self,**kwargs)
		self.start_redis(**kwargs)
		self.get_commands()
		
	def start_redis(self,**kwargs):
		if self.redis_socket is None:
			host = HOST or DEFAULT_HOST
			port = PORT or DEFAULT_PORT 
			#loop through all connection options
			for res in socket.getaddrinfo(host,port):
				try:
					family,stype,protocol,name,address = res
					sock = socket.socket(family,stype,protocol)
					sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
					sock.connect(address)
					sock.settimeout(1)
					self.redis_socket = sock
					self.connected = True
					#and return on the first successful one
					return
				except:
					self.connected = False
					if sock is not None:
						sock.close()
	
	def recv_all(self):
		total_data = []
		while True:
			try:
				data = self.redis_socket.recv(1024)
			except socket.timeout:
				#sink any timeout here
				break
			if data is None:
				break
			total_data.append(data)
		return ''.encode('utf-8').join(total_data)
	
	def get_commands(self):
		if self.connected:
			self.commands = RedisParser('')
			try:
				self.redis_socket.send('command\r\n'.encode('utf-8'))
				response = self.recv_all()
				self.commands = RedisParser(response.decode('utf-8'))
			except:
				traceback.print_tb(sys.exc_info()[2])
				#self.commands = []
	
	#the core of the kernel where the work happens
	def do_execute(self, code, silent, store_history=True, user_expressions=None,
					   allow_stdin=False):
		if not code.strip():
			#we got blank code
			return {'status': 'ok',
					# The base class increments the execution count
					'execution_count': self.execution_count,
					'payload': [],
					'user_expressions': {},
				}
		
		if not self.connected:
			#we are not connected
			return {'status': 'error',
					'ename': '',
					'error': 'Unable to connect to Redis server. Check that the server is running.',
					'traceback': ['Unable to connect to Redis server. Check that the server is running.'],
					# The base class increments the execution count
					'execution_count': self.execution_count,
					'payload': [],
					'user_expressions': {},
				}
			
		
		#check and fix CRLF before we do anything
		code = self.validate_and_fix_code_crlf(code)
		#print code
		data = None
		try:
			#execute the code and get the result
			self.redis_socket.send(code.encode('utf-8'))
			response = self.redis_socket.recv(1024)
			data = RedisParser(response.decode('utf-8'))
		except:
			return {'status': 'error',
					'ename': '',
					'error': 'Error executing code '+ str(sys.exc_info()[0]),
					'traceback': 'Error executing code '+ str(sys.exc_info()[0]),
					# The base class increments the execution count
					'execution_count': self.execution_count,
					'payload': [],
					'user_expressions': {},
				}
		
		#if you want to send output
		if not silent:
			#create the output here
			
			#using display data instead allows to show html
			#stream_content = {'name': 'stdout', 'text':data._repr_text_()}
			#self.send_response(self.iopub_socket, 'stream', stream_content)
			
			display_content = {
				'source':'kernel',
				'data':{
					'text/plain':data._repr_text_(),
					'text/html':data._repr_html_()
				},'metadata':{}
			}
			
			
			self.send_response(self.iopub_socket, 'display_data', display_content)

		#must return this always
		return {'status': 'ok',
				# The base class increments the execution count
				'execution_count': self.execution_count,
				'payload': [],
				'user_expressions': {},
			}

	def do_shutdown(self,restart):
		if self.redis_socket is not None:
			try:
				self.redis_socket.close()
			except:
				pass
	
	def do_is_complete(self,code):
		#for now always return true - need to add something here
		#later if we decide not to send multi to redis immediately
		return True
	
	def validate_and_fix_code_crlf(self,code):
		if not (code [-2:] == '\r\n'):
			code = code.strip() + '\r\n'
		return code

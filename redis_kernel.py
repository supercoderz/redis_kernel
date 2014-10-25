from IPython.kernel.zmq.kernelbase import Kernel
import socket

class RedisKernel(Kernel):
	#these are required for the kernel to identify itself
	implementation = 'redis_kernel'
	implementation_version = '0.1'
	language = 'redis'		  

	#the database connection
	redis_socket = None
	
	#required for the kernel
	@property
	def language_version(self):
		return '0.1'

	@property
	def banner(self):
		return 'redis kernel 0.1'
	
	
	#handle all init logic here
	def __init__(self,**kwargs):
		Kernel.__init__(self,**kwargs)
		self.start_redis()
		
	def start_redis(self):
		if self.redis_socket is None:
			for res in socket.getaddrinfo('localhost',6379):
				try:
					family,stype,protocol,name,address = res
					sock = socket.socket(family,stype,protocol)
					sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
					sock.connect(address)
					self.redis_socket = sock
				except:
					if sock is not None:
						sock.close()
	
	#the core of the kernel where the work happens
	def do_execute(self, code, silent, store_history=True, user_expressions=None,
					   allow_stdin=False):
		
		data = ''
		try:
			self.redis_socket.send(code)
			data = self.redis_socket.recv(1024)
		except:
			#print sys.exc_info()[0]
			pass
		
		#if you want to send output
		if not silent:
			#create the output here
			stream_content = {'name': 'stdout', 'data':data}
			self.send_response(self.iopub_socket, 'stream', stream_content)

		#must return this always
		return {'status': 'ok',
				# The base class increments the execution count
				'execution_count': self.execution_count,
				'payload': [],
				'user_expressions': {},
			}

	def do_shutdown(restart):
		if self.redis_socket is not None:
			try:
				self.redis_socket.close()
			except:
				pass
		
if __name__ == '__main__':
	from IPython.kernel.zmq.kernelapp import IPKernelApp
	IPKernelApp.launch_instance(kernel_class=RedisKernel)
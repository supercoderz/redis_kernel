from .kernel import *
import sys
if sys.version < '3':
	from mock import MagicMock
else:
	from unittest.mock import MagicMock
import IPython


class TestKernel(object):
	def test_create_kernel(self):
		assert RedisKernel() is not None

	def test_misc(self):
		r = RedisKernel()
		assert r.banner is not None
		assert r.language is not None
		assert r.language_version is not None

	def test_fix_crlf(self):
		r = RedisKernel()
		code = r.validate_and_fix_code_crlf('abcd')
		assert code == 'abcd\r\n'
	
	def test_shutdown(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.do_shutdown(False)

	def test_exec_error(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.redis_socket.recv.return_value = None
		r.connected = True
		response = r.do_execute('abracadabra',False)
		assert response['status'] == 'error'

	def test_blank_code_error(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.redis_socket.recv.return_value = None
		r.connected = True
		response = r.do_execute('',False)
		assert response['status'] == 'ok'

	def test_connect_error(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.redis_socket.recv.return_value = None
		response = r.do_execute('abracadabra',False)
		assert response['status'] == 'error'

	def test_normal_response(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		r.redis_socket.recv.return_value = '$1\r\n6\r\n'
		r.connected = True
		response = r.do_execute('get a',False)
		assert response['status'] == 'ok'
	
	def test_error_response(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		r.redis_socket.recv.return_value = '-Errorr\n'
		r.connected = True
		response = r.do_execute('get',False)
		assert response['status'] == 'ok'

	def test_string_response(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		r.redis_socket.recv.return_value = '+OK'
		r.connected = True
		response = r.do_execute('set a 6',False)
		assert response['status'] == 'ok'

	def test_int_response(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		r.redis_socket.recv.return_value = ':1'
		r.connected = True
		response = r.do_execute('bitpos a 1',False)
		assert response['status'] == 'ok'

	def test_array_response(self):
		r = RedisKernel()
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		r.redis_socket.recv.return_value = '*1\r\n$1\r\na\r\n'
		r.connected = True
		response = r.do_execute('keys a*',False)
		assert response['status'] == 'ok'
	
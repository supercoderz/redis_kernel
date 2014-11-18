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
		r.do_shutdown(False)

	def test_exec_error(self):
		r = RedisKernel()
		#dont want this to connect to the real redis server
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.redis_socket.recv.return_value = None
		r.connected = True
		response = r.do_execute('abracadabra',False)
		assert response['status'] == 'ok'

	def test_blank_code_error(self):
		r = RedisKernel()
		response = r.do_execute('',False)
		assert response['status'] == 'ok'

	def test_connect_error(self):
		r = RedisKernel()
		#this does not connect to the real redis and the is connected flag is false
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		r.redis_socket = MagicMock(name='socket', spec=socket.socket)
		r.redis_socket.recv.return_value = None
		response = r.do_execute('abracadabra',False)
		assert response['status'] == 'ok'

	def test_normal_response(self):
		r = RedisKernel()
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		response = r.do_execute('get a',False)
		assert response['status'] == 'ok'
	
	def test_error_response(self):
		r = RedisKernel()
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		response = r.do_execute('get',False)
		assert response['status'] == 'ok'

	def test_string_response(self):
		r = RedisKernel()
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		response = r.do_execute('set a 6',False)
		assert response['status'] == 'ok'

	def test_int_response(self):
		r = RedisKernel()
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		response = r.do_execute('bitpos a 1',False)
		assert response['status'] == 'ok'

	def test_array_response(self):
		r = RedisKernel()
		r.session = MagicMock(name='session', spec=IPython.kernel.zmq.session.Session)
		response = r.do_execute('keys a*',False)
		assert response['status'] == 'ok'
		
	def test_get_commands(self):
		r = RedisKernel()
		assert r.commands.result.__len__() > 0

	def test_get_command_count(self):
		r = RedisKernel()
		assert r.commands.result.__len__() == int(r.command_count._repr_text_())
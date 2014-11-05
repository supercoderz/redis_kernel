from redis_parser import *

class TestRedisParser(object):
	def test_create_parser(self):
		out = RedisParser('-Error: test error\r\n')
	
	def test_basic_parse(self):
		out = RedisParser('$1\r\n4\r\n')
		assert out._repr_text_() is not None
		assert out._repr_html_() is not None
	
	def test_parse_simple_string(self):
		out = RedisParser('+Hello\r\n')
		assert out._repr_text_() == str("'Hello'")
		assert out._repr_html_() == str("<p>'Hello'</p>")

	def test_parse_error(self):
		out = RedisParser('-Error\r\n')
		assert out._repr_text_() == str("'Error'")
		assert out._repr_html_() == str("<p>'Error'</p>")

	def test_parse_integer(self):
		out = RedisParser(':1000\r\n')
		assert out._repr_text_() == str("'1000'")
		assert out._repr_html_() == str("<p>'1000'</p>")

	def test_parse_bulk_string(self):
		out = RedisParser('$5\r\nHello\r\n')
		assert out._repr_text_() == str("'Hello'")
		assert out._repr_html_() == str("<p>'Hello'</p>")

	def test_parse_array(self):
		out = RedisParser('*2\r\n$5\r\nHello\r\n$2\r\nHi\r\n')
		assert out._repr_text_() == str("['Hello', 'Hi']")
		assert out._repr_html_() == str("<p>['Hello', 'Hi']</p>")

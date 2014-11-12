class RedisParser(object):
	def __init__(self,response):
		self.response = response.encode('utf-8')
		self.result = []
		self.is_array = False
		self.is_error = False
		self.parse_response()

	def parse_response(self):
		#get each line of the response
		parts = self.response.split('\r\n')
	
		if parts[0].startswith('*'):
			self.is_array = True
		
		for part in parts:
			if part != '':
				value = self.parse_part(part)
				if value is not None:
					self.result.append(repr(value))
	
	def parse_part(self,part):
		if part[0] == '*':
			#array count
			return None
		elif part[0] in ['-','+',':']:
			if part[0] == '-':
				self.is_error = True
			#error or string or integer
			return part[1:]
		elif part[0] == '$':
			if part[1:]== '-1':
				#handle nil
				return 'nil'
			else:
				#ignore the byte count
				return None
		else:
			#values returned after the type specifier
			return part
	
	def _repr_html_(self):
		out = None
		if self.is_array:
			out = '<p>['+', '.join(self.result)+']</p>'
		elif self.is_error:
			out = "<p style='color:red'>"+'\r\n'.join(self.result)+'</p>'
		else:
			out = '<p>'+'\r\n'.join(self.result)+'</p>'
		return out.encode('utf-8')

	def _repr_text_(self):
		if self.is_array:
			return ('['+', '.join(self.result)+']').encode('utf-8')
		else:
			return ('\r\n'.join(self.result)).encode('utf-8')

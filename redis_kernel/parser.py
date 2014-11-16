class RedisParser(object):
	def __init__(self,response,commands=False):
		self.response = response
		self.result = []
		self.is_array = False
		self.is_error = False
		if not commands:
			self.parse_response()
		else:
			self.parse_commands()

	def parse_commands(self):
		#get each section of the command response
		sections = self.response.split('*6\r\n')
		for section in sections:
			parts = section.split('\r\n')
			#only the first one is the command name
			command = self.parse_part(parts[0])
			self.result.append(command)
	
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
		return out

	def _repr_text_(self):
		if self.is_array:
			return ('['+', '.join(self.result)+']')
		else:
			return ('\r\n'.join(self.result))

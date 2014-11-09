from distutils.core import setup
from distutils.command.install import install
import json
import os.path
import sys
from redis_kernel.constants import *

kernel_json = {"argv":[sys.executable,"-m", NAME, "-f", "{connection_file}"],
 "display_name": DISPLAY_NAME,
 "language": LANGUAGE,
 "codemirror_mode": "shell"
}

class install_with_kernelspec(install):
	def run(self):
		# Regular installation
		install.run(self)

		# Now write the kernelspec
		from IPython.kernel.kernelspec import KernelSpecManager
		from IPython.utils.path import ensure_dir_exists
		destdir = os.path.join(KernelSpecManager().user_kernel_dir, LANGUAGE)
		ensure_dir_exists(destdir)
		with open(os.path.join(destdir, 'kernel.json'), 'w') as f:
			json.dump(kernel_json, f, sort_keys=True)
		
		# TODO: Copy resources once they're specified

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
	# Die, setuptools, die.
	sys.argv.remove(svem_flag)

setup(name = NAME,
	  version = VERSION,
	  description= DESCRIPTION,
	  long_description='Please check https://github.com/supercoderz/redis_kernel',
	  author='Narahari Allamraju',
	  author_email='anarahari@gmail.com',
	  url='https://github.com/supercoderz/redis_kernel',
	  packages=[ NAME ],
	  cmdclass={'install': install_with_kernelspec},
	  install_requires=[],
	  classifiers = [
		  'Framework :: IPython',
		  'Programming Language :: Python :: 2.7',
		  'Programming Language :: Python :: 3.4',
		  'Programming Language :: Python :: 3',
		  'Topic :: System :: Shells',
	  ]
)
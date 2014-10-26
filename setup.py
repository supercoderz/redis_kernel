from distutils.core import setup
from distutils.command.install import install
import json
import os.path
import sys

kernel_json = {"argv":[sys.executable,"-m","redis_kernel", "-f", "{connection_file}"],
 "display_name":"Redis",
 "language":"redis",
 "codemirror_mode":"shell"
}

class install_with_kernelspec(install):
	def run(self):
		# Regular installation
		install.run(self)

		# Now write the kernelspec
		from IPython.kernel.kernelspec import KernelSpecManager
		from IPython.utils.path import ensure_dir_exists
		destdir = os.path.join(KernelSpecManager().user_kernel_dir, 'redis')
		ensure_dir_exists(destdir)
		with open(os.path.join(destdir, 'kernel.json'), 'w') as f:
			json.dump(kernel_json, f, sort_keys=True)
		
		# TODO: Copy resources once they're specified

with open('README.rst') as f:
	readme = f.read()

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
	# Die, setuptools, die.
	sys.argv.remove(svem_flag)

setup(name='redis_kernel',
	  version='0.1',
	  description='A redis kernel for IPython',
	  long_description=readme,
	  author='Narahari Allamraju',
	  author_email='anarahari@gmail.com',
	  url='https://github.com/supercoderz/redis_kernel',
	  py_modules=['redis_kernel'],
	  cmdclass={'install': install_with_kernelspec},
	  install_requires=[],
	  classifiers = [
		  'Framework :: IPython',
		  'License :: OSI Approved :: BSD License',
		  'Programming Language :: Python :: 3',
		  'Topic :: System :: Shells',
	  ]
)
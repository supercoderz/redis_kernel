redis_kernel
============

.. image:: https://travis-ci.org/supercoderz/redis_kernel.svg?branch=master
    :target: https://travis-ci.org/supercoderz/redis_kernel

.. image:: https://pypip.in/download/redis_kernel/badge.svg
    :target: https://pypi.python.org/pypi//redis_kernel/
    :alt: Downloads

.. image:: https://pypip.in/version/redis_kernel/badge.svg
    :target: https://pypi.python.org/pypi/redis_kernel/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/redis_kernel/badge.svg
    :target: https://pypi.python.org/pypi/redis_kernel/
    :alt: Supported Python versions
		
A simple IPython kernel for redis

This requires IPython 3, which is not yet released.

To install please use::

    pip install redis_kernel
	
or::

    easy_install redis_kernel

To test it, install and then::

    ipython qtconsole --kernel redis

For details of how this works, see IPython's docs on `wrapper kernels
<http://ipython.org/ipython-doc/dev/development/wrapperkernels.html>`_.

This connects to redis using sockets, so you dont need the redis python client
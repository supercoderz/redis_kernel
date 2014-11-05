redis_kernel
============

.. image:: https://travis-ci.org/supercoderz/redis_kernel.svg?branch=master
    :target: https://travis-ci.org/supercoderz/redis_kernel


A simple IPython kernel for redis

This requires IPython 3, which is not yet released.

To install please use::

    pip install redis_kernel
	
or::

    easy_install redis_kernel

To test it, install and then::

    ipython qtconsole --kernel redis

For details of how this works, see IPython's docs on `wrapper kernels
<http://ipython.org/ipython-doc/dev/development/wrapperkernels.html>`_, and

This connects to redis using sockets, so you dont need the redis python client
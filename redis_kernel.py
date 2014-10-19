from IPython.kernel.zmq.kernelbase import Kernel
import redis

class RedisKernel(Kernel):
    implementation = 'redis_kernel'
    implementation_version = '0.1'
    language = 'redis'        
    redis_db = None

    @property
    def language_version(self):
        return '0.1'

    @property
    def banner(self):
        return 'redis kernel 0.1'
            
    def __init__(self,**kwargs):
        Kernel.__init__(self,**kwargs)
        self.start_redis()
        
    def start_redis(self):
        if self.redis_db is None:
            redis_db = redis.Redis()
            
    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                       allow_stdin=False):
        pass

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=RedisKernel)
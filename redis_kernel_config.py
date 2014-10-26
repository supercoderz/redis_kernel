#in the absence of this file, the kernel will default to localhost
HOST = 'localhost'
#in the absence of this file, the kernel will default to 6379
PORT = 6379

#you can define anything here and it will be imported into the kernel
#but none of that will actually be used since all your commands are 
#passed on to the redis socket directly. 
import parsl
from parsl.app.app import python_app, bash_app

from config import nsccConfig

userHome = '/home/users/industry/uchicago/tsummer2'

parsl.set_stream_logger()
parsl.load(nsccConfig)

@python_app
def mysim():
    from random import randint
    """Generate a random integer and return it"""
    import time
    time.sleep(10)
    return randint(1,100)

print(mysim().result())
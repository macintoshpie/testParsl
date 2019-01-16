import parsl

from parsl.providers import AWSProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller

from parsl.app.app import python_app, bash_app


# This is an example config, make sure to
#        replace the specific values below with the literal values
#          (e.g., 'USERNAME' -> 'your_username')

config = Config(
    executors=[
        IPyParallelExecutor(
            label='ec2_single_node',
            provider=AWSProvider(
                'ami-01e3b8c3a51e88954',    # Please replace image_id with your image id, e.g., 'ami-82f4dae7'
                region='us-east-1',    # Please replace region with your region
                key_name='testVirginiaKey',
                key_file='~/Documents/uchicago/pitjjgenomics/awskeys.json',    # Please replace KEY with your key name **Could be key_file instead...
                profile="default",
                state_file='awsproviderstate.json',
                nodes_per_block=1,
                init_blocks=1,
                max_blocks=1,
                min_blocks=0,
                walltime='01:00:00',
            ),
            controller=Controller(public_ip=None),    # Please replace PUBLIC_IP with your public ip
        )
    ],
)

parsl.load(config)
parsl.set_stream_logger()

@python_app
def mysim():
    from random import randint
    """Generate a random integer and return it"""
    return randint(1,100)

print(mysim().result())

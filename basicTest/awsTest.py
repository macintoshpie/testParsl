import parsl

from parsl.providers import AWSProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller

from parsl.addresses import address_by_route, address_by_query, address_by_hostname

from parsl.app.app import python_app, bash_app


# This is an example config, make sure to
#        replace the specific values below with the literal values
#          (e.g., 'USERNAME' -> 'your_username')

config = Config(
    executors=[
        IPyParallelExecutor(
            label='ec2_single_node',
            provider=AWSProvider(
                'ami-0ac019f4fcb7cb7e6', # 'ami-00bbb68c7e6ca73ce',    # Please replace image_id with your image id, e.g., 'ami-82f4dae7'
                region='us-east-1',    # Please replace region with your region
                key_name='testVirginiaKey',
                profile="default",
                state_file='awsproviderstate.json',
                nodes_per_block=1,
                init_blocks=1,
                max_blocks=1,
                min_blocks=0,
                walltime='01:00:00',
            ),
            controller=Controller(public_ip="10.0.90.253"),    # Please replace PUBLIC_IP with your public ip
        )
    ],
)

parsl.set_stream_logger()
parsl.load(config)

@python_app
def mysim():
    from random import randint
    """Generate a random integer and return it"""
    import time
    time.sleep(10)
    return randint(1,100)

print(mysim().result())
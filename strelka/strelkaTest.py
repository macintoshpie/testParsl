import os

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
                'ami-08c7f5a9a205fa125', # image with strelka installed
                region='us-east-2',
                key_name='testKeyPair',
                profile="default",
                state_file='awsproviderstate.json',
                nodes_per_block=1,
                init_blocks=1,
                max_blocks=1,
                min_blocks=0,
                walltime='01:00:00',
            ),
            controller=Controller(public_ip="10.0.14.150"),
        )
    ],
)

parsl.set_stream_logger()
parsl.load(config)

@bash_app
def mysim(script_file, stdout=None, stderr=None):
    return script_file

# mysim(inputs=[os.path.join(os.getcwd(), "bashFile.sh")]).result()
x = mysim(os.path.abspath('bashFile.sh'), stdout="testing.stdout", stderr="testing.stderr")

# This blocks until the script execution is completed
print(x.result())

with open(x.stdout, 'r') as f:
    print("Content of stdout :", f.read())

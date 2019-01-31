import parsl

from parsl.channels import LocalChannel
from parsl.launchers import SingleNodeLauncher
from parsl.providers import TorqueProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller

from parsl.app.app import python_app, bash_app

initCmd = """#!/usr/bin/env bash
module load anaconda/3
conda create --name parsl_py36 python=3.6
source activate parsl_py36

# install parsl
python3 -m pip install parsl
"""

userHome = '/home/users/industry/uchicago/tsummer2'

config = Config(
  executors=[
    IPyParallelExecutor(
      label='nscc_exec',
      workers_per_node=1,
      provider=TorqueProvider(
        channel=LocalChannel(),
        nodes_per_block=1,
        init_blocks=2,
        max_blocks=1,
        launcher=SingleNodeLauncher(),
        scheduler_options='#PBS -P 11001079\n#PBS -l mem=1G\n',
        worker_init='',
        walltime="00:5:00"
      ),
      controller=Controller(public_ip='192.168.153.3'),    # Please replace PUBLIC_IP with your public ip
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
from parsl.channels import LocalChannel
from parsl.launchers import SimpleLauncher
from parsl.providers import TorqueProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller
from parsl.executors import HighThroughputExecutor

from parsl.addresses import address_by_interface

from requests import get

# config for runnnig on NSCC's Aspire

initCmd = """module load anaconda/3
source activate parsl_py36
"""

nsccConfig = Config(
  executors=[
    IPyParallelExecutor(
      label='nscc_exec',
      workers_per_node=24,
      provider=TorqueProvider(
        cmd_timeout=120,
        channel=LocalChannel(),
        nodes_per_block=1,
        init_blocks=1,
        max_blocks=1,
        launcher=SimpleLauncher(),
        scheduler_options='#PBS -P 11001079\n#PBS -l mem=96G\n',
        worker_init=initCmd,
        walltime="06:00:00"
      ),
      controller=Controller(public_ip=address_by_interface('ib0')),    # Please replace PUBLIC_IP with your public ip
    )
  ],
)

htxConfig = Config(
  executors=[
    HighThroughputExecutor(
      label='nscc_exec',
      address=address_by_interface('ib0'),
      max_workers=24, # Set this
      provider=TorqueProvider(
        cmd_timeout=120,
        channel=LocalChannel(),
        nodes_per_block=1,
        init_blocks=1,
        max_blocks=1,
        launcher=SimpleLauncher(),
        scheduler_options='#PBS -P 11001079\n#PBS -l mem=96G\n',
        worker_init=initCmd,
        walltime="24:00:00"
      ),
    )
  ],
)

# annaConfig = Config(
#   executors=[
#     HighThroughputExecutor(
#       label="htex",
#       worker_debug=True,
#       cores_per_worker=1,
#       public_ip=get('https://api.ipify.org').text,
#       provider=TorqueProvider(
#         queue='normal',
#         launcher=SimpleLauncher(),
#         nodes_per_block=1,
#         tasks_per_node=24,
#         init_blocks=1,
#         max_blocks=1,
#         overrides='#PBS -P 11001079\nsource activate swag\n',
#         queue_timeout=300,
#         walltime='00:90:00'
#       ),
#     )
#   ],
#   retries=3
# )
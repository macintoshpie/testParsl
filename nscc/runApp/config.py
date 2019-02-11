from parsl.channels import LocalChannel
from parsl.launchers import SimpleLauncher
from parsl.providers import TorqueProvider

from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.addresses import address_by_interface


initCmd = """module load anaconda/3
source activate parsl_py36
"""

def getParslConfig(paropt_config):
  """config for runnnig on NSCC's Aspire"""

  return Config(
    executors=[
      HighThroughputExecutor(
        label='nscc_{}'.format(paropt_config['name']),
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
          walltime=paropt_config['walltime']
        ),
      )
    ],
)
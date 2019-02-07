from parsl.channels import LocalChannel
from parsl.launchers import SingleNodeLauncher
from parsl.providers import TorqueProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller

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
        launcher=SingleNodeLauncher(),
        scheduler_options='#PBS -P 11001079\n#PBS -l mem=96G\n',
        worker_init=initCmd,
        walltime="00:10:00"
      ),
      controller=Controller(public_ip='192.168.153.3'),    # Please replace PUBLIC_IP with your public ip
    )
  ],
)
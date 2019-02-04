from parsl.providers import AWSProvider
from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller
from parsl.executors.threads import ThreadPoolExecutor

from paropt import ParslOptimizer

# FIXME: getting error when running on aws:
# Traceback (most recent call last):
#   File "/home/ubuntu/miniconda3/envs/parsl_py36/lib/python3.6/site-packages/parsl/dataflow/dflow.py", line 256, in handle_exec_update
#     res = future.result()
#   File "/home/ubuntu/miniconda3/envs/parsl_py36/lib/python3.6/concurrent/futures/_base.py", line 425, in result
#     return self.__get_result()
#   File "/home/ubuntu/miniconda3/envs/parsl_py36/lib/python3.6/concurrent/futures/_base.py", line 384, in __get_result
#     raise self._exception
#   File "/home/ubuntu/miniconda3/envs/parsl_py36/lib/python3.6/site-packages/ipyparallel/client/asyncresult.py", line 226, in _resolve_result
#     raise r
# ipyparallel.error.RemoteError: ModuleNotFoundError(No module named 'parslLibrary')
# from parslLibrary import timeCmd

from parsl.app.app import python_app

# Parsl function for timing command execution time
@python_app
def timeCmd(cmd, params, invert):
  import os
  from string import Template
  import subprocess
  import time
  import uuid

  cmd_script = os.path.expanduser("~/timeCmdScript_{}.sh".format(uuid.uuid1()))
  cmd = Template(cmd).safe_substitute(params)
  with open(cmd_script, "w") as f:
    f.write(cmd)

  t1 = time.time()
  proc = subprocess.Popen(['bash', cmd_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  outs, errs = proc.communicate()
  t2 = time.time()
  total_time = t2 - t1
  if invert:
    total_time = -total_time
  return (proc.returncode, outs.decode(), total_time)

awsConfig = Config(
  executors=[
    IPyParallelExecutor(
      label='ec2_single_node',
      provider=AWSProvider(
        'ami-09841c7042bfeaf66',
        instance_type='m5.2xlarge',
        spot_max_bid=1,
        region='us-east-2',
        key_name='testKeyPair',
        profile="default",
        state_file='awsproviderstate.json',
        nodes_per_block=1,
        init_blocks=2,
        max_blocks=2,
        min_blocks=0,
        walltime='01:00:00',
      ),
      controller=Controller(public_ip="10.0.14.150"),
    )
  ],
)

cmd = """
cd /home/ubuntu/data
rm -rf analysis

${STRELKA_INSTALL_PATH}/bin/configureStrelkaGermlineWorkflow.py \
  --ref GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna \
  --bam chr21.bam \
  --runDir analysis

# execute on a single local machine with $ncpus
analysis/runWorkflow.py -m local -j ${nCPUs} -g ${memPerCPU}
"""

cmdParams = {
  'nCPUs': (2, 8),
  'memPerCPU': (8, 32)
}

po = ParslOptimizer(
  awsConfig,
  timeCmd,
  command=cmd,
  command_params=cmdParams,
  init_points=2,
  n_iter=2
)

po.run(savePlots=True)
print("Max: ", po.max)
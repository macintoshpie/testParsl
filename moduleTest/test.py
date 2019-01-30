from parsl.providers import AWSProvider
from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller
from parsl.executors.threads import ThreadPoolExecutor


from paropt import ParslOptimizer

# awsConfig = Config(
#   executors=[
#     IPyParallelExecutor(
#       label='ec2_single_node',
#       provider=AWSProvider(
#         'ami-08c7f5a9a205fa125', # image with strelka installed
#         region='us-east-2',
#         key_name='testKeyPair',
#         profile="default",
#         state_file='awsproviderstate.json',
#         nodes_per_block=1,
#         init_blocks=2,
#         max_blocks=2,
#         min_blocks=0,
#         walltime='01:00:00',
#       ),
#       controller=Controller(public_ip="10.0.14.150"),
#     )
#   ],
# )

local_config = Config(
  executors=[
    ThreadPoolExecutor(
      max_threads=8,
      label='local_threads'
    )
  ]
)

cmd = ''
scriptPath = './sleepFunc.sh'
with open(scriptPath, 'r') as f:
  cmd = f.read()

cmdParams = {
  'x': (2, 4),
  'y': (-3, 3)
}

po = ParslOptimizer(
  local_config,
  command=cmd,
  command_params=cmdParams,
  init_points=2,
  n_iter=3
)

po.run(True)
print("Max: ", po.max)
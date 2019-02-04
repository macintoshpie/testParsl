from parsl.providers import AWSProvider
from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller
from parsl.executors.threads import ThreadPoolExecutor

from paropt import ParslOptimizer

from parslLibrary import timeCmd

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
cd ~/data
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
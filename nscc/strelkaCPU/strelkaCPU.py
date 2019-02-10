import os

from parsl.app.app import python_app

from paropt import ParslOptimizer
from config import nsccConfig, htxConfig

# Parsl function for timing command execution time
@python_app
def timeCmd(cmd, params):
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
  # invert b/c we are trying to minimize time
  total_time = -total_time
  # divide by number of seconds in a day to scale down
  secs_in_day = 86400
  total_time = total_time / secs_in_day
  return (proc.returncode, outs.decode(), total_time)

cmd = """
${STRELKA_INSTALL_PATH}/bin/configureStrelkaGermlineWorkflow.py \
  --ref /home/projects/11001079/references/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna \
  --bam /home/projects/11001079/giab/NHGRI_Illumina300X_Chinesetrio_novoalign_bams/chr21.bam \
  --runDir analysis

analysis/runWorkflow.py -m local -j ${nCPUs} -g ${totalMem}

# remove generated data directory
rm -rf analysis
"""

cmdParams = {
  'nCPUs': (2, 24),
  'totalMem': (8, 96)
}

po = ParslOptimizer(
  htxConfig,
  timeCmd,
  command=cmd,
  command_params=cmdParams,
  init_points=2,
  n_iter=2
)

po.run()
print("Max: ", po.max)
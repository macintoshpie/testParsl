from paropt import ParslOptimizer
from parsl.app.app import python_app

from ..config import nsccConfig

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

# read in commands from local bash file
while open('strelkaDemo.bash', 'r') as f:
  cmd = f.read()

cmdParams = {
  'nCPUs': (2, 24),
  'memPerCPU': (8, 32)
}

po = ParslOptimizer(
  nsccConfig,
  timeCmd,
  command=cmd,
  command_params=cmdParams,
  init_points=2,
  n_iter=2
)

po.run()
print("Max: ", po.max)
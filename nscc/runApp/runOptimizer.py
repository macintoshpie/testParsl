import os
import sys
import json

from parsl.app.app import python_app

from paropt import ParslOptimizer
from config import getParslConfig

HELP = """Usage:
python3 runOptimizer.py <config_path>
  config_path: path to paropt configuration file
"""

# Parsl function for timing command execution time
@python_app
def timeCmd(cmd_script_path):
  import os
  import subprocess
  import time

  t1 = time.time()
  proc = subprocess.Popen(['bash', cmd_script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  outs, errs = proc.communicate()
  t2 = time.time()
  total_time = t2 - t1
  # invert b/c we are trying to minimize time
  total_time = -total_time
  # divide by number of seconds in a day to scale down
  secs_in_day = 86400
  total_time = total_time / secs_in_day
  return (proc.returncode, outs.decode(), total_time)

# get paropt config file
if len(sys.argv) != 2:
  print(HELP)
  exit(1)
with open(sys.argv[1]) as f:
  paropt_config = json.loads(f.read())

print("Paropt config: {}".format(paropt_config))

# reformat params to tuples
for p, rng in paropt_config['parameters'].items():
  paropt_config['parameters'][p] = tuple(rng)

print("Final paropt config: {}".format(paropt_config))

po = ParslOptimizer(
  getParslConfig(paropt_config, False),
  timeCmd,
  paropt_config=paropt_config
)

po.run()

import json
from string import Template
import time
import subprocess
import sys

HELP = """Usage:
python3 submit.py <paropt_config_path>
"""

if len(sys.argv) != 2:
  print(HELP)
  exit(1)
with open(sys.argv[1]) as f:
  paropt_config = json.loads(f.read())

# create a script to submit job
with open('submitTemplate.sh', 'r') as f:
  submitScript = Template(f.read()).safe_substitute(paropt_config_path=sys.argv[1], **paropt_config)
submitScriptPath = 'submit_{}_{}.sh'.format(paropt_config['name'], int(time.time()))
with open(submitScriptPath, 'w') as f:
  f.write(submitScript)

proc = subprocess.Popen(['qsub', submitScriptPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
outs, errs = proc.communicate()
print(outs, errs)
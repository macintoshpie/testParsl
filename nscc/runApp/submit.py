import json
from string import Template
import time
import subprocess

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
  submitScript = Template(f.read()).safe_substitute(**paropt_config)
submitScriptName = 'submit_{}_{}.sh'.format(paropt_config['name'], int(time.time()))
with open(submitScriptName, 'w') as f:
  f.write(submitScript)

cmd = Template(self.command).safe_substitute(params)
proc = subprocess.Popen(['bash', cmd_script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
outs, errs = proc.communicate()
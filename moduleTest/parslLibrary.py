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
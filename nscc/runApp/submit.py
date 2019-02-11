import json

HELP = """Usage:
python3 submit.py <paropt_config_path>
"""

if len(sys.argv) != 2:
  print(HELP)
  exit(1)
with open(sys.argv[1]) as f:
  paropt_config = json.loads(f.read())


import os
import sys

import parsl
from parsl.providers import AWSProvider
from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller
from parsl.executors.threads import ThreadPoolExecutor
from parsl.app.app import python_app, bash_app

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction

awsConfig = Config(
    executors=[
        IPyParallelExecutor(
            label='ec2_single_node',
            provider=AWSProvider(
                'ami-08c7f5a9a205fa125', # image with strelka installed
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

localConfig = Config(
    executors=[
        ThreadPoolExecutor(
            max_threads=8,
            label='local_threads'
        )
    ]
)

parsl.set_stream_logger()
debug = False
if sys.platform == "darwin":
    parsl.load(localConfig)
    debug = True
else:
    parsl.load(awsConfig)

@python_app
def timeApp(cmd, parameters):
    import os
    from string import Template
    import subprocess
    import time

    scriptPath = os.path.expanduser("~/timeAppScript.sh")
    cmd = Template(cmd).safe_substitute(parameters)
    with open(scriptPath, "w") as text_file:
        text_file.write(cmd)

    t1 = time.time()
    proc = subprocess.Popen(['bash', scriptPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    outs, errs = proc.communicate()
    t2 = time.time()
    return (proc.returncode, outs, t2 - t1)


def prepareAndRun(params, debug=False):
    params = {key: int(val) for key, val in params.items()}
    cmd = ''
    if debug:
        cmd = """#!/usr/bin/env bash
bashVar="This is a bash var"
echo "Hello World - ${bashVar}"
echo "nCPUs: ${nCPUs}"
echo "memPerCPU: ${memPerCPU}"
"""
    else:
        with open(os.path.dirname(os.path.abspath(__file__))+'/strelkaDemo.bash', 'r') as f:
            cmd = f.read()
    print(cmd)
    print("RUNNING WITH PARAMS: ", params)
    return timeApp(cmd, params)

def registerResult(params, res):
    if res[0] == 0:
        bo.register(
            params=params,
            target=res[2],
        )
    else:
        raise Exception("NON_ZERO_EXIT:\n  PARAMS: {}\n  OUT: {}".format(params, res[1]))

paramDefs = {
    'nCPUs': (1, 4),
    'memPerCPU': (2, 4)
}

bo = BayesianOptimization(
    f=prepareAndRun,
    pbounds=paramDefs,
    verbose=2,
    random_state=1,
)

utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)

n_init = 2
n_iter = 2

# run initial random points in parallel
init_params = []
init_futures = []
for i in range(n_init):
    init_params.append(bo.suggest(utility))
    init_futures.append(prepareAndRun(init_params[i], debug))

# Wait for initial results before continuing
# add results to GP model
for init_point, init_fut in zip(init_params, init_futures):
    res = init_fut.result()
    registerResult(init_point, res)

# run remaining tests
for i in range(n_iter):
    probe_point = bo.suggest(utility)
    res = prepareAndRun(probe_point, debug).result()
    registerResult(probe_point, res)

print("FINISHED: {}".format(bo.max))
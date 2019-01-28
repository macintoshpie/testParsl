import os
import sys
from string import Template

import parsl

from parsl.providers import AWSProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller
from parsl.executors.threads import ThreadPoolExecutor


from parsl.app.app import python_app, bash_app

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
                init_blocks=1,
                max_blocks=1,
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

cmd = """#!/usr/bin/env bash
#
# Execute small germline variant demonstration/verification run
#

set -o nounset
set -o pipefail

scriptDir="/home/ubuntu/strelka2/bin"
demoDir=$scriptDir/../share/demo/strelka
dataDir=$demoDir/data
expectedDir=$demoDir/expectedResults

analysisDir=./strelkaGermlineDemoAnalysis
configScript=$scriptDir/configureStrelkaGermlineWorkflow.py
demoConfigFile=$demoDir/strelkaGermlineDemoConfig.ini


# verify paths are correctly configured
if [ ! -e $configScript ]; then
    cat<<END 1>&2
ERROR: Strelka must be installed prior to running demo.
END
    exit 2
fi

if [ -e $analysisDir ]; then
    cat<<END 1>&2
ERROR: Demo analysis directory already exists: '$analysisDir'
       Please remove/move this to rerun demo.
END
    exit 2
fi

# create workflow
cmd="$configScript \
--bam='$dataDir/NA12891_demo20.bam' \
--bam='$dataDir/NA12892_demo20.bam' \
--referenceFasta='$dataDir/demo20.fa' \
--callMemMb=1024 \
--exome \
--disableSequenceErrorEstimation \
--runDir=$analysisDir"

eval $cmd

# run workflow
cmd="$analysisDir/runWorkflow.py -m local -j ${nCPUs} -g ${memPerCPU}"
$cmd


if [ $? -ne 0 ]; then
    cat<<END 1>&2
ERROR: Workflow execution step failed
END
    exit 1
fi
"""

if sys.platform == "darwin":
    parsl.load(localConfig)
    cmd = """#!/usr/bin/env bash
bashVar="This is a bash var"
echo "Hello World - ${bashVar}"
echo "nCPUs: ${nCPUs}"
echo "memPerCPU: ${memPerCPU}"
"""
else:
    parsl.load(awsConfig)

@python_app
def timeApp(cmd, parameters):
    scriptPath = os.path.expanduser("~/timeAppScript.sh")
    cmd = Template(cmd).safe_substitute(parameters)
    with open(scriptPath, "w") as text_file:
        text_file.write(cmd)

    import subprocess
    import time
    t1 = time.time()
    proc = subprocess.Popen(['bash', scriptPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    outs, errs = proc.communicate()
    t2 = time.time()
    return (outs, t2 - t1)

params = {
    'nCPUs': 1,
    'memPerCPU': 4
}
x = timeApp(cmd, params)
print(x.result())
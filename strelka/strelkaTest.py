import os

import parsl

from parsl.providers import AWSProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller

from parsl.addresses import address_by_route, address_by_query, address_by_hostname

from parsl.app.app import python_app, bash_app


# This is an example config, make sure to
#        replace the specific values below with the literal values
#          (e.g., 'USERNAME' -> 'your_username')

config = Config(
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

parsl.set_stream_logger()
parsl.load(config)

@python_app
def mysim():
    cmdX = """#!/usr/bin/env bash

echo "Hello World"

echo $STRELKA_INSTALL_PATH

#
# Strelka - Small Variant Caller
# Copyright (c) 2009-2018 Illumina, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

#
# Execute small germline variant demonstration/verification run
#

set -o nounset
set -o pipefail

scriptDir=$(dirname $0)
demoDir=$scriptDir/../share/demo/strelka
dataDir=$demoDir/data
expectedDir=$demoDir/expectedResults

analysisDir=./strelkaGermlineDemoAnalysis

configScript=$scriptDir/configureStrelkaGermlineWorkflow.py

demoConfigFile=$demoDir/strelkaGermlineDemoConfig.ini



if [ ! -e $configScript ]; then
    cat<<END 1>&2
ERROR: Strelka must be installed prior to running demo.
END
    exit 2
fi


#
# Step 1: configure demo
#
if [ -e $analysisDir ]; then
    cat<<END 1>&2
ERROR: Demo analysis directory already exists: '$analysisDir'
       Please remove/move this to rerun demo.
END
    exit 2
fi

cmd="$configScript \
--bam='$dataDir/NA12891_demo20.bam' \
--bam='$dataDir/NA12892_demo20.bam' \
--referenceFasta='$dataDir/demo20.fa' \
--callMemMb=1024 \
--exome \
--disableSequenceErrorEstimation \
--runDir=$analysisDir"

echo 1>&2
echo "**** Starting demo configuration and run." 1>&2
echo "**** Configuration cmd: '$cmd'" 1>&2
echo 1>&2
eval $cmd

if [ $? -ne 0 ]; then
    echo 1>&2
    echo "ERROR: Demo configuration step failed" 1>&2
    echo 1>&2
    exit 1
else
    echo 1>&2
    echo "**** Completed demo configuration." 1>&2
    echo 1>&2
fi


#
# Step 2: run demo (on single local core):
#
#stderrlog=$analysis_dir/make.stderr.log
cmd="$analysisDir/runWorkflow.py -m local -j 1 -g 4"
echo 1>&2
echo "**** Starting demo workflow execution." 1>&2
echo "**** Workflow cmd: '$cmd'" 1>&2
echo 1>&2
$cmd


if [ $? -ne 0 ]; then
    cat<<END 1>&2
ERROR: Workflow execution step failed
END
#        See make error log file: '$stderrlog'
    exit 1
else
    echo 1>&2
    echo "**** Completed demo workflow execution." 1>&2
    echo 1>&2
fi

echo 1>&2
echo "**** Demo/verification successfully completed" 1>&2
echo 1>&2
"""

    cmd = """#!/usr/bin/env bash
echo 'Hello World'
"""
    with open("/home/ubuntu/profile.sh", "w") as text_file:
        text_file.write(cmd)

    import subprocess
    proc = subprocess.Popen(['bash', '/home/ubuntu/profile.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        outs, errs = proc.communicate(timeout=200)
        return outs
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate(timeout=300)
        return outs

# mysim(inputs=[os.path.join(os.getcwd(), "bashFile.sh")]).result()
x = mysim()

# This blocks until the script execution is completed
print(x.result())
print(x)
print(dir(x))
print(x.stdout)

with open(x.stdout, 'r') as f:
    print("Content of stdout :", f.read())

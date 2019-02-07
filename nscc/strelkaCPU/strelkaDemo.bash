#!/usr/bin/env bash
#
# Execute small germline variant demonstration/verification run
#

set -o nounset
set -o pipefail

scriptDir="${STRELKA_INSTALL_PATH}/bin"
demoDir=$scriptDir/../share/demo/strelka
dataDir=$demoDir/data
expectedDir=$demoDir/expectedResults

analysisDir="./strelkaGermlineDemoAnalysis$(RANDOM)"
configScript=$scriptDir/configureStrelkaGermlineWorkflow.py
demoConfigFile=$demoDir/strelkaGermlineDemoConfig.ini


# verify paths are correctly configured
if [ ! -e $configScript ]; then
    cat<<END 1>&2
ERROR: Strelka must be installed prior to running demo.
END
    exit 2
fi

rm -rf $analysisDir

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
cmd="$analysisDir/runWorkflow.py -m local -j ${nCPUs}"
$cmd


if [ $? -ne 0 ]; then
    cat<<END 1>&2
ERROR: Workflow execution step failed
END
    exit 1
fi

# remove generated data directory
rm -rf $analysisDir
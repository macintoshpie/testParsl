#!/bin/bash

#PBS -q normal
#PBS -P 11001079
#PBS -l select=1:ncpus=1:mem=2G
#PBS -l walltime=${walltime}
#PBS -N ${name}_head
#PBS -o /home/users/industry/uchicago/tsummer2/outputfiles/${name}_head.o
#PBS -e /home/users/industry/uchicago/tsummer2/errorfiles/${name}_head.e

module load anaconda/3
source activate parsl_py36

echo "Starting ${name} optimization at $(date)"
python ${HOME}/testParsl/nscc/runApp/runOptimizer.py ${paropt_config_path}
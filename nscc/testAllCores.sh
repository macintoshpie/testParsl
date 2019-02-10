#!/bin/bash

#PBS -q normal
#PBS -P 11001079
#PBS -l nodes=1:ppn=24
#PBS -l walltime=00:20:00
#PBS -N Strelka_Head
#PBS -o /home/users/industry/uchicago/tsummer2/outputfiles/Strelka_Head.o
#PBS -e /home/users/industry/uchicago/tsummer2/errorfiles/Strelka_Head.e

echo "Started head task"
echo "Running in $(pwd)"

${STRELKA_INSTALL_PATH}/bin/configureStrelkaGermlineWorkflow.py \
  --ref /home/projects/11001079/references/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna \
  --bam /home/projects/11001079/giab/NHGRI_Illumina300X_Chinesetrio_novoalign_bams/chr21.bam \
  --runDir analysis

analysis/runWorkflow.py -m local -j 24 -g 96
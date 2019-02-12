bam="/home/projects/11001079/ts_data/chr21rg.bam"
ref="/home/projects/11001079/ts_data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"

# remove generated data directory (just in case it already exists)
rm -rf analysis

${STRELKA_INSTALL_PATH}/bin/configureStrelkaGermlineWorkflow.py \
  --ref ${ref} \
  --bam ${bam} \
  --runDir analysis

analysis/runWorkflow.py -m local -j ${nCPUs} -g ${totalMem}

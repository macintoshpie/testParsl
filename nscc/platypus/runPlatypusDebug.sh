bam="/home/projects/11001079/ts_data/chr21rg.bam"
ref="/home/projects/11001079/ts_data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"

vcf="${HOME}/results/chr21platypus.vcf.gz"

# see here for configs:
# https://www.well.ox.ac.uk/research/research-groups/lunter-group/softwares/platypus-documentation

sleep 5

echo "platypus callVariants --bamFiles=${bam} --refFile=${ref} --output=${vcf} --nCPU ${nCPU} --bufferSize ${bufferSize}"

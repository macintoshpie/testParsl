module load java
bam="/home/projects/11001079/ms_data/chr21/bam/chr21rg.bam"
ref="/home/projects/11001079/ms_data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"

vcf="${HOME}/results/chr21gatk4.vcf.gz"

gatk HaplotypeCaller -I $bam -O $vcf -R $ref

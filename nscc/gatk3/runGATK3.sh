module load java
bam="/home/projects/11001079/ms_data/chr21/bam/chr21rg.bam"
ref="/home/projects/11001079/ms_data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"

vcf="${HOME}/results/chr21gatk3.vcf.gz"

# descr of nt and nct: https://github.com/broadinstitute/gatk/issues/5035
# effect of nct, see https://github.com/broadinstitute/gatk-protected/blob/b9d035bed49b8e91542029a0440bc02ee25cbc43/src/main/java/org/broadinstitute/hellbender/tools/walkers/haplotypecaller/HaplotypeCaller.java#L136

java -jar ${HOME}/GATK3.8-1/GenomeAnalysisTK.jar -R $ref -T HaplotypeCaller -I $bam -nct ${nct} -nt ${nt} -o $vcf

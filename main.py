#!/usr/bin/env python
#1 core 

import os

# os.system(
# '''
# snakemake \
# -s /data/users/ltucker/A_thaliana_Taz-0_assembly/workflow/quality_control.rules \
# --profile /data/users/ltucker/A_thaliana_Taz-0_assembly/slurm \
# --latency-wait 300 \
# -p \
# 2>&1 | tee /data/users/ltucker/A_thaliana_Taz-0_assembly/logs/log_qc.txt
# '''
# )

os.system(
'''
  snakemake \
  -s /data/users/ltucker/A_thaliana_Taz-0_assembly/workflow/all_assemblies.rules \
  --profile /data/users/ltucker/A_thaliana_Taz-0_assembly/slurm \
  -p \
  2>&1 | tee /data/users/ltucker/A_thaliana_Taz-0_assembly/logs/log_assemblies.txt
'''
)

os.system(
'''
  snakemake \
  -s /data/users/ltucker/A_thaliana_Taz-0_assembly/workflow/3_busco.rules \
  --profile /data/users/ltucker/A_thaliana_Taz-0_assembly/slurm \
  -p \
  2>&1 | tee /data/users/ltucker/A_thaliana_Taz-0_assembly/logs/3_busco_log.txt
'''
)

os.system(
'''
  snakemake \
  -s /data/users/ltucker/A_thaliana_Taz-0_assembly/workflow/quast.rules.py \
  --profile /data/users/ltucker/A_thaliana_Taz-0_assembly/slurm \
  -p \
  2>&1 | tee /data/users/ltucker/A_thaliana_Taz-0_assembly/logs/quast_log.txt
'''
)

snakemake \
  -s /data/users/ltucker/A_thaliana_Taz-0_assembly/workflow/5_mercury.rules \
  --profile /data/users/ltucker/A_thaliana_Taz-0_assembly/slurm \
  -p \
  2>&1 | tee /data/users/ltucker/A_thaliana_Taz-0_assembly/logs/5_mercury_log.txt

/data/users/ltucker/A_thaliana_Taz-0_assembly/workflow/6_murmur.rules

snakemake \
  -s /data/users/ltucker/A_thaliana_Taz-0_assembly/workflow/6_mummur.rules \
  --profile /data/users/ltucker/A_thaliana_Taz-0_assembly/slurm \
  -p \
  2>&1 | tee /data/users/ltucker/A_thaliana_Taz-0_assembly/logs/6_mummer_log.txt
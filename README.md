# *Arabidopsis thaliana* Taz-0 Genome Assembly Pipeline

This project implements a comprehensive genome assembly and quality assessment pipeline for the *Arabidopsis thaliana* Taz-0 accession using Snakemake workflow management.

## Background

The sequencing data used in this project comes from two studies that generated high-quality genome assemblies across multiple *Arabidopsis thaliana* accessions:

- **Lian et al. (2024)**: A pan-genome of 69 *Arabidopsis thaliana* accessions reveals a conserved genome structure throughout the global species range. *Nature Genetics* 56:982-991. [DOI: 10.1038/s41588-024-01715-9](https://www.nature.com/articles/s41588-024-01715-9)

- **Jiao & Schneeberger (2020)**: Chromosome-level assemblies of multiple *Arabidopsis* genomes reveal hotspots of rearrangements with altered evolutionary dynamics. *Nature Communications* 11:1–10. [DOI: 10.1038/s41467-020-14779-y](http://dx.doi.org/10.1038/s41467-020-14779-y)

## Project Structure

```
/data/users/ltucker/A_thaliana_Taz-0_assembly
├── input_data/
│   ├── Taz-0/                      # PacBio HiFi DNA reads
│   └── RNAseq_Sha/                 # Illumina RNA-seq reads
├── output/                          # Analysis results (generated)
├── logdir/                          # Snakemake logs (generated)
├── slurm/
│   ├── config.v8+.yaml             # Cluster configuration
│   ├── status-sacct-robust.sh      # SLURM job monitoring
│   └── status-scontrol.sh          # SLURM status checking
├── workflow/
│   ├── 1_quality_control.rules     # Read QC and k-mer analysis
│   ├── 2_all_assemblies.rules      # Genome assembly tools
│   ├── 3_busco.rules               # Gene completeness assessment
│   ├── 4_quast.rules               # Assembly statistics
│   ├── 5_mercury.rules             # K-mer based quality scores
│   └── 6_mummur.rules              # Genome alignments and dotplots
├── main_env.yaml                    # Conda environment specification
└── main.py                          # Pipeline launcher
```

## Workflow Overview

The pipeline consists of six modular workflows that can be run independently or sequentially:

### 1. Quality Control (`1_quality_control.rules`)

Performs comprehensive quality assessment of raw sequencing data:

- **FastQC**: Initial quality metrics for both DNA and RNA reads
- **fastp**: Adapter trimming and quality filtering for RNA-seq data (paired-end reads)
- **Jellyfish**: K-mer counting (k=21) to estimate genome size and heterozygosity from PacBio HiFi reads

The PacBio HiFi reads are evaluated without filtering since they're already high-quality, while RNA-seq reads undergo cleaning before assembly.

### 2. Genome Assembly (`2_all_assemblies.rules`)

Generates genome assemblies using multiple approaches to enable comparison:

- **Flye** (v2.9.5): Long-read assembler optimized for PacBio HiFi data
- **Hifiasm** (v0.25.0): Specialized HiFi assembler producing primary contigs
- **LJA** (v0.2): Alternative long-read assembly algorithm  
- **Trinity** (v2.15.1): De novo transcriptome assembler for RNA-seq data

Each assembler runs with appropriate parameters for the data type (genome vs transcriptome).

### 3. Gene Completeness (`3_busco.rules`)

Evaluates biological completeness using conserved single-copy orthologs:

- Uses the **brassicales_odb10** lineage dataset (appropriate for *A. thaliana*)
- Runs in **genome mode** for DNA assemblies and **transcriptome mode** for Trinity
- Reports complete, fragmented, and missing BUSCOs as a quality indicator

This provides insight into whether the assembly captured the expected gene content.

### 4. Assembly Statistics (`4_quast.rules`)

Computes standard assembly metrics with QUAST:

**With reference genome** (TAIR10):
- Genome fraction covered
- Misassemblies and structural variants
- Gene prediction accuracy using GFF3 annotations

**Without reference**:
- N50, L50, and NG50 values
- Total assembly length  
- Largest contig size
- Number of contigs

Both modes estimate against the 135 Mb *A. thaliana* genome size.

### 5. K-mer Quality Values (`5_mercury.rules`)

Uses Merqury to calculate reference-free quality scores:

- Builds a k-mer database (k=21) from the original reads with **meryl**
- Compares assembly k-mers to read k-mers to compute **QV scores** (similar to Phred scores)
- Generates **completeness statistics** showing what fraction of read k-mers appear in the assembly

Higher QV values indicate fewer errors in the assembly.

### 6. Comparative Alignments (`6_mummur.rules`)

Creates pairwise alignments and dotplots using MUMmer4:

**Assemblies vs Reference**:
- Flye vs TAIR10
- Hifiasm vs TAIR10  
- LJA vs TAIR10

**Assemblies vs Assemblies**:
- Flye vs Hifiasm
- Flye vs LJA
- Hifiasm vs LJA

Dotplots reveal structural differences, rearrangements, and regions of disagreement between assemblies.

## Requirements

### Software Dependencies

The pipeline uses Apptainer/Singularity containers for reproducibility:

- FastQC (v0.12.1)
- fastp (v0.24.1)
- Jellyfish (v2.2.6)
- Flye (v2.9.5)
- Hifiasm (v0.25.0)
- LJA (v0.2)
- Trinity (v2.15.1, loaded as module)
- BUSCO (v5.4.2, loaded as module)
- QUAST (v5.2.0)
- Merqury (v1.3)
- MUMmer4 with gnuplot

### Computational Resources

The pipeline is designed for HPC clusters using SLURM:

- **Memory**: 8-128 GB depending on the step (Hifiasm requires the most at 128 GB)
- **Threads**: 1-24 cores per job
- **Time**: 1 hour to 2 days depending on assembly complexity
- **Storage**: Several hundred GB for intermediate and output files

## Usage

### Running the Pipeline

Execute the main Python script to launch the Snakemake workflow:

```bash
python main.py
```

### Running Individual Workflow Steps

Each workflow module can be run independently by targeting specific output flags:

```bash
# Quality control only
snakemake --snakefile workflow/1_quality_control.rules

# All assemblies
snakemake --snakefile workflow/2_all_assemblies.rules

# BUSCO assessment
snakemake --snakefile workflow/3_busco.rules

# QUAST evaluation
snakemake --snakefile workflow/4_quast.rules

# Merqury QV scores
snakemake --snakefile workflow/5_mercury.rules

# MUMmer comparisons
snakemake --snakefile workflow/6_mummur.rules
```

### SLURM Integration

The pipeline uses cluster configuration files for job submission:

```bash
snakemake --profile slurm/
```

This automatically submits jobs with appropriate resource requests and monitors their status using the provided status scripts.

## Output Organization

All results are written to the `output/` directory with the following structure:

```
output/
├── read_qc/                    # FastQC reports
├── rna_fastp_trimmed/          # Cleaned RNA-seq reads
├── hifi_fastp_stats/           # PacBio read statistics
├── jellyfish/                  # K-mer histograms
├── assemblies/
│   ├── flye/
│   ├── hifiasm/
│   ├── LJA/
│   └── trinity/
├── busco/                      # Completeness reports
├── quast/                      # Assembly statistics
│   ├── with_reference/
│   └── no_reference/
├── merqury/                    # QV scores
│   ├── flye/
│   ├── hifiasm/
│   └── lja/
├── nucmer/                     # Alignment dotplots
│   ├── flye_vs_ref/
│   ├── hifiasm_vs_ref/
│   ├── lja_vs_ref/
│   ├── flye_vs_hifiasm/
│   ├── flye_vs_lja/
│   └── hifiasm_vs_lja/
└── out_flags/                  # Workflow completion markers
```

Flag files in `out_flags/` indicate successful completion of each step.

## Key Features

- **Modular design**: Each workflow module is independent and reusable
- **Multiple assemblers**: Compare results across different assembly algorithms
- **Comprehensive QC**: Both reference-based and reference-free quality metrics
- **Reproducible**: Uses containers and explicit version pinning
- **HPC-ready**: Integrated with SLURM for cluster execution
- **Well-documented**: Inline comments explain parameters and design choices

## Notes

- The RNA-seq data comes from the Sha accession, not Taz-0, but is used for transcriptome assembly practice
- Some rules reference output paths that may need adjustment based on actual assembly output filenames (e.g., Trinity output location)
- The Hifiasm rule uses direct `apptainer exec` calls rather than the container directive due to Snakemake compatibility issues
- Flag files serve as sentinels to track workflow completion and enable proper dependency resolution

---

**Author**: ltucker  
**Project Date**: October 2025

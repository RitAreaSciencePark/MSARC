# MSARC
Code for clustering MSA representations to drive AF2 predictions toward alternative states.

**Step 1**
- Requirements: 
    - localcolabfold 
    - virtual env with: python>3, perl, fair-esm, scikit-learn, pandas, Bio

- Exectution: 
    - sbatch pipeline/1_full_af.sh name_id sequence
    - sbatch pipeline/2_MSA-Transformer_reps_dist.sh
    - sbatch pipeline/3_cluster_AF.sh
    - TO BE DONE: sbatch pipeline/4_results_analysis.sh (avoid gromacs, maybe biopython pdb parser is enough)

- Sanity checks:
    - TO BE DONE compare with dbscan and no_reps/reps clustering
    - TO BE DONE check reps dist varying MSA subsampling

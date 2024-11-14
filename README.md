# MSARC
Code for clustering MSA representations to drive AF2 predictions toward alternative states.

step1 - initial script will take as input from the user tha name of the folder and the sequence, and will generate the standard scaled eculidean distance matrix
step2 - perform the clustering - default will be HAC minimum cluster size=20, give possibilities to adapt parameters and use DBSCAN 

**Step 1**
- Requirements: localcolabfold, python>3, perl
- Exectution: sbatch full_af.sh name_id sequence

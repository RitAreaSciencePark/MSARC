# MSARC
Code for clustering MSA representations to drive AF2 predictions toward alternative states.

- Requirements: 
    - localcolabfold (to install from [localcolabfold-github](https://github.com/YoshitakaMo/localcolabfold))

- Installation:
    - python -m venv conformer
    - source conformer/bin/activate
    - pip install -f requirements.txt 

- Input Format:  
    The input file "input_file_name" must be a txt file containing the list of input ids and sequences in space separated format: "id sequence".
    Example:    
    my_prot1 ABCDEFGH  
    my_prot2 ILMNPQRS

- Exectution: 
    - sbatch launch.sh input_file_name 
    - TO BE DONE: avoid gromacs at last step of pipeline (maybe biopython is enough?)

- Sanity checks:
    - TO BE DONE compare with dbscan and no_reps/reps clustering
    - TO BE DONE check reps dist varying MSA subsampling

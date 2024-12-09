# MSARC
Code for clustering MSA representations to drive AF2 predictions toward alternative states.

- Requirements: 
    - localcolabfold (please follow the installation guidelines: [localcolabfold-github](https://github.com/YoshitakaMo/localcolabfold))

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

- Missing things:
    - TO BE DONE compare with dbscan and no_reps/reps clustering
    - DCA analysis code. !!!!! HELL INSTALLATION
    - Add checks that the input file exists in right path and right format

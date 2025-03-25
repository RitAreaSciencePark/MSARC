# MSARC
Code for clustering MSA representations to drive AF2 predictions toward alternative states.

- Requirements: 
    - localcolabfold (please follow the installation guidelines: [localcolabfold-github](https://github.com/YoshitakaMo/localcolabfold))

Our pipeline was implemented with the followig python version:
$> python3 --version
Python 3.10.12

- Installation:
    - python -m venv conformer
    - source conformer/bin/activate
    - pip install -r requirements.txt 

- Input Format:  
    The input file "input_file_name" must be placed in the input_files folder and it should be a txt file containing the list of input ids and sequences in space separated format: "id sequence".
    Example:
    
    my_prot1 ABCDEFGH  
    my_prot2 ILMNPQRS

- Execution: 
    - sbatch launch.sh input_file_name 


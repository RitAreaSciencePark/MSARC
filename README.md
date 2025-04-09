# MSARC
Code for clustering MSA representations to drive AF2 predictions toward alternative states.

### Requirements: 
    - localcolabfold (please follow the installation guidelines: [localcolabfold-github](https://github.com/YoshitakaMo/localcolabfold))
 
As far as CUDA is concerned, we tested the code with the following configuration

```
$> nvidia-smi | grep CUDA 
| NVIDIA-SMI 530.30.02              Driver Version: 530.30.02    CUDA Version: 12.1     | 
```

Finally, we tested the code with the following python version
```
$> python3 --version
Python 3.10.2 
```

The dependencies are listed in the `requirements.txt` file, obtained with pip freeze in th environement we used to test our code. The general packages needed to run the code are listed in 'packages.txt'.

### Installation:
    - python -m venv conformer
    - source conformer/bin/activate
    - pip install -r packages.txt 

### Input Format:  
    The input file "input_file_name" must be placed in the input_files folder and it should be a txt file containing the list of input ids and sequences in space separated format: "id sequence".
    Example:
    
    my_prot1 ABCDEFGH  
    my_prot2 ILMNPQRS

### Execution on a SLURM queue: 
    - sbatch launch.sh input_file_name 


#!/bin/bash

#SBATCH --partition=DGX
#SBATCH --job-name=MSATrans
#SBATCH --nodes=1
#SBATCH --gpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=50
#SBATCH --mem-per-cpu=2g
#SBATCH --time=12:00:00

source /orfeo/scratch/area/cuturellof/basic/bin/activate

name=$1

input=$name"/sequence_files/msa_split/"
output=$name"/reps_MSATransformer/"
mkdir -p $output

address=$(ip a s | grep -o '10\.128\.6\.[0-9]*' | grep -F -v '.255')

python scripts/data_distributed_inference.py -idir=$input -rdir=$output -n 1 -nr 0 -ip=$address

python scripts/distances.py $name

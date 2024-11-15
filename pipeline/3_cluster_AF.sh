#!/bin/bash

#SBATCH --partition=DGX
#SBATCH --job-name=clustersAF
#SBATCH --nodes=1
#SBATCH --gpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=50
#SBATCH --mem-per-cpu=2g
#SBATCH --time=12:00:00

#source /orfeo/scratch/area/cuturellof/basic/bin/activate
source /u/area/vpiomponi/scratch/env_dgx/bin/activate

name=$1        

python scripts/clustering.py $name

input=$name"/clusters/"
output=$name"/AF_clusters/"
mkdir -p $output


msas=($(ls $input | grep fasta))
for msa in "${msas[@]}"
do
    perl "scripts/reformat.pl" -v 0 -r fas a3m $input$msa $input$msa".a3m"
    name=$(echo $msa | sed 's/.fasta//g')
    colabfold_batch  --amber --num-recycle 3 --num-relax 5 --num-models 5 --use-gpu-relax $input$msa".a3m" $output$name
done

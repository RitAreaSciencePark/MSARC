#!/bin/bash


name_in=$1
name="${name_in%/}"

input="output_files/"$name"/sequence_files/msa_split/"
output="output_files/"$name"/reps_MSATransformer/"
mkdir -p $output

address=$(ip a s | grep -o '10\.128\.6\.[0-9]*' | grep -F -v '.255')

python scripts/data_distributed_inference.py -idir=$input -rdir=$output -n 1 -nr 0 -ip="$address" 

python scripts/distances.py $name 

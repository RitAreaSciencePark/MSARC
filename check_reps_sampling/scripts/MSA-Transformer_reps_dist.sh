#!/bin/bash


name_in=$1
name="${name_in%/}"

address=$(ip a s | grep -o '10\.128\.6\.[0-9]*' | grep -F -v '.255')

input_dir=$name"/msa_splits/"
output_dir=$name"/reps_MSATransformer/"
mkdir -p $output_dir

inputs=($(ls $input_dir))

for input in "${inputs[@]}"
do
	mkdir -p $output_dir$input

	python ../scripts/data_distributed_inference.py -idir=$input_dir$input -rdir=$output_dir$input -n 1 -nr 0 -ip="$address" 

	python scripts/distances.py $name $input

done

#!/bin/sh

#SBATCH --partition=EPYC
#SBATCH --job-name=gmx
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=3g
#SBATCH --time=6:00:00

input_file=$1
proteins=($(cat $input_file | awk '{print $1}'))

for name in "${proteins[@]}"
do

	bash pipeline/4_parse_pdbs_gmx.sh $name
done

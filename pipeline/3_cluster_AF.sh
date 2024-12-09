#!/bin/bash

name_in=$1        
name="${name_in%/}"

input="output_files/"$name"/clusters/"
path_full="output_files/"$name"/AF_full/"
path="output_files/"$name"/AF_clusters/"
output="output_files/"$name"/results/" 

mkdir -p $path
mkdir -p $output

python scripts/clustering.py $name

msas=($(ls $input | grep fasta))
for msa in "${msas[@]}"
do
    name=$(echo $msa | sed 's/.fasta//g')
    perl "scripts/reformat.pl" -v 0 -r fas a3m $input$msa $input$name".a3m"
    colabfold_batch  --amber --num-recycle 3 --num-relax 1 --num-models 5 --use-gpu-relax $input$name".a3m" $path$name
done



awk '{ if ($12 != "H" ) print $0 }' $path_full*_relaxed_rank_001*  > $output"fullMSA_noH.pdb"
for i in $(ls $path | grep -oP 'cluster_\K\d+' | sort -n)
do
        awk '{ if ($12 != "H" ) print $0 }' $path"cluster_$i/cluster_${i}_relaxed_rank_001"* > $output"clus$i.pdb"
done

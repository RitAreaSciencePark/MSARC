#!/bin/bash

name_in=$1        
name="${name_in%/}"

python scripts/clustering.py $name

input=$name"/clusters/"
output=$name"/AF_clusters/"
mkdir -p $output


msas=($(ls $input | grep fasta))
for msa in "${msas[@]}"
do
    name=$(echo $msa | sed 's/.fasta//g')
    perl "scripts/reformat.pl" -v 0 -r fas a3m $input$msa $input$name".a3m"
    colabfold_batch  --amber --num-recycle 3 --num-relax 1 --num-models 5 --use-gpu-relax $input$name".a3m" $output$name
done


path=$name"/AF_clusters" # path_to_input_files (AF pdbs)
output=$name"/output" # output directory
mkdir -p "$output"


awk '{ if ($12 != "H" ) print $0 }' $name/AF_full/*_relaxed_rank_001*  > $output/fullMSA_noH.pdb
for i in $(ls $path | grep -oP 'cluster_\K\d+' | sort -n)
do
        awk '{ if ($12 != "H" ) print $0 }' $path/cluster_$i/cluster_${i}_relaxed_rank_001* > $output/clus$i.pdb
done

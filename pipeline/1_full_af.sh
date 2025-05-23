#!/bin/bash


name_in=$(echo "$1")
name="${name_in%/}"
sequence=$(echo "$2" | tr -cd 'A-Za-z') 

# create input/output directories
seq_dir='output_files/'$name'/sequence_files/'
out_dir='output_files/'$name"/AF_full/"
mkdir -p $out_dir
mkdir -p $seq_dir


# create query sequence
echo ">$name" > $seq_dir'query.fasta'
echo "$sequence"  >> $seq_dir'query.fasta'

# launch ColabFold (AF2) with query sequence
colabfold_batch  --amber --num-recycle 3 --num-relax 5 --num-models 5 --use-gpu-relax --msa-mode mmseqs2_uniref_env $seq_dir'query.fasta' $out_dir

# reformat MSA built in AF2 from a3m to fasta and remove gapped more than 20%
msa_a3m=$(ls $out_dir | grep a3m)
perl "scripts/reformat.pl" -v 0 -r a3m fas $out_dir$msa_a3m $out_dir$name".fasta"  
awk 'BEGIN{FS=""}{if($1==">"){if(NR==1)print $0; else {printf "\n";print $0;}}else printf toupper($0)}' $out_dir$name".fasta" | awk 'BEGIN{FS=""}{if($1==">")name[NR]=$0; else{count=0;for(i=1;i<=NF;i++)if($i=="-")count+=1; if(count/NF<0.2){print name[NR-1]; print $0}}}' > $seq_dir'full_MSA.fasta'

# randomly split MSA to fit in memory for Transformer
python scripts/sample_msa.py $name 



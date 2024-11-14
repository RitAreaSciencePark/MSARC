#!/bin/bash

#SBATCH --partition=DGX
#SBATCH --job-name=af
#SBATCH --nodes=1
#SBATCH --gpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=50
#SBATCH --mem-per-cpu=2g
#SBATCH --time=12:00:00



name=$1
sequence=$2

# create input/output directories
seq_dir=$name'/sequence_files/'
out_dir=$name"/AF_full/"
mkdir -p $out_dir
mkdir -p $seq_dir

# create query sequency
echo ">"$name > $seq_dir'query.fasta'
echo $sequence >> $seq_dir'query.fasta'

# launch ColabFold (AF2) with query sequence
colabfold_batch  --amber --num-recycle 3 --num-relax 5 --num-models 5 --use-gpu-relax --msa-mode mmseqs2_uniref_env $seq_dir'query.fasta' $out_dir

# reformat MSA built in AF2 from a3m to fasta and remove gapped more than 20%
msa_a3m=$(ls $out_dir | grep a3m)
perl "scripts/reformat.pl" -v 0 -r a3m fas $out_dir$msa_a3m $out_dir$name".fasta"  
awk 'BEGIN{FS=""}{if($1==">"){if(NR==1)print $0; else {printf "\n";print $0;}}else printf toupper($0)}' $out_dir$name".fasta" | awk 'BEGIN{FS=""}{if($1==">")name[NR]=$0; else{count=0;for(i=1;i<=NF;i++)if($i=="-")count+=1; if(count/NF<0.2){print name[NR-1]; print $0}}}' > $seq_dir'full_MSA.fasta'

# randomly split MSA to fit in memory for Transformer
python scripts/sample_msa.py $name 



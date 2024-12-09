
if [ "$#" -ne 1 ]; then
	echo "Usage: $0 <name of protein>"
    exit 1
fi

name_in=$1
name="${name_in%/}"
path=$name"/AF_clusters" # path_to_input_files (AF pdbs)
output=$name"/output" # output directory
mkdir -p "$output"


awk '{ if ($12 != "H" ) print $0 }' $name/AF_full/*_relaxed_rank_001*  > $output/fullMSA_noH.pdb
for i in $(ls $path | grep -oP 'cluster_\K\d+' | sort -n)
do
        awk '{ if ($12 != "H" ) print $0 }' $path/cluster_$i/cluster_${i}_relaxed_rank_001* > $output/clus$i.pdb
done

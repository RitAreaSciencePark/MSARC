module use /u/area/vpiomponi/.local/modules/
module load gromacs/2022.5

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 <name of protein>"
    exit 1
fi

name_in=$1
name="${name_in%/}"
path=$name"/AF_clusters" # path_to_input_files (AF pdbs)
output=$name"/gmx_traj" # output directory

mkdir -p "$output"

awk '{ if ($12 != "H" ) print $0 }' $name/AF_full/*_relaxed_rank_001*  > $output/fullMSA_noH.pdb

for i in $(ls $path | grep -oP 'cluster_\K\d+' | sort -n)
do
        awk '{ if ($12 != "H" ) print $0 }' $path/cluster_$i/cluster_${i}_relaxed_rank_001* > clus.pdb
        
	gmx_mpi editconf -f clus.pdb -o clus$i.gro 
	gmx_mpi trjconv -f clus$i.gro -o clus$i.xtc

done

len=$(ls $path | wc -l | awk '{print $1}')
if [ "$len" -gt 100 ]; then
        gmx_mpi trjcat -f clus{?,??,???}.xtc -cat -o $output/traj.xtc
elif [ "$len" -gt 10 ]; then
        gmx_mpi trjcat -f clus{?,??}.xtc -cat -o $output/traj.xtc
else
        gmx_mpi trjcat -f clus?.xtc -cat -o $output/traj.xtc
fi

cp clus1.gro $output/traj.gro

rm *clus*
rm $output/*#traj*



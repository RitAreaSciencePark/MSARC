perl write_mdp.pl md_lam

for i in {0..7}
do
	for j in {0..5}
	do
		k=$((i * 6 + j))
		mkdir lam$k
		gmx_mpi grompp -f md_lam_$k.mdp -c 8replica_equilibration/npt$i.gro -r 8replica_equilibration/npt$i.gro -p topol.top -o lam$k/md.tpr -n index.ndx
	done
done	

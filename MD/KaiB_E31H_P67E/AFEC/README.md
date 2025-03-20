This folder contains all prameter files, topologies, and script needed to reproduce the AFEC simulations.

The starting strucure pmx_p67e.pdb was obtained merging to pdbs:

1 - The WT Ground State of KaiB as predicted by AF2 through clustered MSA (GS.pdb)
2 - a mutant P67E in the Fold-switched state as predicted by AF2 with defaul setting, but shifted by 60 A along the x axis (FS_P67E_shifted.pdb)

Then the hybrid strucutres and topologies were generated in PMX_preparation.ipynb

Solvated Box generated with gmx_preparation_scripts.sh 

Equilibration scripts and parameters are found in the folder 8replica_equilibration 

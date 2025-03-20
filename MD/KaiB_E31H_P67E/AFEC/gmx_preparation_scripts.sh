gmx editconf -f conf.gro -o conf.gro -c -d 2.5 -bt dodecahedron
gmx solvate -cp conf.gro -o conf_solv.gro -p topol.top
gmx grompp -f ions.mdp -c conf_solv.gro -p topol.top -o ions.tpr
gmx genion -s ions.tpr -o conf_solv_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.1

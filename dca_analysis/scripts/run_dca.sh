name=$1
filename="../output_files/"$name"/results/cluster_ids_alternative_state.npy"
clusters=($(python -c "import numpy as np; print(' '.join(map(str, np.load('$filename'))))"))
out_dir="output_files/"$name"/"
mkdir -p $out_dir
in_full="../output_files/"$name"/sequence_files/full_MSA.fasta"
plmdca compute_fn protein $in_full --apc --lambda_h 1.0 --lambda_J 10.0 --verbose --output $out_dir			


for clu in "${clusters[@]}"
do
	clu_msa="../output_files/"$name"/clusters/cluster_"$clu".fasta"

	plmdca compute_fn protein $clu_msa --apc --lambda_h 1.0 --lambda_J 10.0 --verbose --output $out_dir
done
		

name=$1

in_file="output_files/"$name"/results/max_size_alternative_cluster.csv"
if [ -z "$in_file" ];then
	echo "Could not find " $in_file
else
	clu_name=$(awk 'BEGIN{FS=","}{if(NR==2)print $1}' $in_file)
	if [ -z "$clu_name" ];then
		echo "Could not find alternative cluster in file"
	else
		in_full="output_files/"$name"/sequence_files/full_MSA.fasta"
		if [ -z "$in_full" ];then
			echo "Could not find " $in_full
		else
			clu_msa="output_files/"$name"/clusters/"$clu_name".fasta"
			out_dir=$name"/results/"
			mkdir -p $out_dir

			plmdca compute_fn protein $in_full --apc --lambda_h 1.0 --lambda_J 10.0 --verbose --output $out_dir
			plmdca compute_fn protein $clu_msa --apc --lambda_h 1.0 --lambda_J 10.0 --verbose --output $out_dir
		
		fi
	fi
fi

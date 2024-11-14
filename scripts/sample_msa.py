import random
import os
import sys

def parse_fasta(file):
    """Parse a FASTA file into sequence names and sequences."""
    with open(file, 'r') as f:
        lines = f.readlines()

    names = []
    seqs = []
    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            names.append(line)
            seqs.append("")
        else:
            seqs[-1] += line

    return names, seqs

def shuffle_and_split(names, seqs, output_dir, limit=16000):
    """Shuffles sequences and splits them into chunks without exceeding the character limit."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # First sequence is the query (not shuffled)
    query_name = names[0]
    query_seq = seqs[0]
    query_len = len(query_seq)

    # Rest of the sequences
    rest_names = names[1:]
    rest_seqs = seqs[1:]

    # Shuffle the remaining sequences to get a random order
    zipped = list(zip(rest_names, rest_seqs))
    random.shuffle(zipped)
    rest_names, rest_seqs = zip(*zipped)

    # chunk MSA
    chunk_size = int(limit / query_len) - 1
    num_chunks = int(len(rest_seqs)/chunk_size) + 1
    
    for c in range(num_chunks):

        if c < num_chunks-1:
            chunk_names = rest_names[c*chunk_size:(c+1)*chunk_size]
            chunk_seqs = rest_seqs[c*chunk_size:(c+1)*chunk_size]
        else:
            remaining = len(rest_seqs) - (num_chunks-1)*chunk_size
            chunk_names = rest_names[c*chunk_size:(c*chunk_size)+remaining]
            chunk_seqs = rest_seqs[c*chunk_size:(c*chunk_size)+remaining]
        
        # Write the current chunk to a new FASTA file
        with open(f"{output_dir}/msa_{c}.fasta", 'w') as f:
            f.write(f"{query_name}\n{query_seq}\n")
            for name, seq in zip(chunk_names, chunk_seqs):
                f.write(f"{name}\n{seq}\n")
        

def main():
    # Get the input file and output directory from the command-line arguments
    name = str(sys.argv[1])
    input_file = f'{name}/sequence_files/full_MSA.fasta'
    output_dir = f'{name}/sequence_files/msa_split'

    # Parse the MSA file to get names and sequences
    names, seqs = parse_fasta(input_file)

    # Shuffle and split the sequences into chunks
    shuffle_and_split(names, seqs, output_dir)

if __name__ == "__main__":
    main()


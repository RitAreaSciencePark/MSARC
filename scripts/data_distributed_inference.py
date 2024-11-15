import esm
import torch
from torch.utils.data import Dataset, DataLoader

import numpy as np
import pandas as pd
import os
from Bio import SeqIO
import itertools
from typing import List, Tuple
import string
import random
import time
import argparse
import math
import csv

torch.cuda.empty_cache()
torch.set_grad_enabled(False)

deletekeys = dict.fromkeys(string.ascii_lowercase)
deletekeys["."] = None
deletekeys["*"] = None
translation = str.maketrans(deletekeys)

def remove_insertions(sequence: str) -> str:
    return sequence.translate(translation)

def read_msa(filename: str, nseq: int) -> List[Tuple[str, str,str]]:
    records = list(SeqIO.parse(filename, "fasta")) 
    lseq = max([len(records[i].seq) for i in range(len(records))]) 
    
    if lseq > 1024:
        for seq in range(len(records)):
            records[seq] = records[seq][:1023]
            lseq = 1023
      
    nseq = min(int(nseq), len(records)) 
        
    if(nseq*lseq>(16000)): 
        nseq = (16000)//(lseq+1)
    
    idxs = [records[i].id for i in range(nseq)]
    
    pdb_list=[(records[0].description, remove_insertions(str(records[0].seq)))] 
    
    return pdb_list+[(records[i].description, remove_insertions(str(records[i].seq))) for i in range(1,nseq)], nseq, idxs

class MSA_Dataset(Dataset):
    def __init__(self, base_dir, n_seq):
        self.dir = base_dir
        self.nseq = n_seq
        self.filenames = os.listdir(base_dir)

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        msa_name = os.path.join(self.dir, self.filenames[idx])
        msa, n_seq, idxs = read_msa(msa_name, nseq = self.nseq)
        return msa, msa_name, n_seq, idxs

    
class InfiniteDataLoader(torch.utils.data.dataloader.DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, 'batch_sampler', _RepeatSampler(self.batch_sampler))
        self.iterator = super().__iter__()

    def __len__(self):
        return len(self.batch_sampler.sampler)

    def __iter__(self):
        for i in range(len(self)):
            yield next(self.iterator)
            
class _RepeatSampler(object):
    def __init__(self, sampler):
        self.sampler = sampler

    def __iter__(self):
        while True:
            yield from iter(self.sampler)
    
def custom_collate(data):
    output = []
    for seq,name,nseq,idxs in data:
        output.append(seq)
    return output,name,nseq,idxs

def compute_loss(soft,logit,toks):
    s = torch.zeros(1)
    probs = soft(logit)
    for i in range(probs.shape[1]):
        for j in range(probs.shape[2]):
            s+=probs[0,i,j,toks[0,i,j]]
    return s/(probs.shape[1]*probs.shape[2])

def prepare_inference(gpu, args):

    resdir = args.resdir

    rank = args.gpus * args.nr + gpu
    
    if (resdir is not None):
        if not os.path.exists(resdir):
            os.makedirs(resdir,exist_ok='True')
        if not os.path.exists(os.path.join(resdir,'reps')):
            os.makedirs(os.path.join(resdir,'reps'),exist_ok='True')
        if not os.path.exists(os.path.join(resdir,'ids')):
            os.makedirs(os.path.join(resdir,'ids'),exist_ok='True')
    
    torch.distributed.init_process_group(
        backend = "nccl",
        init_method ='tcp://'+args.ip+':8889',
        world_size = args.world_size,
        rank = rank)
    device = f"cuda:{gpu}"

    
    msa_t, msa_alphabet = esm.pretrained.esm_msa1b_t12_100M_UR50S()
    msa_t.to(device)
    msa_t.eval()
    msa_transformer = torch.nn.parallel.DistributedDataParallel(msa_t, device_ids=[gpu])
    msa_batch_converter = msa_alphabet.get_batch_converter()
    
    nseq = args.nseq
    msa_dataset = MSA_Dataset(base_dir = args.inputdir, n_seq = args.nseq )

    msa_sampler = torch.utils.data.distributed.DistributedSampler(msa_dataset, 
                                                                  num_replicas = args.world_size, 
                                                                  rank = rank)

    msa_loader = InfiniteDataLoader(msa_dataset, shuffle = False, 
                                    batch_size = 1, batch_sampler = None, 
                                    num_workers = 1 , sampler = msa_sampler, 
                                    collate_fn = custom_collate, pin_memory = False)
    
    msa_loader_iter = iter(msa_loader)
    
    d_loss = {}

    for i in range(len(msa_loader)):
        msa, filename, nseq, idxs = next(msa_loader_iter)
        fn = filename[filename.find('msa'):]
        print(fn)
                
        try:
            msa_batch_labels, msa_batch_strs, msa_batch_tokens = msa_batch_converter(msa)  
        
        except: 
            falign = open(os.path.join(resdir,"wrong_alignments"+str(rank)), "w")
            falign.write(fn+"\n")
            continue
        
        if (msa_batch_tokens.size()[2] <=1024):
            try:
                name = fn.partition('/')[2]
                print(name)
                
                msa = msa_transformer.forward(msa_batch_tokens, repr_layers=[12], return_contacts=True)
                msa_rep = msa['representations'][12].cpu()
               
                msa_rep_name = os.path.join(resdir,"rep/"+name+".npy")
                msa_rep_np = msa_rep.numpy() 
                np.save(msa_rep_name,  msa_rep_np)
                
                idxs_name = os.path.join(resdir,"ids/"+name+".npy")
                np.save(idxs_name, idxs)
            except:
                  fprob = open(os.path.join(resdir,"problems_inference"+str(rank)), "w")
                  fprob.write(fn+"\n")
        else:
            flong = open(os.path.join(resdir,"too_longMSAS"+str(rank)), "w")
            flong.write(fn+"\n") 



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nodes', default=1, type=int, metavar='N')
    parser.add_argument('-g', '--gpus', default=1, type=int, help='number of gpus per node')
    parser.add_argument('-nr', '--nr', default=0, type=int, help='ranking within the nodes')
    parser.add_argument("-ip", "--ip", default=None, type=str, help="IP of master process")
    parser.add_argument("-ns", "--nseq", default=10**5, type=int, help="number of sequences required")
    parser.add_argument("-rdir", "--resdir", default='MSA-Trans_results', type=str, help="output directory")
    parser.add_argument("-idir", "--inputdir", default='5VBL_MSA', type=str, help="input directory")
    parser.add_argument("-rs", "--randseed", default=1109, type=int, help='selection of random seed')

    args = parser.parse_args()
    
    random.seed(args.randseed)
    
    if args.ip is None:
        if args.nodes == 1:
            args.ip = "127.0.0.1"
        else:
            raise argparse.ArgumentError("If nodes > 1, ip can't be left None")
    
    args.world_size = args.gpus * args.nodes
    torch.multiprocessing.spawn(prepare_inference, nprocs=args.gpus, args = (args,))

    
    

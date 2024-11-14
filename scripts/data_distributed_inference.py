#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import esm

import torch
from torch.utils.data import Dataset, DataLoader

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


#data-preprocessing step
deletekeys = dict.fromkeys(string.ascii_lowercase)
deletekeys["."] = None
deletekeys["*"] = None
translation = str.maketrans(deletekeys)

def remove_insertions(sequence: str) -> str:
    return sequence.translate(translation)

def read_msa(filename: str, nseq: int) -> List[Tuple[str, str,str]]:
    records = list(SeqIO.parse(filename, "fasta")) 
    lseq = max([len(records[i].seq) for i in range(len(records))]) #lenght of longest seq of msa
    
    if lseq > 1024:
        for seq in range(len(records)):
            records[seq] = records[seq][:1023]
            lseq = 1023
      
    nseq = min(int(nseq), len(records)) #select the numb of seq you are interested in
        
    if(nseq*lseq>(16000)): 
        nseq = (16000)//(lseq+1)
#    idx=random.sample(list(range(0,len(records)-1)), nseq-1) #extract nseq-1 idx'''
    
    
    idxs = []
    for i in range(nseq):
        idxs.append(records[i].id)
    
    pdb_list=[(records[0].description, remove_insertions(str(records[0].seq)))] #the first is included always
    
    return pdb_list+[(records[i].description, remove_insertions(str(records[i].seq))) for i in range(1,nseq)], nseq, idxs

class MSA_Dataset(Dataset):
    def __init__(self, base_dir, n_seq):
        ''' 
        Dataset class.
        Args:
            self.dir: directory where the files are found
            nseq: how many sequences for each MSA are selected
            filenames: list of all files located in the directory
        '''
        self.dir = base_dir
        self.nseq = n_seq
        self.filenames = os.listdir(base_dir)

    def __len__(self):
        ''' How many files are present in the directory. '''
        return len(self.filenames)

    def __getitem__(self, idx):
        '''
        Overiding of index operator in order to select a given file from the directory.
        Args:
            msa_name: name of the file 
            msa: selected msa  
            n_seq: how many sequences have been selected 
        '''
        msa_name = os.path.join(self.dir, self.filenames[idx])
        msa, n_seq, idxs = read_msa(msa_name, nseq = self.nseq)
        return msa, msa_name, n_seq, idxs

    
class InfiniteDataLoader(torch.utils.data.dataloader.DataLoader):
    '''
    Dataloader that reuses workers.
    Uses same syntax as vanilla DataLoader.
    '''
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
    ''' 
    Sampler that repeats forever. 
    Args:
        sampler (Sampler)
    '''
    def __init__(self, sampler):
        self.sampler = sampler

    def __iter__(self):
        while True:
            yield from iter(self.sampler)
    

#customized collate function 
def custom_collate(data):
    output = []
    for seq,name,nseq,idxs in data:
        output.append(seq)
    return output,name,nseq,idxs

#function for computing the loss
def compute_loss(soft,logit,toks):
    s = torch.zeros(1)
    probs = soft(logit)
    for i in range(probs.shape[1]):
        for j in range(probs.shape[2]):
            s+=probs[0,i,j,toks[0,i,j]]
    return s/(probs.shape[1]*probs.shape[2])

#main function that perform inference 
def prepare_inference(gpu, args):

    ''' Set the directories for saving the files that produce error '''
    resdir = args.resdir

    ''' Define the rank '''
    rank = args.gpus * args.nr + gpu
    
    if (resdir is not None):
        if not os.path.exists(resdir):
            os.makedirs(resdir,exist_ok='True')
        if not os.path.exists(os.path.join(resdir,'rep')):
            os.makedirs(os.path.join(resdir,'rep'),exist_ok='True')
        if not os.path.exists(os.path.join(resdir,'score')):
            os.makedirs(os.path.join(resdir,'score'),exist_ok='True')
        if not os.path.exists(os.path.join(resdir,'ids')):
            os.makedirs(os.path.join(resdir,'ids'),exist_ok='True')
        
        fprob = open(os.path.join(resdir,"probinferMSAS"+str(rank)), "w")
        flong = open(os.path.join(resdir,"longMSAS"+str(rank)), "w")
        falign = open(os.path.join(resdir,"wrongalignMSAS"+str(rank)), "w")
    
    ''' Initiate the process '''
    torch.distributed.init_process_group(
        backend = "nccl",
        init_method ='tcp://'+args.ip+':8889',
        world_size = args.world_size,
        rank = rank)
    device = f"cuda:{gpu}"

    ''' Initialize the pre-trained transformer '''
    msa_t, msa_alphabet = esm.pretrained.esm_msa1b_t12_100M_UR50S()
    msa_t.to(device)
    msa_t.eval()
    msa_transformer = torch.nn.parallel.DistributedDataParallel(msa_t, device_ids=[gpu])
    msa_batch_converter = msa_alphabet.get_batch_converter()
    
    nseq = args.nseq
    ''' Select the Dataset '''
    msa_dataset = MSA_Dataset(base_dir = args.inputdir, n_seq = args.nseq )

    ''' 
    Define the DistributedSampler: 
    it creates a list of different indeces sorted without replacement for each of the rank  
    '''
    msa_sampler = torch.utils.data.distributed.DistributedSampler(msa_dataset, 
                                                                  num_replicas = args.world_size, 
                                                                  rank = rank)

    ''' 
    ut_list)
    Define the DataLoader:
    based on the indeces obtained by the msa_sampler, it selects the msa from the dataset and store them 
    in a tensor
    '''
    msa_loader = InfiniteDataLoader(msa_dataset, shuffle = False, 
                                    batch_size = 1, batch_sampler = None, 
                                    num_workers = 1 , sampler = msa_sampler, 
                                    collate_fn = custom_collate, pin_memory = False)
    
    ''' Define an iterator over the selected msa '''
    msa_loader_iter = iter(msa_loader)
    
    d_loss = {}
    
    ''' 
    For each msa perform inference and save in dedicated file the contacts, the final layer representaton and 
    the loss. 
    If during one of the steps an error is raised, the name of the given msa is written in the respective 
    error file. 
    Both contacts and representation are saved as .npy object.  
    '''

    for i in range(len(msa_loader)):
        msa, filename, nseq, idxs = next(msa_loader_iter)
        fn = filename[filename.find('msa'):]
        print(fn)
                
        try:
            msa_batch_labels, msa_batch_strs, msa_batch_tokens = msa_batch_converter(msa)  
        
        except: 
            falign.write(fn+"\n")
            continue
        
        if (msa_batch_tokens.size()[2] <=1024):
            try:
                msa = msa_transformer.forward(msa_batch_tokens, repr_layers=[12], return_contacts=True)
 #               msa_contact = msa['contacts'].cpu()
                msa_rep = msa['representations'][12].cpu()
                '''
                soft = torch.nn.Softmax(dim = 3)
                logit = msa["logits"].cpu()
                loss = compute_loss(soft,logit,msa_batch_tokens)
                d_loss[fn] = loss'''
               
                name = fn.partition('/')[2]
                print(name)
               # msa_shape_rep = msa_rep.shape[1:]
                msa_rep_name = os.path.join(resdir,"rep/"+name+".npy")
                msa_rep_np = msa_rep.numpy() #.reshape(msa_shape_rep)
                np.save(msa_rep_name,  msa_rep_np)
                '''                
                msa_shape_res = msa_contact.shape[1:]
                msa_res_name = os.path.join(resdir,"score/scores_"+fn+".npy")
                msa_contact_matrix = msa_contact.numpy().reshape(msa_shape_res)
                np.save(msa_res_name, msa_contact_matrix)'''
                
                idxs_name = os.path.join(resdir,"ids/"+name+".npy")
                np.save(idxs_name, idxs)
            except:
                  fprob.write(fn+"\n")
        else:
            print(fn)
            flong.write(fn+"\n") 

#    with open(os.path.join(resdir,'loss'+str(rank)+'.csv'), 'w') as f:
#        for filename in d_loss.keys():
#            f.write("%s,%s\n"%(filename, d_loss[filename]))
            


if __name__ == "__main__":
    print('start')
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

    
    
    


    
    

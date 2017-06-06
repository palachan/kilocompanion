# -*- coding: utf-8 -*-
"""
Created on Sun May 28 12:40:09 2017

map_ntt_file taken in part from http://nedlom.blogspot.com/2013/02/how-to-read-neuralynx-ntt-files-with.html
otherwise,
@author: Patrick
"""
import numpy as np 
import os
import tkFileDialog
from shutil import copyfile


def mmap_spike_file(filename): 
    """ Memory map the Neuralynx .ntt file """ 
    
    #Are we working with tetrodes or stereotrodes?
    if filename.endswith(".ntt"):
        wires = 4
    elif filename.endswith(".nst"):
        wires = 2
    #specify the NTT datatypes
    ntt_dtype = np.dtype([ 
        ('timestamp'  , '<u8'), 
        ('sc_number'  , '<u4'), 
        ('cell_number', '<u4'), 
        ('params'     , '<u4',   (8,)), 
        ('waveforms'  , '<i2', (32,wires)), 
    ]) 
    #memmap the file
    mmap = np.memmap(filename, dtype=ntt_dtype, mode='r+', 
       offset=(16 * 2**10))
    #transpose the waveform array into a useful shape
    x = mmap['waveforms'].transpose((2,0,1))
    #break the waveform array into samples from each wire
    for l in x:
        #flatten the new arrays and assign them to list 'mmaps'
        mmaps.append(l.flatten())
        
    return mmaps, wires,l,x
       
def compile_data(mmaps):
    """ Make memmap waveforms into one long list """
    
    #make a list to count number of samples per waveform array
    numsamps = []
    #count number of samples per array
    for i in range(len(mmaps)):
        numsamps.append(len(mmaps[i]))
    #add fake data (mean of each array) to end of waveform arrays to make them
    #all the length of the longest array
    for i in range(len(mmaps)):
        mmaps[i] = np.pad(mmaps[i],(0,max(numsamps)-len(mmaps[i])),mode='mean')
    #stack 'em up
    mmaps = np.column_stack(mmaps)
    #break 'em down
    continuous = mmaps.flatten()          
    
    return continuous,mmaps
    
def write_bin(cont,filename):
    """ write long waveform array to file """
    #get a file ready
    fid =open(bin_file,'wb')
    #write it!
    cont[0].tofile(fid)
       
if __name__ == '__main__':
    #which folder has the spike files? **Change initialdir to appropriate directory
    fdir = tkFileDialog.askdirectory(initialdir='\\\\tsclient\\C\\Users\\Jeffrey Taube\\Desktop\\Patrick\\')
    #get some files and folders ready
    bin_file = fdir + "/data.bin"
    sffolder = fdir + "/kilosorted_spikefiles"
    tsfolder = fdir + "/kilosorted_tsfiles"
    if not os.path.exists(sffolder):
        os.makedirs(sffolder)
    if not os.path.exists(tsfolder):
        os.makedirs(tsfolder)
    #make a list of spike files in directory
    spike_files = []
    for file in os.listdir(fdir):
        if file.endswith(".ntt") or file.endswith(".nst"):
            #copy the spike files to new 'kilosorted_spikefiles' directory for
            #future editing
            copyfile(fdir + '/' + file, sffolder+'/' + file)
            #save the names of the spike files
            spike_files.append(sffolder + '/' + file)
    #make a list for memory maps
    mmaps = []
    #memmap the spike files
    for i in range(len(spike_files)):
        print('Processing %s' % spike_files[i])
        mmaps,wires,l,x = mmap_spike_file(spike_files[i])
    #compile the date into one long list
    print('Compiling data')
    cont = compile_data(mmaps)
    print('Writing binary file')
    #write the binary file
    write_bin(cont,bin_file)


        


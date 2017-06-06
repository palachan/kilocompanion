# -*- coding: utf-8 -*-
"""
Created on Mon May 29 10:21:25 2017

@author: Patrick (except mmap_spike_file, from http://nedlom.blogspot.com/2013/02/how-to-read-neuralynx-ntt-files-with.html)
"""

def mmap_spike_file(filename,mmap_mode): 
    """ Memory map the Neuralynx .ntt file """ 
          
    #defines datatypes within NTT and NST files
    ntt_dtype = np.dtype([ 
        ('timestamp'  , '<u8'), 
        ('sc_number'  , '<u4'), 
        ('cell_number', '<u4'), 
        ('params'     , '<u4',   (8,)), 
        ('waveforms'  , '<i2', (32,wires)), 
    ]) 

    #memory map the spike file
    mmap = np.memmap(filename, dtype=ntt_dtype, mode=mmap_mode, offset=(16 * 2**10))

    return mmap

def get_channels(templates):
    """ Figure out which channel each cluster belongs to """
    
    #start a list for channels for each cluster
    clustchannels = []
    #make the templates file into a useful shape
    x = templates.transpose((0,2,1))
    #for every template
    for i in range(len(x)):
        amps = []
        #find the amplitude of the template on each wire
        for j in range(len(x[i])):
            amps.append(max(x[i][j])-min(x[i][j]))
        #assign the wire with the highest amplitude to the cluster
        channel = amps.index(max(amps))
        #add it to the list
        clustchannels.append(channel)
    
    return clustchannels
    
def write_ntt(spike_times,spike_clusters,clustchannels,sffolder):
    """ Write cluster IDs to a new spike file """
    
    #start a dict for spike data and list for spike indices
    data = {}
    spike_inds = []
    
    #for every spike time in spike_times file
    for i in range(len(spike_times)):
        #assign to an index corresponding to one 32-sample chunk
        spike_inds.append(spike_times[i]/32)
        #add the indices to the corresponding key in data dict
        #(one key for each cluster in spike_clusters)
        if '{}'.format(int(spike_clusters[i])) in data:
            data['{}'.format(int(spike_clusters[i]))].append(int(spike_inds[i]))
        else:
            data['{}'.format(int(spike_clusters[i]))] = []
            data['{}'.format(int(spike_clusters[i]))].append(int(spike_inds[i]))
            
    #start some dicts for NTT files and SS3D cluster numbers
    ntts = {}
    trodeclusts = {}
    
    #for each copied NTT file in 'kilosorted_spikefiles' folder
    for file in os.listdir(sffolder):
        #memmap the file
        ntts['{}'.format(file)] = mmap_spike_file(sffolder+'/'+file,'r+')
        #start a new entry in 'trodeclusts'
        trodeclusts['{}'.format(file)] = 0

    #for every cluster
    for key in data:
        #start a list for timestamps
        spike_timestamps = []
        #figure out which channel it is
        channel = clustchannels[int(key)-1]

        #figure out which NTT file we need to edit
        if wires == 2:
            trode = channel/2 + 1
            trodefile = 'ST'+str(trode)+'.nst'
        elif wires == 4:
            trode = channel/4 + 1
            trodefile = 'TT'+str(trode)+'.ntt'
        print('Editing ' + trodefile)
        
        #increment the SS3D cluster number
        trodeclusts[trodefile] += 1
        #for every spike index in data dict
        for index in data[key]:
            if index < len(ntts[trodefile]):
                #assign the cluster number to the spike in the NTT file
                ntts[trodefile][index]['cell_number'] = trodeclusts[trodefile]
                #add timestamp to 'spike_timestamps' list
                spike_timestamps.append(ntts[trodefile][index]['timestamp'])
        #make a timestamp file for the cluster, save in 'kilosorted_tsfiles'
        ts_file = open(tsfolder + '/' + trodefile[:len(trodefile)-4]+'_C'+str(trodeclusts[trodefile])+'.txt', 'w')
        for ts in spike_timestamps:
            ts_file.write("%s\n" % ts)
    #flush the NTT data to disk
    for key in ntts:    
        ntts[key].flush()
    #close the NTT files
    del ntts

    return data,spike_inds,trodeclusts
        
############################################################
if __name__ == '__main__':
    #import appropriate files from kilosort
    spike_times = np.load(fdir+'/kilofiles/spike_times.npy', mmap_mode='r')
    spike_clusters = np.load(fdir+'/kilofiles/spike_clusters.npy', mmap_mode='r')
    templates = np.load(fdir+'/kilofiles/templates.npy', mmap_mode='r')
    #figure out which channel corresponds to which cluster
    clustchannels=get_channels(templates)
    #write the cluster IDs into the NTT files
    data,spike_inds,trodeclusts = write_ntt(spike_times,spike_clusters,clustchannels,sffolder)

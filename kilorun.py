# -*- coding: utf-8 -*-
"""
Created on Mon May 29 13:25:33 2017

@author: Patrick
"""

import matlab.engine


############################################################
if __name__ == '__main__':
    execfile('ntt2bin.py')
    eng = matlab.engine.start_matlab()
    eng.run_kilosort(bin_file,wires,fdir)
    execfile('kilo2ntt.py')
    
    
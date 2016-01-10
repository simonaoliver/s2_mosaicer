__author__ = 'simonaoliver'

# coding: utf-8

import sys
import subprocess
import os
import shutil
import zipfile
import uuid

input_path = os.path.normpath('/g/data/fj7/MSI/Sentinel-2/L1C/2015-12')
outpath =os.path.normpath('/short/v10/sao547/tmp/s2overview')
ziplist=[]
# List the the zip archives
os.path.walk
print "Creating zip list"
count = 0
for r,d,f in os.walk(input_path):
    for files in f:
        if files.endswith('zip'):

            zf = zipfile.ZipFile(input_path+'/'+files,'r')
            ziplist.append(os.path.join(input_path,files))
	    print len(ziplist)
	    if (len(ziplist)==5):
	        print ziplist 
		uid=uuid.uuid4()
                #make a folder and write symbolic links for all of the files
		if not os.path.exists(os.path.join(outpath,str(uid))):
		    print uid
                    uidpath=os.path.join(outpath,str(uid))
                    os.makedirs(uidpath)
                for zips in ziplist:
                    if not os.path.exists(os.path.join(uidpath,os.path.basename(zips))):
		        os.symlink(zips,os.path.join(uidpath,os.path.basename(zips)))
                    print "Zips",zips
		    print "outpath",os.path.join(uidpath,os.path.basename(uidpath))
		ziplist=[]
                f = open(os.path.join(uidpath,'s2_pbs.sh'),'w')
		f.write('# Write shell script here and execute PBS job')
		f.write('#!/bin/bash')
		f.write('#PBS -P v10')
		f.write('#PBS -q express')
		f.write('#PBS -l walltime=5:00:00,ncpus=1,mem=16GB')
		f.write('#PBS -joe -o pbs.olog')

		f.write('module load proj/4.8.0')
		f.write('module load gdal/1.9.2')
		f.write('module load python/2.7.6')
		f.write('export LD_LIBRARY_PATH=/g/data/v10/projects/libjasper:$LD_LIBRARY_PATH')
		f.write('python /home/547/sao547/scripts/s2overview.py /g/data/fj7/MSI/Sentinel-2/L1C/2015-12 0 /short/v10/sao547/tmp/s2overview GTiff tif EPSG:4326 0.0025 B04.jp2 B03.jp2 B02.jp2')
                f.close() 

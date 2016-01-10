#!/bin/bash
#PBS -P v10
#PBS -q express
#PBS -l walltime=5:00:00,ncpus=1,mem=16GB
#PBS -joe -o pbs.olog

module load proj/4.8.0
module load gdal/1.9.2 
module load python/2.7.6
export LD_LIBRARY_PATH=/g/data/v10/projects/libjasper:$LD_LIBRARY_PATH
#python /home/547/sao547/scripts/s2overview.py /g/data/fj7/MSI/Sentinel-2/L1C/2015-12 0 /short/v10/sao547/tmp/s2overview GTiff tif EPSG:3577 250 B04.jp2 B03.jp2 B02.jp2
python /home/547/sao547/scripts/s2overview.py /g/data/fj7/MSI/Sentinel-2/L1C/2015-12 0 /short/v10/sao547/tmp/s2overview GTiff tif EPSG:4326 0.0025 B04.jp2 B03.jp2 B02.jp2

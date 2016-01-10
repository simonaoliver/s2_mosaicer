__author__ = 'simonaoliver'

# coding: utf-8

from osgeo import gdal,osr
from gdalconst import *
import sys
import subprocess
import os
import zipfile
import shutil
import datetime


if len(sys.argv)<8:
        print "*----------------------------------------------------------------*"
        print ""
        print " vrt_mosaic.py creates colour mosaic from input scenes"
        print ""
        print "*----------------------------------------------------------------*"
        print ""
        print " usage: vrt_mosaic.py <input path> <input null> <output path>"
        print "        <out format>"
        print " <files to mosaic like B02.jp2 B03.jp2 B08.jp2"
        print ""
        print " example: s2_zip_mosaicer.py /home/simonaoliver/data/zip -9999"
        print "          /home/simonaoliver/data/tmp GTiff tif EPSG:3577 250"
        print "          B04.jp2 B03.jp2 B02.jp2"
        print "*----------------------------------------------------------------*"

# Read arguments

input_path = sys.argv[1]
null = sys.argv[2]
outpath =os.path.normpath(sys.argv[3])
outformat =sys.argv[4]
extension =sys.argv[5]
outepsg=sys.argv[6]
outres =sys.argv[7]

starttime=datetime.datetime.now()

# List the the zip archives
os.path.walk
for r,d,f in os.walk(input_path):
    for files in f:
        if files.endswith('zip'):
            zf = zipfile.ZipFile(input_path+'/'+files,'r')

            # List to hold bands to mosaic
            mosaic_bands=[]
            if len(sys.argv)>=8:
                for i in range(len(sys.argv)):
                    if i>=8:
                        print("searching for band",sys.argv[i])
                        mosaic_bands.append(sys.argv[i])

            # Unzip the required bands from the zip archive to output directory
            ziplist=[]
            for info in zf.filelist:
                for i in mosaic_bands:
                    if i in info.filename:
                        print(info.filename)
                        if os.path.exists(os.path.join(outpath,info.filename)):
                            print('This folder exists:',os.path.join(outpath,info.filepath))
                        else:
                            zf.extract(info.filename, outpath)
                            ziplist.append(info.filename)
            zipfilename=(str.split(files,'.'))[0]
            unzipped=os.path.join(outpath,zipfilename)
            print(unzipped)

            # Create an output folder to house the warped imagery for each zip archive

            if not os.path.exists(os.path.join(outpath,zipfilename+'_'+str.replace(outepsg,':',''))):
                os.makedirs(os.path.join(outpath,zipfilename+'_'+str.replace(outepsg,':','')))
            else:
                print('This folder exists:',os.path.join(outpath,zipfilename+'_'+str.replace(outepsg,':','')))
                shutil.rmtree(unzipped+'.SAFE')
                sys.exit(0)

            # Create lists to hold working files
            vrt_band=[]
            proj_list=[]
            print("We have this many mosaic bands to create:", len(mosaic_bands))

            # For the extracted mosaic bands, list and create list of input files for band specific VRTs
            for j, value in enumerate(mosaic_bands):
                print(value)

                # List the like bands and create a VRT for a single band
                # Determine which projections are used
                #file = open(filelist, "w")
                for r,d,f in os.walk(outpath):
                    for files in f:
                        if files.endswith(mosaic_bands[j]):
                            image_path = os.path.join(r,files)
                            print(image_path)
                            ds = gdal.Open(image_path)

                            proj_ref = ds.GetProjectionRef()

                            # Write to a projection specific VRT for each mosaic band

                            proj_srs=osr.SpatialReference()
                            proj_srs.ImportFromWkt(proj_ref)
                            projcs = (proj_srs.GetAttrValue('PROJCS').replace(" ","")).replace("/","_")

                            filelist = os.path.join(outpath,"filelist_"+projcs+mosaic_bands[j]+".txt")
                            file = open(filelist, "a")
                            file.writelines(image_path+"\n")

                            # List the different projection systems in the data source
                            # we'll loop through this later and create the appropriate number of output files

                            if projcs in proj_list:
                                print(projcs,"found in list")
                            else:
                                proj_list.append(projcs)

                            file.close() #

            # In[5]:

            # Build the RGB Virtual Raster at full resolution

            for k in proj_list:
                print("Processing this PROG_CS:",k)
                for l, value in enumerate(mosaic_bands):
                    print("Processing:",mosaic_bands[l])
                    vrtband = os.path.join(outpath,mosaic_bands[l]+"_"+k+zipfilename+".vrt")
                    filelist = os.path.join(outpath,"filelist_"+k+mosaic_bands[l]+".txt")

                    print("gdalbuildvrt", "-input_file_list", filelist, "-overwrite", "-srcnodata", null, vrtband)
                    subprocess.call(["gdalbuildvrt", "-input_file_list", filelist, "-overwrite", "-srcnodata", str(null), vrtband])
                    os.remove(filelist)

                print("Completed per band vrt creation")
                # Group bands to single file vrt for warping
                groupedvrt=os.path.join(outpath,k+zipfilename+"_grouped.vrt")
                print("gdalbuildvrt", "-separate", groupedvrt, os.path.join(outpath,"*.vrt"))
                subprocess.call(["gdalbuildvrt", "-separate", groupedvrt, os.path.join(outpath,mosaic_bands[0]+"_"+k+zipfilename+".vrt"),os.path.join(outpath,mosaic_bands[1]+"_"+k+zipfilename+".vrt"),os.path.join(outpath,mosaic_bands[2]+"_"+k+zipfilename+".vrt")])

                # Subsample imagery in source projection for faster warping...test if this is the case
                #groupedscaledimg= os.path.join(outpath,zipfilename+"_"+k+"_grouped_scaled."+extension)
                #print("gdalwarp", "-tr",outres,outres,"-of",outformat,groupedvrt, groupedscaledimg)
                #subprocess.call(["gdalwarp", "-tr",outres,outres,"-of",outformat,groupedvrt, groupedscaledimg])

                # Warp to output projection
                #outband = os.path.join(outpath,zipfilename+"_"+k+"."+extension)
                outband = os.path.join(outpath,zipfilename+'_'+str.replace(outepsg,':',''),zipfilename+"_"+k+"."+extension)
                print outband
                #print("gdalwarp", "-t_srs",outepsg,"-tr",outres,outres,"-of", outformat, "-tap", groupedscaledimg, outband)
                #subprocess.call(["gdalwarp", "-t_srs",outepsg,"-tr",outres,outres,"-of", outformat, "-tap", groupedscaledimg, outband])
                subprocess.call(["gdalwarp", "-t_srs",outepsg,"-tr",outres,outres,"-of", outformat, "-tap", groupedvrt, outband])


                # clean up temporary files
                #os.remove(groupedscaledimg)

            # clean up more temporary files
            shutil.rmtree(unzipped+'.SAFE')
            filelist = [ f for f in os.listdir(outpath) if f.endswith(".vrt") ]
            for f in filelist:
                os.remove(os.path.join(outpath,f))
endtime= datetime.datetime.now()
elapsedtime=endtime-starttime
print(starttime,endtime,elapsedtime.seconds)




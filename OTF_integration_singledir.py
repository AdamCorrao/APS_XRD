'''
Automated integration of 2D images to 1D patterns using pyFAI.
This version assumes all images are in one directory and places all integrated patterns
into a single "XY" directory, another version will be added for better managed filepath / directory naming.
Notes to user:
-provide calibration (.poni) and edge / beamstop mask (.tif)
-define integration method, X units, number of azimuthal points, etc. in first block of code
-lines2skip is to remove metadata in pyFAI generated files which is currently 23 
Written by Adam A. Corrao: October, 2021.
Last edited: June 28th, 2022
'''
import fabio
import pyFAI
import os
import pandas as pd
import numpy as np
############################################ EDIT BELOW HERE FOR INT PRMS ############################################################

maindir = os.path.join('Y:',os.sep,'data','2022-2','KhalifahJun2022') #maind directory where .tif files are saved
xy_dir = os.path.join('Y:',os.sep,'data','2022-2','KhalifahJun2022','XY') #directory where all integrated images should be saved
os.chdir(maindir)

calib_dir = os.path.join('Y:',os.sep,'data','2022-2','KhalifahJun2022','calib') #location of calibration files
ponif = 'Si_640f_14rings.poni' #.poni file name, must be in calib_dir
maskf = 'beamstop_edge_block_mask.tif' # must save mask as a tiff to open with fabio, as an array, or convert file to an array properly - save in calib_dir
static_mask = fabio.open(calib_dir + os.sep + maskf).data

intmethod = 'Full' # full pixel splitting method, change as needed - defaults to CSR
xunit = '2th_deg' # integrates images to 2theta space, change as needed: q_nm^-1 , q_A^-1, 2th_rad, d*2_A^-2, etc.
npoints = int(15000) # number of radial points to integrate 2D image over
#azim_points = int(360) # number of azimuthal points to integrate 2D image over, defaults to 360 so not used
neg_mask = float(-1e-10) # automask pixels in 2D image below this value (all negative pixels)
errormodel = 'None' # no error model used, change to 'poisson' for variance = I or 'azimuthal' for variance=(I - <I>)^2
lines2skip = int(23) # number of lines to skip in pyfai generated .xy file - these contain int / calib info
############################# below here is integration ############################################
ai = pyFAI.load(calib_dir + os.sep + ponif)

tfiles = [] #list of all .tif files
xyfiles = [] #list of all xy files generated
intme = [] #list of files to be integrated, updated on every loop to not repeat integrations

n = 1 #for logic to keep while loop running until quit by user
counter = 0

while n < 11:
    counter = counter + 1
    print('Searching for new tiffs\n')
    for file in os.listdir(maindir):
        if file.endswith('.tif'):
            if file in tfiles:
                continue
            if file not in tfiles:
                print(file,' not in tiff list, adding now\n')
                tfiles.append(file)

    for file in tfiles:
        if file not in xyfiles:
            intme.append(file)

    print('Integrating new tiffs, total: ',(len(intme)),'\n')
    time.sleep(3) #time to make sure all tiffs are properly saved before trying to open

    for file in intme:
        darksub_img = fabio.open(maindir + os.sep + file).data
        xy_name = xy_dir + os.sep + file.replace('.tif','.xy')
        ai.integrate1d(data=darksub_img,mask=static_mask,dummy=neg_mask,method=intmethod,npt=npoints,error_model=errormodel,filename=xy_name,correctSolidAngle=False,unit=xunit)
        xy_f = pd.read_csv(xy_name,skiprows=lines2skip,delim_whitespace=True,header=None)
        xy_f.columns = ['X','Y']
        xy_f.to_csv(xy_name,index=False,float_format='%.8f',sep='\t')
        xyfiles.append(file)
    if len(intme) == 0:
        print('Nothing to integrate on loop: ',counter,'\n')
    if len(intme) > 0:
        print('Done integrating for loop number ',counter,'\n')
    intme = []
    print('Total number of tiff images: ',len(tfiles),'\n')
    print('Total number of xy files: ',len(xyfiles),'\n')
    time.sleep(5) #Time to read print statements from integration loop
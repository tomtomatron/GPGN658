from rsf.proj import *
import wplot
import fdmod 
import rsf.api as rsf
import sys, pylab
import math
import random
import wplot
import pyr


# Run motion magnification (MM) on MP4 video 
# (RGB only)
#
# Inputs:
#   Fv_mp4 - absolute path and file name to input video file 
#   par    - motion magnification parameter dictionary
#
# Outputs:
#   More files than you can shake a stick at.
# 
# This version has following features
#  1.) Whatever happens in pyr.motionmag() happens here 
#  2.) Runs MM on 3 bands in input video
def motionmag_v1(Fv_mp4,par):

  # decompose video into bands
  Fb1 ="b1" # blue
  Fb2 ="b2" # green 
  Fb3 ="b3" # red 
  Fb1w=Fb1+'_w'
  Fb2w=Fb2+'_w'
  Fb3w=Fb3+'_w'
  Flow([Fb1,Fb2,Fb3],'video2rsf.x','./video2rsf.x '+Fv_mp4+
                                   ''' verb=n
                                       band1=${TARGETS[0]} 
                                       band2=${TARGETS[1]} 
                                       band3=${TARGETS[2]}
                                       norm=y
                                   ''')
  

  # window for now
  par['ox']=par['wox']
  par['oz']=par['woz']
  par['ot']=par['wot']
  par['nx']=par['wnx']
  par['nz']=par['wnz']
  par['nt']=par['wnt']
  Flow(Fb1w,Fb1,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d'%par) 
  Flow(Fb2w,Fb2,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d'%par) 
  Flow(Fb3w,Fb3,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d'%par) 

  # save results for level 0
  pyr.plot_level_cube(Fb1w,dict(),'','movie=3 title="band 1"')
  pyr.plot_level_cube(Fb2w,dict(),'','movie=3 title="band 2"')
  pyr.plot_level_cube(Fb3w,dict(),'','movie=3 title="band 3"')

  # set 'em up
  par['fs_Hz'] =1.0/par['dt']

  # perform motion magnification on various videos here
  Fb1m =Fb1w+'_mm'   
  Fb2m =Fb2w+'_mm'  
  Fb3m =Fb3w+'_mm'   
  pyr.motionmag(Fb1m,Fb1w,par) 
  pyr.motionmag(Fb2m,Fb2w,par) 
  pyr.motionmag(Fb3m,Fb3w,par) 
  pyr.plot_level_cube(Fb1m,dict(),'','movie=3 title="band 1: motion magnified"')
  pyr.plot_level_cube(Fb2m,dict(),'','movie=3 title="band 2: motion magnified"')
  pyr.plot_level_cube(Fb3m,dict(),'','movie=3 title="band 3: motion magnified"')

  # window a single pixel out of band 1 to take a look
  Flow('pixel1'      ,'b1_w'   ,'window n1=1 n2=1 n3=256 f1=0 f2=0 f3=0')
  Flow('pixel1_mm'   ,'b1_w_mm','window n1=1 n2=1 n3=256 f1=0 f2=0 f3=0')
  Flow('pixel1_fft'   ,'pixel1'   ,'fft1 | put label1=frequency unit1=Hz label2=amplitude ')
  Flow('pixel1_mm_fft','pixel1_mm','fft1 | put label1=frequency unit1=Hz label2=amplitude ')
  Plot('pixel1'       ,'graph')
  Plot('pixel1_mm'    ,'graph')
  Plot('pixel1_fft'   ,'cabs | graph')
  Plot('pixel1_mm_fft','cabs | graph')

  # end of motionmag_v1()

# Run motion magnification (MM) on MP4 video 
# (RGB and greyscale)
#
# Inputs:
#   Fv_mp4 - absolute path and file name to input video file 
#   par    - motion magnification parameter dictionary
#
# Outputs:
#   More files than you can shake a stick at.
# 
# This version has following features
#  1.) Whatever happens in pyr.motionmag() happens here 
#  2.) Runs MM on 3 bands in input video
def motionmag_v2(Fv_mp4,par):

  # decompose video into bands
  Fb1 ="b1" # blue
  Fb2 ="b2" # green 
  Fb3 ="b3" # red 
  Fg  ="grey"
  Flow([Fb1,Fb2,Fb3],'video2rsf.x','./video2rsf.x '+Fv_mp4+
                                   ''' verb=n
                                       band1=${TARGETS[0]} 
                                       band2=${TARGETS[1]} 
                                       band3=${TARGETS[2]}
                                       norm=y
                                   ''')
  # derive greyscale 
  Flow(Fg,[Fb3,Fb2,Fb1],'''
                                math
                                r=${SOURCES[0]} g=${SOURCES[1]} b=${SOURCES[2]}
                                output="(r+g+b)/3"
                                ''')
  

  # window for now
  Fb1w=Fb1+'_w'
  Fb2w=Fb2+'_w'
  Fb3w=Fb3+'_w'
  Fgw =Fg +'_w'
  par['ox']=par['wox']
  par['oz']=par['woz']
  par['ot']=par['wot']
  par['nx']=par['wnx']
  par['nz']=par['wnz']
  par['nt']=par['wnt']
  par['dt']=par['dt']*par['wjt']
  Flow(Fb1w,Fb1,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb2w,Fb2,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb3w,Fb3,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fgw, Fg ,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 

  # save results for level 0
  pyr.plot_level_cube(Fb1w,dict(),'','movie=3 title="blue band"')
  pyr.plot_level_cube(Fb2w,dict(),'','movie=3 title="green band"')
  pyr.plot_level_cube(Fb3w,dict(),'','movie=3 title="red band"')
  pyr.plot_level_cube(Fgw ,dict(),'','movie=3 title="greyscale"')

  # set 'em up
  par['fs_Hz'] =1.0/par['dt']

  # perform motion magnification on various videos here
  Fb1m =Fb1w+'_mm'   
  Fb2m =Fb2w+'_mm'  
  Fb3m =Fb3w+'_mm'   
  Fgm  =Fgw +'_mm'   
  pyr.motionmag(Fb1m,Fb1w,par) 
  pyr.motionmag(Fb2m,Fb2w,par) 
  pyr.motionmag(Fb3m,Fb3w,par) 
  pyr.motionmag(Fgm, Fgw, par) 
  pyr.plot_level_cube(Fb1m,dict(),'','movie=3 title="blue band: motion magnified"')
  pyr.plot_level_cube(Fb2m,dict(),'','movie=3 title="green band: motion magnified"')
  pyr.plot_level_cube(Fb3m,dict(),'','movie=3 title="red band: motion magnified"')
  pyr.plot_level_cube(Fgm ,dict(),'','movie=3 title="greyscale: motion magnified"')

  # window a single pixel out of band 1 to take a look
  Flow('pixel1'      ,'b1_w'   ,'window n1=1 n2=1 n3=256 f1=0 f2=0 f3=0')
  Flow('pixel1_mm'   ,'b1_w_mm','window n1=1 n2=1 n3=256 f1=0 f2=0 f3=0')
  Flow('pixel1_fft'   ,'pixel1'   ,'fft1 | put label1=frequency unit1=Hz label2=amplitude ')
  Flow('pixel1_mm_fft','pixel1_mm','fft1 | put label1=frequency unit1=Hz label2=amplitude ')
  Plot('pixel1'       ,'graph')
  Plot('pixel1_mm'    ,'graph')
  Plot('pixel1_fft'   ,'cabs | graph')
  Plot('pixel1_mm_fft','cabs | graph')

  # end of motionmag_v2()

# Run motion magnification for use with detecting heartbeats 
#
# Inputs:
#   Fv_mp4 - absolute path and file name to input video file 
#   par    - motion magnification parameter dictionary
#
# Outputs:
#   More files than you can shake a stick at.
# 
# This version has following features
#  1.) Whatever happens in pyr.motionmag() happens here 
#  2.) Runs MM on 3 bands in input video
#  3.) TODO: Outputs a single mp4 file with motion magnified video
#  4.) TODO: Hacks pyr.motionmag() as it currently is to only use 
#            one level in motion magnification process
def motionmag_v3(Fv_mp4,par):
  

  # output mp4 filename
  Fclrm='color2_mm.mp4'   

  # decompose video into bands
  Fb1 ="b1" # blue
  Fb2 ="b2" # green 
  Fb3 ="b3" # red 
  Fg  ="grey"
  Flow([Fb1,Fb2,Fb3],'video2rsf.x','./video2rsf.x '+Fv_mp4+
                                   ''' verb=n
                                       band1=${TARGETS[0]} 
                                       band2=${TARGETS[1]} 
                                       band3=${TARGETS[2]}
                                       norm=y
                                   ''')
  # derive greyscale 
  Flow(Fg,[Fb3,Fb2,Fb1],'''
                                math
                                r=${SOURCES[0]} g=${SOURCES[1]} b=${SOURCES[2]}
                                output="(r+g+b)/3"
                                ''')
  

  # window for now
  Fb1w=Fb1+'_w'
  Fb2w=Fb2+'_w'
  Fb3w=Fb3+'_w'
  Fgw =Fg +'_w'
  par['ox']=par['wox']
  par['oz']=par['woz']
  par['ot']=par['wot']
  par['nx']=par['wnx']
  par['nz']=par['wnz']
  par['nt']=par['wnt']
  par['dt']=par['dt']*par['wjt']
  par['ux']='pixels'
  par['uz']='pixels'
  par['ut']='s'
  wplot.param(par)
  Flow(Fb1w,Fb1,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb2w,Fb2,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb3w,Fb3,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fgw, Fg ,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 

  # save results for level 0
  pyr.plot_level_cube(Fb1w,par,'gainpanel=a',' label1=z label2=x title="blue band"')
  pyr.plot_level_cube(Fb2w,par,'gainpanel=a',' label1=z label2=x title="green band"')
  pyr.plot_level_cube(Fb3w,par,'gainpanel=a',' label1=z label2=x title="red band"')
  pyr.plot_level_cube(Fgw ,par,'gainpanel=a',' label1=z label2=x title="greyscale"')

  # save accumulation plots
  Fb1wa=Fb1w+'_acc'
  Fb2wa=Fb2w+'_acc'
  Fb3wa=Fb3w+'_acc'
  pyr.accumulate(Fb1wa,Fb1w,par)
  pyr.accumulate(Fb2wa,Fb2w,par)
  pyr.accumulate(Fb3wa,Fb3w,par)
  

  # set 'em up
  par['fs_Hz'] =1.0/par['dt']

  # perform motion magnification on various videos here
  Fb1m =Fb1w+'_mm'   
  Fb2m =Fb2w+'_mm'  
  Fb3m =Fb3w+'_mm'   
  Fgm  =Fgw +'_mm'   
  pyr.motionmag(Fb1m,Fb1w,par) 
  pyr.motionmag(Fb2m,Fb2w,par) 
  pyr.motionmag(Fb3m,Fb3w,par) 
  pyr.motionmag(Fgm, Fgw, par) 
  pyr.plot_level_cube(Fb1m,par,'','  label1=z label2=x title="blue band: motion magnified (all levels)"')
  pyr.plot_level_cube(Fb2m,par,'','  label1=z label2=x title="green band: motion magnified (all levels)"')
  pyr.plot_level_cube(Fb3m,par,'','  label1=z label2=x title="red band: motion magnified (all levels)"')
  pyr.plot_level_cube(Fgm ,par,'',' label1=z label2=x title="greyscale: motion magnified (all levels)"')

  # window a single pixel out of band 1 to take a look
  Flow('pixel1'      ,'b1_w'   ,'window n1=1 n2=1 n3=256 f1=0 f2=0 f3=0')
  Flow('pixel1_mm'   ,'b1_w_mm','window n1=1 n2=1 n3=256 f1=0 f2=0 f3=0')
  Flow('pixel1_fft'   ,'pixel1'   ,'fft1 | put label1=frequency unit1=Hz label2=amplitude ')
  Flow('pixel1_mm_fft','pixel1_mm','fft1 | put label1=frequency unit1=Hz label2=amplitude ')
  Plot('pixel1'       ,'graph')
  Plot('pixel1_mm'    ,'graph')
  Plot('pixel1_fft'   ,'cabs | graph')
  Plot('pixel1_mm_fft','cabs | graph')

  Fb1wpm='b1_wpm'
  Fb2wpm='b2_wpm'
  Fb3wpm='b3_wpm'

  Flow(Fb1wpm,[Fb1w,Fb1m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')
  Flow(Fb2wpm,[Fb2w,Fb2m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')
  Flow(Fb3wpm,[Fb3w,Fb3m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')

  # convert motion magnified bands to a video
  Flow(Fclrm,[Fb1wpm,Fb2wpm,Fb3wpm,'rsf2video.x'],'./rsf2video.x '+Fv_mp4+
                                     ''' verb=n
                                         mp4_out=${TARGETS[0]}
                                         band1=${SOURCES[0]} 
                                         band2=${SOURCES[1]} 
                                         band3=${SOURCES[2]}
                                         fps=30
                                     ''')

  # custom plot saves for IP project

  # stacked trace and spectra for raw video
  # concatenate and normalize before plotting for scale
  Fb1s='b1_w_l00_s'
  Fb2s='b2_w_l00_s'
  Fb3s='b3_w_l00_s'
  Fb1f='b1_w_l00_s_f'
  Fb2f='b2_w_l00_s_f'
  Fb3f='b3_w_l00_s_f'
  FbAs='ba_w_l00_s'
  FbAf='ba_w_l00_s_f'
  Flow(FbAs,[Fb1s,Fb2s,Fb3s],'cat axis=2 space=n ${SOURCES[1:3]} | scale axis=123') 
  Flow(FbAf,[Fb1f,Fb2f,Fb3f],'cat axis=2 space=n ${SOURCES[1:3]} | cabs | scale axis=123') 
  # time series
  Plot(Fb1s,FbAs,'window n2=1 f2=0 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=6') #blue 
  Plot(Fb2s,FbAs,'window n2=1 f2=1 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=3') #green
  Plot(Fb3s,FbAs,'window n2=1 f2=2 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=5') #red
  # spectra 
  Plot(Fb1f,FbAf,'window n2=1 f2=0 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=6') #blue 
  Plot(Fb2f,FbAf,'window n2=1 f2=1 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=3') #green
  Plot(Fb3f,FbAf,'window n2=1 f2=2 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=5') #red

  Result(FbAs,[Fb1s,Fb2s,Fb3s],'Overlay')
  Result(FbAf,[Fb1f,Fb2f,Fb3f],'Overlay')
 
  # each level motion magnified (cube + trace + frequency plot) 
  for i in range(0,5):
    tag = "%02d"%i 
    tagc= "_rui"+'_'+tag
    tags= "_l"+tag+'_bs_s'
    tagf= tags+"_f"
  
    Fcube1 =Fb1m+tagc        #cube view
    Fcube2 =Fb2m+tagc        #cube view
    Fcube3 =Fb3m+tagc        #cube view
    Fcube1s=Fcube1+'_scaled' #cube view scaled 0-1
    Fcube2s=Fcube2+'_scaled' #cube view scaled 0-1
    Fcube3s=Fcube3+'_scaled' #cube view scaled 0-1
    Fcubeg =Fgm+tagc         #cube view
    Fb1s   =Fb1w+tags        #stacked trace
    Fb2s   =Fb2w+tags        #stacked trace
    Fb3s   =Fb3w+tags        #stacked trace
    Fb1f   =Fb1w+tagf        #stacked trace spectra
    Fb2f   =Fb2w+tagf        #stacked trace spectra
    Fb3f   =Fb3w+tagf        #stacked trace spectra
    FbAs   ='ba'+tags        #stacked trace
    FbAf   ='ba'+tagf        #stacked trace spectra
    Fmp4   ='ba'+tagc+'.mp4' #mp4 file

    print FbAs
    print FbAf


    # plot cubes
    pyr.plot_level_cube(Fcube1,par,'','''
                        label1=z label2=x title="blue band: motion magnified (level %d)" 
                                        '''%(i))
    pyr.plot_level_cube(Fcube2,par,'','''
                        label1=z label2=x title="green band: motion magnified (level %d)" 
                                        '''%(i))
    pyr.plot_level_cube(Fcube3,par,'','''
                        label1=z label2=x title="red band: motion magnified (level %d)" 
                                        '''%(i))
    pyr.plot_level_cube(Fcubeg,par,'','''
                        label1=z label2=x title="gray image: motion magnified (level %d)" 
                                        '''%(i))

    # write out this level's bands as an MP4 file
    # scale all bands to be between zero and one
    Flow(Fcube1s,Fcube1,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fcube2s,Fcube2,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fcube3s,Fcube3,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fmp4,[Fcube1s,Fcube2s,Fcube3s,'rsf2video.x'],'./rsf2video.x '+Fv_mp4+
                                    ''' verb=n
                                        mp4_out=${TARGETS[0]}
                                        band1=${SOURCES[0]} 
                                        band2=${SOURCES[1]} 
                                        band3=${SOURCES[2]}
                                        fps=30
                                    ''')


    # concatenate and normalize before plotting for scale
    Flow(FbAs,[Fb1s,Fb2s,Fb3s],'cat axis=2 space=n ${SOURCES[1:3]} | scale axis=123') 
    Flow(FbAf,[Fb1f,Fb2f,Fb3f],'cat axis=2 space=n ${SOURCES[1:3]} | cabs | scale axis=123') 
    # time series
    Plot(Fb1s,FbAs,'window n2=1 f2=0 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=6') #blue 
    Plot(Fb2s,FbAs,'window n2=1 f2=1 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=3') #green
    Plot(Fb3s,FbAs,'window n2=1 f2=2 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=5') #red
    # spectra 
    Plot(Fb1f,FbAf,'window n2=1 f2=0 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=6') #blue 
    Plot(Fb2f,FbAf,'window n2=1 f2=1 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=3') #green
    Plot(Fb3f,FbAf,'window n2=1 f2=2 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=5') #red

    Result(FbAs,[Fb1s,Fb2s,Fb3s],'Overlay')
    Result(FbAf,[Fb1f,Fb2f,Fb3f],'Overlay')


 
   
    

  

  # end of motionmag_v3()

# Run motion magnification for use with library cup and paper experiment 
#
# Inputs:
#   Fv_mp4 - absolute path and file name to input video file 
#   par    - motion magnification parameter dictionary
#
# Outputs:
#   More files than you can shake a stick at.
# 
# This version has following features
#  1.) Whatever happens in pyr.motionmag() happens here 
#  2.) Runs MM on 3 bands in input video
def motionmag_v4(Fv_mp4,par):
  

  # output mp4 filename
  Fclrm='color2_mm.mp4'   

  # decompose video into bands
  Fb1 ="b1" # blue
  Fb2 ="b2" # green 
  Fb3 ="b3" # red 
  Flow([Fb1,Fb2,Fb3],'video2rsf.x','./video2rsf.x '+Fv_mp4+
                                   ''' verb=n
                                       band1=${TARGETS[0]} 
                                       band2=${TARGETS[1]} 
                                       band3=${TARGETS[2]}
                                       norm=y
                                   ''')

  # window for now
  Fb1w=Fb1+'_w'
  Fb2w=Fb2+'_w'
  Fb3w=Fb3+'_w'
  par['ox']=par['wox']
  par['oz']=par['woz']
  par['ot']=par['wot']
  par['nx']=par['wnx']
  par['nz']=par['wnz']
  par['nt']=par['wnt']
  par['dt']=par['dt']*par['wjt']
  par['ux']='pixels'
  par['uz']='pixels'
  par['ut']='s'
  wplot.param(par)
  Flow(Fb1w,Fb1,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb2w,Fb2,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb3w,Fb3,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 

  # save results for level 0
  # pyr.plot_level_cube(Fb1w,par,'gainpanel=a',' label1=z label2=x title="blue band"')
  #pyr.plot_level_cube(Fb2w,par,'gainpanel=a',' label1=z label2=x title="green band"')
  #pyr.plot_level_cube(Fb3w,par,'gainpanel=a',' label1=z label2=x title="red band"')

  frame1=par['nx']/2.0
  frame2=par['nz']/2.0
  frame3=par['ot']


  Result(Fb1w,' byte pclip=100 scalebar=y gainpanel=a bar=bar.rsf | grey3 scalebar=y bar=bar.rsf label1=z label2=x title="blue band" frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 
  Result(Fb2w,' byte pclip=100 scalebar=y gainpanel=a bar=bar.rsf | grey3 scalebar=y bar=bar.rsf label1=z label2=x title="green band" frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 
  Result(Fb3w,' byte pclip=100 scalebar=y gainpanel=a bar=bar.rsf | grey3 scalebar=y bar=bar.rsf label1=z label2=x title="red band" frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 


  # save accumulation plots
  Fb1wa=Fb1w+'_acc'
  Fb2wa=Fb2w+'_acc'
  Fb3wa=Fb3w+'_acc'
  pyr.accumulate(Fb1wa,Fb1w,par)
  pyr.accumulate(Fb2wa,Fb2w,par)
  pyr.accumulate(Fb3wa,Fb3w,par)
  

  # set 'em up
  par['fs_Hz'] =1.0/par['dt']

  # perform motion magnification on various videos here
  Fb1m =Fb1w+'_mm'   
  Fb2m =Fb2w+'_mm'  
  Fb3m =Fb3w+'_mm'   
  pyr.motionmag(Fb1m,Fb1w,par) 
  pyr.motionmag(Fb2m,Fb2w,par) 
  pyr.motionmag(Fb3m,Fb3w,par) 
  pyr.plot_level_cube(Fb1m,par,'','  label1=z label2=x title="blue band: motion magnified (all levels)"')
  pyr.plot_level_cube(Fb2m,par,'','  label1=z label2=x title="green band: motion magnified (all levels)"')
  pyr.plot_level_cube(Fb3m,par,'','  label1=z label2=x title="red band: motion magnified (all levels)"')


  Fb1wpm='b1_wpm'
  Fb2wpm='b2_wpm'
  Fb3wpm='b3_wpm'

  Flow(Fb1wpm,[Fb1w,Fb1m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')
  Flow(Fb2wpm,[Fb2w,Fb2m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')
  Flow(Fb3wpm,[Fb3w,Fb3m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')

  # convert motion magnified bands to a video
  Flow(Fclrm,[Fb1wpm,Fb2wpm,Fb3wpm,'rsf2video.x'],'./rsf2video.x '+Fv_mp4+
                                     ''' verb=n
                                         mp4_out=${TARGETS[0]}
                                         band1=${SOURCES[0]} 
                                         band2=${SOURCES[1]} 
                                         band3=${SOURCES[2]}
                                         fps=30
                                     ''')

  # custom plot saves for IP project

  # stacked trace and spectra for raw video
  # concatenate and normalize before plotting for scale
  Fb1s='b1_w_l00_s'
  Fb2s='b2_w_l00_s'
  Fb3s='b3_w_l00_s'
  Fb1f='b1_w_l00_s_f'
  Fb2f='b2_w_l00_s_f'
  Fb3f='b3_w_l00_s_f'
  FbAs='ba_w_l00_s'
  FbAf='ba_w_l00_s_f'
  Flow(FbAs,[Fb1s,Fb2s,Fb3s],'cat axis=2 space=n ${SOURCES[1:3]} | scale axis=123') 
  Flow(FbAf,[Fb1f,Fb2f,Fb3f],'cat axis=2 space=n ${SOURCES[1:3]} | cabs | scale axis=123') 
  # time series
  Plot(Fb1s,FbAs,'window n2=1 f2=0 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=6') #blue 
  Plot(Fb2s,FbAs,'window n2=1 f2=1 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=3') #green
  Plot(Fb3s,FbAs,'window n2=1 f2=2 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=5') #red
  # spectra 
  Plot(Fb1f,FbAf,'window n2=1 f2=0 | graph min2=0 max2=1.1 min1=20 max1=100 title='' plotfat=3 plotcol=6') #blue 
  Plot(Fb2f,FbAf,'window n2=1 f2=1 | graph min2=0 max2=1.1 min1=20 max1=100 title='' plotfat=3 plotcol=3') #green
  Plot(Fb3f,FbAf,'window n2=1 f2=2 | graph min2=0 max2=1.1 min1=20 max1=100 title='' plotfat=3 plotcol=5') #red

  Result(FbAs,[Fb1s,Fb2s,Fb3s],'Overlay')
  Result(FbAf,[Fb1f,Fb2f,Fb3f],'Overlay')
 
  # each level motion magnified (cube + trace + frequency plot) 
  for i in range(0,5):
    tag  = "%02d"%i 
    tagc = "_rui"+'_'+tag
    tags = "_l"+tag+'_bs_s'
    tagf = tags+"_f"
    tagsp= tagf+"_sp"
  
    Fcube1 =Fb1m+tagc        #cube view
    Fcube2 =Fb2m+tagc        #cube view
    Fcube3 =Fb3m+tagc        #cube view
    Fcube1s=Fcube1+'_scaled' #cube view scaled 0-1
    Fcube2s=Fcube2+'_scaled' #cube view scaled 0-1
    Fcube3s=Fcube3+'_scaled' #cube view scaled 0-1
    Fb1s   =Fb1w+tags        #stacked trace
    Fb2s   =Fb2w+tags        #stacked trace
    Fb3s   =Fb3w+tags        #stacked trace
    Fb1f   =Fb1w+tagf        #stacked trace spectra
    Fb2f   =Fb2w+tagf        #stacked trace spectra
    Fb3f   =Fb3w+tagf        #stacked trace spectra
    Fb1sp  =Fb1w+tagsp       #stacked trace spectrogram
    Fb2sp  =Fb2w+tagsp       #stacked trace spectrogram
    Fb3sp  =Fb3w+tagsp       #stacked trace spectrogram
    FbAs   ='ba'+tags        #stacked trace
    FbAf   ='ba'+tagf        #stacked trace spectra
    Fmp4   ='ba'+tagc+'.mp4' #mp4 file

    print FbAs
    print FbAf


    # plot cubes
    pyr.plot_level_cube(Fcube1,par,'','''
                        label1=z label2=x title="blue band: motion magnified (level %d)" 
                                        '''%(i))
    pyr.plot_level_cube(Fcube2,par,'','''
                        label1=z label2=x title="green band: motion magnified (level %d)" 
                                        '''%(i))
    pyr.plot_level_cube(Fcube3,par,'','''
                        label1=z label2=x title="red band: motion magnified (level %d)" 
                                        '''%(i))

    # write out this level's bands as an MP4 file
    # scale all bands to be between zero and one
    Flow(Fcube1s,Fcube1,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fcube2s,Fcube2,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fcube3s,Fcube3,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fmp4,[Fcube1s,Fcube2s,Fcube3s,'rsf2video.x'],'./rsf2video.x '+Fv_mp4+
                                    ''' verb=n
                                        mp4_out=${TARGETS[0]}
                                        band1=${SOURCES[0]} 
                                        band2=${SOURCES[1]} 
                                        band3=${SOURCES[2]}
                                        fps=30
                                    ''')


    # concatenate and normalize before plotting for scale
    Flow(FbAs,[Fb1s,Fb2s,Fb3s],'cat axis=2 space=n ${SOURCES[1:3]} | scale axis=123') 
    Flow(FbAf,[Fb1f,Fb2f,Fb3f],'cat axis=2 space=n ${SOURCES[1:3]} | cabs | scale axis=123') 
    # time series
    Plot(Fb1s,FbAs,'window n2=1 f2=0 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=6') #blue 
    Plot(Fb2s,FbAs,'window n2=1 f2=1 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=3') #green
    Plot(Fb3s,FbAs,'window n2=1 f2=2 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=5') #red
    # spectra 
    Plot(Fb1f,FbAf,'window n2=1 f2=0 | graph min2=0 max2=1.1 min1=20 max1=100 title='' plotfat=3 plotcol=6') #blue 
    Plot(Fb2f,FbAf,'window n2=1 f2=1 | graph min2=0 max2=1.1 min1=20 max1=100 title='' plotfat=3 plotcol=3') #green
    Plot(Fb3f,FbAf,'window n2=1 f2=2 | graph min2=0 max2=1.1 min1=20 max1=100 title='' plotfat=3 plotcol=5') #red

    Result(FbAs,[Fb1s,Fb2s,Fb3s],'Overlay')
    Result(FbAf,[Fb1f,Fb2f,Fb3f],'Overlay')
    
    # save spectra
    Result(Fb1sp,Fb1s,'ltft | cabs | grey mean=y color=j title='' allpos=y') 
    Result(Fb2sp,Fb2s,'ltft | cabs | grey mean=y color=j title='' allpos=y') 
    Result(Fb3sp,Fb3s,'ltft | cabs | grey mean=y color=j title='' allpos=y') 

  # end of motionmag_v3()

# Run motion magnification for use with MIT experiment 
#
# Inputs:
#   Fv_mp4 - absolute path and file name to input video file 
#   par    - motion magnification parameter dictionary
#
# Outputs:
#   More files than you can shake a stick at.
# 
# This version has following features
#  1.) Whatever happens in pyr.motionmag() happens here 
#  2.) Runs MM on 3 bands in input video
def motionmag_v4_face(Fv_mp4,par):
  

  # output mp4 filename
  Fclrm='color2_mm.mp4'   

  # decompose video into bands
  Fb1 ="b1" # blue
  Fb2 ="b2" # green 
  Fb3 ="b3" # red 
  Flow([Fb1,Fb2,Fb3],'video2rsf.x','./video2rsf.x '+Fv_mp4+
                                   ''' verb=n
                                       band1=${TARGETS[0]} 
                                       band2=${TARGETS[1]} 
                                       band3=${TARGETS[2]}
                                       norm=y
                                   ''')

  # window for now
  Fb1w=Fb1+'_w'
  Fb2w=Fb2+'_w'
  Fb3w=Fb3+'_w'
  par['ox']=par['wox']
  par['oz']=par['woz']
  par['ot']=par['wot']
  par['nx']=par['wnx']
  par['nz']=par['wnz']
  par['nt']=par['wnt']
  par['dt']=par['dt']*par['wjt']
  par['ux']='pixels'
  par['uz']='pixels'
  par['ut']='s'
  wplot.param(par)
  Flow(Fb1w,Fb1,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb2w,Fb2,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 
  Flow(Fb3w,Fb3,'window n1=%(nz)d n2=%(nx)d n3=%(nt)d f1=%(oz)d f2=%(ox)d f3=%(ot)d j3=%(wjt)d'%par) 

  # save results for level 0
  # pyr.plot_level_cube(Fb1w,par,'gainpanel=a',' label1=z label2=x title="blue band"')
  #pyr.plot_level_cube(Fb2w,par,'gainpanel=a',' label1=z label2=x title="green band"')
  #pyr.plot_level_cube(Fb3w,par,'gainpanel=a',' label1=z label2=x title="red band"')

  frame1=par['nx']/2.0
  frame2=par['nz']/2.0
  frame3=par['ot']


  Result(Fb1w,' byte pclip=100 scalebar=y gainpanel=a bar=bar.rsf | grey3 scalebar=y bar=bar.rsf label1=z label2=x title="blue band" frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 
  Result(Fb2w,' byte pclip=100 scalebar=y gainpanel=a bar=bar.rsf | grey3 scalebar=y bar=bar.rsf label1=z label2=x title="green band" frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 
  Result(Fb3w,' byte pclip=100 scalebar=y gainpanel=a bar=bar.rsf | grey3 scalebar=y bar=bar.rsf label1=z label2=x title="red band" frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 


  # save accumulation plots
  Fb1wa=Fb1w+'_acc'
  Fb2wa=Fb2w+'_acc'
  Fb3wa=Fb3w+'_acc'
  pyr.accumulate(Fb1wa,Fb1w,par)
  pyr.accumulate(Fb2wa,Fb2w,par)
  pyr.accumulate(Fb3wa,Fb3w,par)
  

  # set 'em up
  par['fs_Hz'] =1.0/par['dt']

  # perform motion magnification on various videos here
  Fb1m =Fb1w+'_mm'   
  Fb2m =Fb2w+'_mm'  
  Fb3m =Fb3w+'_mm'   
  pyr.motionmag(Fb1m,Fb1w,par) 
  pyr.motionmag(Fb2m,Fb2w,par) 
  pyr.motionmag(Fb3m,Fb3w,par) 
  pyr.plot_level_cube(Fb1m,par,'','  label1=z label2=x title="blue band: motion magnified (all levels)"')
  pyr.plot_level_cube(Fb2m,par,'','  label1=z label2=x title="green band: motion magnified (all levels)"')
  pyr.plot_level_cube(Fb3m,par,'','  label1=z label2=x title="red band: motion magnified (all levels)"')


  Fb1wpm='b1_wpm'
  Fb2wpm='b2_wpm'
  Fb3wpm='b3_wpm'

  Flow(Fb1wpm,[Fb1w,Fb1m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')
  Flow(Fb2wpm,[Fb2w,Fb2m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')
  Flow(Fb3wpm,[Fb3w,Fb3m],'math x=${SOURCES[0]} y=${SOURCES[1]} output=x+y')

  # convert motion magnified bands to a video
  Flow(Fclrm,[Fb1wpm,Fb2wpm,Fb3wpm,'rsf2video.x'],'./rsf2video.x '+Fv_mp4+
                                     ''' verb=n
                                         mp4_out=${TARGETS[0]}
                                         band1=${SOURCES[0]} 
                                         band2=${SOURCES[1]} 
                                         band3=${SOURCES[2]}
                                         fps=30
                                     ''')

  # custom plot saves for IP project

  # stacked trace and spectra for raw video
  # concatenate and normalize before plotting for scale
  Fb1s='b1_w_l00_s'
  Fb2s='b2_w_l00_s'
  Fb3s='b3_w_l00_s'
  Fb1f='b1_w_l00_s_f'
  Fb2f='b2_w_l00_s_f'
  Fb3f='b3_w_l00_s_f'
  FbAs='ba_w_l00_s'
  FbAf='ba_w_l00_s_f'
  Flow(FbAs,[Fb1s,Fb2s,Fb3s],'cat axis=2 space=n ${SOURCES[1:3]} | scale axis=123') 
  Flow(FbAf,[Fb1f,Fb2f,Fb3f],'cat axis=2 space=n ${SOURCES[1:3]} | cabs | scale axis=123') 
  # time series
  Plot(Fb1s,FbAs,'window n2=1 f2=0 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=6') #blue 
  Plot(Fb2s,FbAs,'window n2=1 f2=1 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=3') #green
  Plot(Fb3s,FbAs,'window n2=1 f2=2 | graph min2=0 max2=+1.1 title='' plotfat=3 plotcol=5') #red
  # spectra 
  Plot(Fb1f,FbAf,'window n2=1 f2=0 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=6') #blue 
  Plot(Fb2f,FbAf,'window n2=1 f2=1 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=3') #green
  Plot(Fb3f,FbAf,'window n2=1 f2=2 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=5') #red

  Result(FbAs,[Fb1s,Fb2s,Fb3s],'Overlay')
  Result(FbAf,[Fb1f,Fb2f,Fb3f],'Overlay')
 
  # each level motion magnified (cube + trace + frequency plot) 
  for i in range(0,5):
    tag  = "%02d"%i 
    tagc = "_rui"+'_'+tag
    tags = "_l"+tag+'_bs_s'
    tagf = tags+"_f"
    tagsp= tagf+"_sp"
  
    Fcube1 =Fb1m+tagc        #cube view
    Fcube2 =Fb2m+tagc        #cube view
    Fcube3 =Fb3m+tagc        #cube view
    Fcube1s=Fcube1+'_scaled' #cube view scaled 0-1
    Fcube2s=Fcube2+'_scaled' #cube view scaled 0-1
    Fcube3s=Fcube3+'_scaled' #cube view scaled 0-1
    Fb1s   =Fb1w+tags        #stacked trace
    Fb2s   =Fb2w+tags        #stacked trace
    Fb3s   =Fb3w+tags        #stacked trace
    Fb1f   =Fb1w+tagf        #stacked trace spectra
    Fb2f   =Fb2w+tagf        #stacked trace spectra
    Fb3f   =Fb3w+tagf        #stacked trace spectra
    Fb1sp  =Fb1w+tagsp       #stacked trace spectrogram
    Fb2sp  =Fb2w+tagsp       #stacked trace spectrogram
    Fb3sp  =Fb3w+tagsp       #stacked trace spectrogram
    FbAs   ='ba'+tags        #stacked trace
    FbAf   ='ba'+tagf        #stacked trace spectra
    Fmp4   ='ba'+tagc+'.mp4' #mp4 file

    print FbAs
    print FbAf


    # plot cubes
    pyr.plot_level_cube(Fcube1,par,'','''
                        label1=z label2=x title="blue band: motion magnified (level %d)" 
                                        '''%(i))
    pyr.plot_level_cube(Fcube2,par,'','''
                        label1=z label2=x title="green band: motion magnified (level %d)" 
                                        '''%(i))
    pyr.plot_level_cube(Fcube3,par,'','''
                        label1=z label2=x title="red band: motion magnified (level %d)" 
                                        '''%(i))

    # write out this level's bands as an MP4 file
    # scale all bands to be between zero and one
    Flow(Fcube1s,Fcube1,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fcube2s,Fcube2,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fcube3s,Fcube3,' scale axis=123 | math output=input+1 | scale axis=123')  
    Flow(Fmp4,[Fcube1s,Fcube2s,Fcube3s,'rsf2video.x'],'./rsf2video.x '+Fv_mp4+
                                    ''' verb=n
                                        mp4_out=${TARGETS[0]}
                                        band1=${SOURCES[0]} 
                                        band2=${SOURCES[1]} 
                                        band3=${SOURCES[2]}
                                        fps=30
                                    ''')


    # concatenate and normalize before plotting for scale
    Flow(FbAs,[Fb1s,Fb2s,Fb3s],'cat axis=2 space=n ${SOURCES[1:3]} | scale axis=123') 
    Flow(FbAf,[Fb1f,Fb2f,Fb3f],'cat axis=2 space=n ${SOURCES[1:3]} | cabs | scale axis=123') 
    # time series
    Plot(Fb1s,FbAs,'window n2=1 f2=0 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=6') #blue 
    Plot(Fb2s,FbAs,'window n2=1 f2=1 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=3') #green
    Plot(Fb3s,FbAs,'window n2=1 f2=2 | graph min2=-1.1 max2=+1.1 title='' plotfat=3 plotcol=5') #red
    # spectra 
    Plot(Fb1f,FbAf,'window n2=1 f2=0 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=6') #blue 
    Plot(Fb2f,FbAf,'window n2=1 f2=1 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=3') #green
    Plot(Fb3f,FbAf,'window n2=1 f2=2 | graph min2=0 max2=1.1 min1=0 max1=3 title='' plotfat=3 plotcol=5') #red

    Result(FbAs,[Fb1s,Fb2s,Fb3s],'Overlay')
    Result(FbAf,[Fb1f,Fb2f,Fb3f],'Overlay')
    
    # save spectra
    Result(Fb1sp,Fb1s,'ltft | cabs | grey mean=y color=j title='' allpos=y') 
    Result(Fb2sp,Fb2s,'ltft | cabs | grey mean=y color=j title='' allpos=y') 
    Result(Fb3sp,Fb3s,'ltft | cabs | grey mean=y color=j title='' allpos=y') 

  # end of motionmag_v3()

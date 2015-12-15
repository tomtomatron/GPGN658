try:    from rsf.cluster import *
except: from rsf.proj    import *
import sys, pylab
import math
import random
import wplot

# downscale an RSF file n-times using sfpyr.x 
# Inputs:
#   string oF       - downscaled output RSF file 
#   string iF       - input RSF file to downscale n-times
#   ing    n        - number of times to downscale 
#   string preflow  - custom preflow before downscaling n-times
#   string postflow - custom postflow after downscaling n-times
# Outputs:
#   no explicit outputs
#   modifies RSF file oF
def downscale(oF,iF,n=1,preflow='',postflow=''):
    com = ''
    if n>=1:
      prg = preflow+'./sfpyr.x verb=n up=n boundary=0'
      for i in range(n):
          com+=prg
          if i != n-1:
              com+=' | '
      com+=postflow
      Flow(oF,[iF,'sfpyr.x'],com)
    elif n==0:
      print("n=0: copying not downscaling")
      Flow(oF,[iF,'sfpyr.x'],'math output=input')
    else:
      com += ' '+preflow+' '+postflow
      Flow(oF,[iF,'sfpyr.x'],com)
########################################################################################
# end of downscale()
########################################################################################


# upscale an RSF file n-times using sfpyr.x 
# Inputs:
#   string oF       - upscaled output RSF file 
#   string iF       - input RSF file to upscale n-times
#   ing    n        - number of times to upscale
#   string preflow  - custom preflow before upscaling n-times
#   string postflow - custom postflow after upscaling n-times
# Outputs:
#   no explicit outputs
#   modifies RSF file oF
def upscale(oF,iF,n=1,preflow='',postflow=''):
    com = ''
    if n>=1:
      prg = preflow+'./sfpyr.x verb=n up=y boundary=0'
      for i in range(n):
          com+=prg
          if i != n-1:
              com+=' | '
      com+=postflow
      Flow(oF,iF,com)
    elif n==0:
      print("n=0: copying not upscaling")
      Flow(oF,iF,'math output=input')
    else:
      com += ' '+preflow+' '+postflow
      Flow(oF,iF,com)
########################################################################################
# end of upscale()
########################################################################################

# collapses image pyramid after upscaling 
# Inputs:
#   string oF       - collapsed output file over dimension i 
#   list   IF       - list of input RSF files to collapse
#                     in order of decreasing resolution 
#   int    pyr_type - 0=Gaussian 1=Laplacian     
# Outputs:
#   no explicit outputs
#   modifies RSF file oF
# Notes:
#   assumes files are in order of decreasing size/resolution
def collapse(oF,IF,pyr_type=1):
    
    # number of levels     
    n=len(IF)
    Fbase=oF;

    if pyr_type==1: # gaussian pyramid
      # compute residuals
      for iL in range(0,n-1):
        tagi="%02d"%iL
        Fui =Fbase+"_ui_"+tagi # up once at next level down
        Fri =Fbase+"_ri_"+tagi # residual at this level
        Frui =Fbase+"_rui_"+tagi # residual at this level

        # up next level once 
        upscale(Fui,IF[iL+1],1) 
        
        # subtract from this level for residual      
        Flow(Fri,[IF[iL],Fui],'math x=${SOURCES[0]} y=${SOURCES[1]} output="x-y" ') 

        # resize residual to original image size
        upscale(Frui,Fri,iL) 

      # resize highest level of image pyramid to original size
      upscale(Fbase+'_rui_'+"%02d"%(n-1),IF[n-1],n-1) 

      # sum resized residuals with lowest level
      IFr=[Fbase+'_rui_%02d'%i for i in range(n)]
      sum_files(oF,IFr)
      
    elif pyr_type==2: # laplacian pyramid
      # each level is the residual, just sum them up!
      # *** the highest level of Laplacian pyramid is equal to that in Gaussian
      #     in my implementation.
      for iL in range(0,n-1):
        tagi="%02d"%iL
        Frui =Fbase+"_rui_"+tagi # residual at this level
  
        # upscale to original image size
        upscale(Frui,IF[iL],iL) 

      # sum resized residuals 
      IFr=[Fbase+'_rui_%02d'%i for i in range(n-1)]
      sum_files(oF,IFr)

    else:
      print("pyr_type ID not recognized")
########################################################################################
# end of collapse()
########################################################################################


# magnify motion in a video
#
# Inputs:
#   string Fo - output file name
#   string Fi - input file name
#   dict   par- parameter file
#
# Outputs:
#   No explicit outputs.  Modified Fo that is a motion magnified version
#   of input Fi
def motionmag(Fo,Fi,par):
  wplot.param(par)

  # motion magnification parameters
  nlevel  =par['nlevel']
  pyr_type=par['pyr_type']

  
  Fband1p=Fi+'_l00'
 
  # preprocess video
  preprocess(Fband1p,Fi,par)
  plot_level_cube(Fband1p,par,'','flat=n title="Original video: tapered "')

  # first loop over image pyramid levels (downsampling)
  for i in range(1,nlevel+1):
  
    # next file name
    tagn = "_l"+"%02d"%i  
    Fband1n=Fi+tagn

    # no matter the pyramid you must downscale once 
    downscale(Fband1n,Fband1p,1)

    #if pyr_type==1: # gaussian pyramid
      # do nothing (might change later...)
    if pyr_type==2:

      # special case for Laplacian pyramid at highest level
      if i==nlevel:
        tagL = "_l"+"%02d"%(i)+'_L'
        Fband1nL=Fi+tagL
        downscale(Fband1nL,Fband1p,1)

        # save result for now
        Plot(Fband1nL,wplot.igrey2d('',par))

      if i<=nlevel:
        tagL = "_l"+"%02d"%(i-1)+'_L'
        Fband1nL=Fi+tagL

        # use previous level in the Gaussian pyramid 
        # to form this level of Laplacian 
        Flow(Fband1nL,Fband1p,' ./sfpyr.x lap=y verb=n up=n boundary=0')

        # compute next level of the Gaussian pyramid
        downscale(Fband1n,Fband1p,1)
 
        # save result for now
        Plot(Fband1nL,wplot.igrey2d('',par))
      
    elif pyr_type!=1:
      print("pyr_type type not recognized")

    # save resulting level for testing
    Plot(Fband1n, wplot.igrey2d('',par))

    # swap file names
    tagp=tagn
    Fband1p=Fband1n
  
  # second loop over image pyramid levels 
  #  transpose x and t axis 
  #    => bandpass => scale 
  #    => transpose x and t axis
  #    => upscale to original size
  Fmulti1=[]
  for i in range(0,nlevel+1):
  
      # previous file name
      tagp = "_l"+"%02d"%i 
      Fband1p=Fi+tagp
      Fband1n=Fband1p+'_bs'

      preflow=''' 
                transp plane=13 | 
                erf flo=%(fl_Hz)g fhi=%(fh_Hz)g rect=32 |
                math output=%(alpha)g*input |
                transp plane=13 
              '''%par
      Flow(Fband1n,Fband1p,preflow) 

      plot_level_cube(Fband1n,par,'','flat=n title=""')
  
      # save list of filenames to collapse later
      Fmulti1.append(Fband1n)


  # collapse pyramid (works for Gaussian only right now)
  # TODO: collapse a Laplacian pyramid 
  collapse(Fo,Fmulti1,pyr_type)

  # Optional section:
  # compute stacked versions of the cube if desired
  # stack over z and x (first two dimensions) to show time series 
  # and spectrum for each level (w and w/o magnification)
  go_stack=True
  if go_stack:
    # for motion magnified result
    # stack over z and x then normalize
    Flow(Fo+'_s',Fo,'''stack axis=1 norm=n | stack axis=1 norm=n 
                       | put label1=time unit1=s label2=intensity unit2='' 
                    ''' )
    # amplitude spectra
    Flow(Fo+'_s'+'_f',Fo+'_s','''fft1  
                                 | put label1=frequency unit1=Hz label2=amplitude unit2='' 
                              ''')

    # save what you want here 
    Plot(Fo+'_s'     ,'graph title='' plotfat=3 plotcol=3')
    Plot(Fo+'_s'+'_f','cabs | graph title='' plotfat=3 plotcol=3')

    # for each level of the pyramid
    for i in range(0,nlevel+1):
        
        # previous files
        tagp = "_l"+"%02d"%i+"_bs" 
        tagl = "_l"+"%02d"%i 
        Fband1p =Fi+tagp
        Fband1l =Fi+tagl
    
        # next files 
        Fband1n  =Fband1p+'_s'
        Fband1nf =Fband1n+'_f'
        Fband1nl =Fband1l+'_s'
        Fband1nlf=Fband1nl+'_f'

        # stack over z and x then normalize
        Flow(Fband1n ,Fband1p,'''stack axis=1 norm=n | stack axis=1 norm=n 
                                 | put label1=time unit1=s label2=intensity unit2='' 
  	    											''' )
        Flow(Fband1nl,Fband1l,'''stack axis=1 norm=n | stack axis=1 norm=n 
                                 | put label1=time unit1=s label2=intensity unit2='' 
  	    											''' )
        # amplitude spectra
        Flow(Fband1nf,Fband1n,'''fft1  
                                 | put label1=frequency unit1=Hz label2=amplitude unit2='' 
		    										  ''')
        Flow(Fband1nlf,Fband1nl,'''fft1  
                                 | put label1=frequency unit1=Hz label2=amplitude unit2='' 
		    										  ''')
   
        # save what you want here 
        #Plot(Fband1n  ,'graph title='' plotfat=3 plotcol=3')
        #Plot(Fband1nl ,'graph title='' plotfat=3 plotcol=3')
        #Plot(Fband1nf ,'cabs | graph title='' plotfat=3 plotcol=3')
        #Plot(Fband1nlf,'cabs | graph title='' plotfat=3 plotcol=3')
########################################################################################
# end of motionmag()
########################################################################################

def preprocess(Fband1p,Fi,par,verb=False):
  if (verb): print("Tapering video with cosine taper")
  # cosine taper size for sfcostaper to reduce ringing   
  # try 20% taper
  #nw3     =round(par['nt']*0.2) 
  nw3     =round(par['nt']*0.0) 

  Flow(Fband1p,Fi,"math output=input | costaper nw3=%d"%nw3)


# Accumulate differrences from first video frame
# 
# Input:
#   string Fo - output file name
#   string Fi - input file name
#   dict  par - parameter dictionary for video 
# 
# Output:
#   Not explicit output - creates RSF file Fo with plot
def accumulate(Fo,Fi,par):
  Fif=Fi+'_fst'
  Fis=Fi+'_stk'
  Flow(Fif,Fi,'window f3=0 n3=1') # get first frame
  Flow(Fis,Fi,'stack axis=3 norm=n') # get stack over time
  Flow(Fo,[Fif,Fis],''' math x=${SOURCES[0]} y=${SOURCES[1]} 
                        output="abs((%d-1)*x-y)/%d"
                    '''%(par['nt'],par['nt']))
  Result(Fo,'grey mean=y allpos=y scalebar=y title=""')

  # jerry-rig to comply with wplot.py
  part=par
  print par['oz']
  #part['nx']=par['nx']
  #part['nz']=par['n2']
  #part['dx']=par['d1']
  ##part['dz']=par['d2']
  #part['ox']=par['o1']
  #part['oz']=par['o2']


  Result(Fo,wplot.igrey2d('label1=x label2=z allpos=y scalebar=y mean=y',par))






# sum multiple RSF files of equal size
#
# Input:
#   string Fo - output file name 
#   list   FI - list of RSF files 
# Output:
#   No explicit output.  Fo is created as the sum
#   of files in FI.
# Notes:
#   Assumes the files have the same axis info
def sum_files(oF,IF):

    n=len(IF)

    # generate variable names
    vnames=getrandletter(n)

    # form input commands for sfmath
    inputs=''
    outputs=''

    for i in range(n):
      inputs += vnames[i]+'='+'${SOURCES['+str(i)+']} '
      outputs+= vnames[i]
      if i != n-1:
			  outputs+='+'

    Flow(oF,IF,' math '+inputs+' output='+outputs)

# weighted sum multiple RSF files of equal size
#
# Input:
#   string Fo - output file name 
#   list   FI - list of RSF files 
#   array  alpha - scales for each file 
# Output:
#   No explicit output.  Fo is created as the sum
#   of files in FI.
# Notes:
#   Assumes the files have the same axis info
def sum_files_weighted(oF,IF,alpha):

    n=len(IF)

    # generate variable names
    vnames=getrandletter(n)

    # form input commands for sfmath
    print(alpha)
    inputs=''
    outputs=''

    for i in range(n):
      inputs += vnames[i]+'='+'${SOURCES['+str(i)+']} '
      outputs+= '(%g)*'%alpha[i]+vnames[i]
      if i != n-1:
			  outputs+='+'
    Flow(oF,IF,' math '+inputs+' output='+'"'+outputs+'"')
########################################################################################
# end of sum_files()
########################################################################################


# get n unique random letters from the alphabet
# Inputs:
#   int n        - number of letters 
# Outputs:
#   list letters - list of letters 
def getrandletter(n):
  let = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'
          'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'
          'p', 'q', 'r', 's', 't', 'u', 'v', 'w'
          'x', 'y', 'z']
  letters=[];
  for i in range(n):
      pos = random.randint(0,len(let)-1)
      letters.append(let[pos])
  return letters
########################################################################################
# end of getrandletter()
########################################################################################


# plot a cube
# meant to be used when displaying levels of video cube
def plot_level_cube(Fin,par=dict(),custombyte='',customgrey3=' title=""'):
  wplot.param(par)
  frame1=par['nx']/2.0
  frame2=par['nz']/2.0
  # index not coordinate
  frame3=par['ot']

  # good for all positive between zero and one
  #Result(Fin,' byte pclip=100 gainpanel=a allpos=y scalebar=y ' + custombyte + ' bar=bar.rsf | grey3 scalebar=y bar=bar.rsf ' + customgrey3 + ' frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 
  Result(Fin,' byte pclip=100 scalebar=y ' + custombyte + ' bar=bar.rsf | grey3 scalebar=y bar=bar.rsf ' + customgrey3 + ' frame1=%d '%frame1 + ' frame2=%d '%frame2 + ' frame3=%d'%frame3); 

########################################################################################
# end of plot_level_cube()
########################################################################################


# get parameter dictionary from an rsf file
#
# Input:
#   string filename - input rsf file
# Output: 
#   dict   par      - parameter dictionary for rsf file axis
def get_par_rsf(par,filename):
  input = rsf.Input(filename)
  par['n1'] = input.int("n1")
  par['n2'] = input.int("n2")
  par['n3'] = input.int("n3")
  par['d1'] = input.float("d1")
  par['d2'] = input.float("d2")
  par['d3'] = input.float("d3")
  par['o1'] = input.float("o1")
  par['o2'] = input.float("o2")
  par['o3'] = input.float("o3")
  #par['label1'] = input.string("label1")
  #par['label2'] = input.string("label2")
  #par['label3'] = input.string("label3")
  #par['unit1'] = input.string("unit1")
  #par['unit2'] = input.string("unit2")
  #par['unit3'] = input.string("unit3")
########################################################################################
# end of get_par_rsf()
########################################################################################

 

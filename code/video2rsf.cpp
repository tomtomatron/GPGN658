#include <iostream>
#include <valarray>

#include <opencv2/videoio.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

#include "rsf.hh"
#include "utilities.hpp"

/*
Purpose: Converts video file to 3 RSF files for each video channel 

Inputs:
string stdin = video file name 
float  fps   = frames per second 
               (defaults to video fps stored in video file) 
bool   verb  = verbose output?  
               (default is false)
bool   norm   = normalize pixel values [0-1]?  
               (default is false)

Outputs:
sf_file band1 = RSF file corresponding to first band (B)
sf_file band2 = RSF file corresponding to second band (G)
sf_file band3 = RSF file corresponding to third band (R)

Notes:

Usage:
./video2rsf.x < video.mp4 verb=n fps=29.97 band1=band1.rsf band2=band2.rsf band3=band3.rsf

or in SConstruct using M8R

Flow(['band1','band2','band3'],'video2rsf.x','./video2rsf.x video.mp4 verb=n fps=29.97 band1=${TARGETS[0]} band2=${TARGETS[1]} band3=${TARGETS[2]}')


*/
using namespace std;
using namespace cv;

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::cerr << "Must specify input video file." << std::endl;
        return 1;
    }
    bool verb,norm;
    float fps;
    sf_warning("In video2rsf.cpp");

    // possibly relax these hardcoded values later
    int channels  = 3;  //number of channels in video frame

    // temporary debug variables
    bool verb_debug(true);
    int c(0); //temporary counter

    // initialize RSF
    sf_init(argc,argv);
    if (!sf_getbool("verb",&verb)) verb=0;
    if (!sf_getbool("norm",&norm)) norm=0;

    // video file input  
    string file_input=argv[1];    
    VideoCapture cap(file_input);
    if (!cap.isOpened()){ cerr << "video file not open" << endl; }
    if (!sf_getfloat("fps",&fps )) fps=cap.get(CAP_PROP_FPS);
    int num_frames= cap.get(CAP_PROP_FRAME_COUNT);
    int width     = cap.get(CAP_PROP_FRAME_WIDTH);
    int height    = cap.get(CAP_PROP_FRAME_HEIGHT);
    int type      = cap.get(CAP_PROP_FORMAT);
    sf_warning("number of frames = %d",num_frames);
    sf_warning("width = %d",width);
    sf_warning("height= %d",height);
    sf_warning("type  = %d",type);
    sf_warning("cap.get(CAP_PROP_FPS)= %f",cap.get(CAP_PROP_FPS));
    sf_warning("fps= %f",fps);
    if (verb) sf_warning("Video pixel type = %d",type);
    Mat temp_frame;   
 
    // setup output RSF file
    sf_file Fo1=NULL, Fo2=NULL, Fo3=NULL; // I/O files for each band
    int nx(width);
    int nz(height);
    int nt(num_frames);                   //length of axes
    float dx(1), dz(1), dt(1/fps);          //sampling of axes
    
    // setup I/O files
    Fo1=sf_output("band1");
    Fo2=sf_output("band2");
    Fo3=sf_output("band3");
    int num_frames_dropped=get_num_frames_dropped(file_input);
  
    // setup I/O axes info for each band file 
    int   n1(nz), n2(nx), n3(nt-num_frames_dropped);
    float d1(dz), d2(dx), d3(dt);
    int   o1(0) , o2(0) , o3(0);
    //
    nx=nx; nz=nz; nt=(nt-num_frames_dropped);
    dx=dx; dz=dz; dt=dt;
    float ox(0),  oz(0),  ot(0) ;
    sf_axis ax,az,at;
    // using old n1n2n3 notation
    ax=sf_maxa(n1,o1,d1); sf_setlabel(ax,"x");    sf_setunit(ax,"pixels");
    az=sf_maxa(n2,o2,d2); sf_setlabel(az,"z");    sf_setunit(az,"pixels");
    at=sf_maxa(n3,o3,d3); sf_setlabel(at,"time"); sf_setunit(at,"s");

    sf_oaxa(Fo1,ax,1);   
    sf_oaxa(Fo1,az,2);   
    sf_oaxa(Fo1,at,3);   
    sf_oaxa(Fo2,ax,1);   
    sf_oaxa(Fo2,az,2);   
    sf_oaxa(Fo2,at,3);   
    sf_oaxa(Fo3,ax,1);   
    sf_oaxa(Fo3,az,2);   
    sf_oaxa(Fo3,at,3);   


    // allocate color channel arrays
    float *b=NULL;
    float *g=NULL;
    float *r=NULL;
    float pb;
    float pg;
    float pr;
    b = sf_floatalloc(n1*n2*n3);
    g = sf_floatalloc(n1*n2*n3);
    r = sf_floatalloc(n1*n2*n3);

    cv::Mat planes[3]; 
    // main loop over each frame in video 
    int num_frames_not_dropped=0;
    for (int it=0; it<n3; ++it) {
       
        
      cap >> temp_frame;


      // check if frame was dropped
      if (temp_frame.rows==0) { 
        sf_warning("next frame in video is dropped! Not including in rsf video"); 
      } else {
        temp_frame.convertTo(temp_frame, CV_32FC3);  //*important to convert to float 
        if (norm) { 
          temp_frame *= (1.0)/(255.0);
        }
        split(temp_frame,planes);                    //fill channels with BGR values 
        for (int ix=0; ix<nx; ++ix) { //column
          for (int iz=0; iz<nz; ++iz) { //row

            // extract pixel values from each band
            pb= planes[0].at<float>(iz,ix);
            pg= planes[1].at<float>(iz,ix);
            pr= planes[2].at<float>(iz,ix);
                
            // place color values in 1D array
            b[c] = pb;
            g[c] = pg;
            r[c] = pr;
            
            // increment pixel index  
            ++num_frames_not_dropped;
            ++c;
          }
        }
      } 
    }

    if (verb) sf_warning("Number of frames not dropped = ",num_frames_not_dropped);

    // write to band files
    sf_floatwrite(b,n1*n2*n3,Fo1);
    sf_floatwrite(g,n1*n2*n3,Fo2);
    sf_floatwrite(r,n1*n2*n3,Fo3);

    // release the kraken 
    free(b);
    free(g);
    free(r);

    return 0;
}


#include <iostream>
#include <valarray>

#include <opencv2/videoio.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

#include "rsf.hh"
#include "utilities.hpp"
#include <cmath>

/*
Purpose: Converts 3 RSF files to a .MP4 file 

Inputs:
sf_file band1 = RSF file corresponding to first band (B)
sf_file band2 = RSF file corresponding to second band (G)
sf_file band3 = RSF file corresponding to third band (R)
float  fps   = frames per second 
               (defaults to video fps stored in video file) 
bool   verb  = verbose output?  
               (default is false)

Outputs:
string stdin = MP4 video file name 

Notes:

Usage:
./rsf2video.x < video.mp4 verb=n band1=band1.rsf band2=band2.rsf band3=band3.rsf

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
    sf_warning("In rsf2video.cpp");

    // possibly relax these hardcoded values later
    int nchannels  = 3;  //number of channels in video frame

    // temporary debug variables
    bool verb_debug(true);
    int c(0); //temporary counter

    // initialize RSF
    sf_init(argc,argv);
    if (!sf_getbool("verb",&verb)) verb=0;
    if (!sf_getbool("norm",&norm)) norm=0;

    // input color band videos
    sf_file Fb1, Fb2, Fb3; 
    string Fclr;
    sf_axis ax,az,at;
    Fb1 =sf_input("band1");
    Fb2 =sf_input("band2");
    Fb3 =sf_input("band3");
    Fclr=sf_getstring("mp4_out"); 
    if (!sf_getfloat("fps",&fps )) sf_error("Must specify fps"); 
    ax=sf_iaxa(Fb1,1);  az=sf_iaxa(Fb1,2);  at=sf_iaxa(Fb1,3);
    int width  =sf_n(ax);
    int height =sf_n(az);
    int nframes=sf_n(at);
    int nx(width);
    int nz(height);
    int nt(nframes);
    
    

    // video file output  
<<<<<<< HEAD
    cv::Mat b, g, r;
=======
>>>>>>> 9e70fe330568262b8611661a3f44c0b1fc02b7cc

    cv::VideoWriter writer;
    vector<Mat> bands;
    cv::Mat b, g, r, temp_frame, fin_img;

    // video writer
    int fcc = CV_FOURCC('M', 'P', '4','V'); //four character code to write video
    //int fcc = CV_FOURCC('X', '2', '6','4'); //four character code to write video
    cv::Size frameSize(width,height);
    writer=cv::VideoWriter(Fclr,fcc,fps,frameSize);
    if(!writer.isOpened()){
        cerr << "writer not opened" << endl;
        getchar(); //wait for user to press key
        exit(EXIT_FAILURE);
    }


    // hardcode bands and merge into frame
    b=Mat::zeros(Size(width,height),CV_32FC1);
    g=Mat::zeros(Size(width,height),CV_32FC1);
    r=Mat::zeros(Size(width,height),CV_32FC1);
    bands.push_back(b);
    bands.push_back(g);
    bands.push_back(r);
    merge(bands,temp_frame);

    cv::Mat temp_frame(3,3,CV_32F);
 //??
    //bconvertTo(b, CV_32FC3);  //*important to convert to float 
    //g.convertTo(g, CV_32FC3);  //*important to convert to float 
    //r.convertTo(r, CV_32FC3);  //*important to convert to float 


<<<<<<< HEAD
    int fcc = CV_FOURCC('X', '2', '6','4'); //four character code to write video
    cv::Size frameSize(width,height);
    //writer=cv::VideoWriter("out.mp4",fcc,fps,frameSize,true);
    writer=cv::VideoWriter("out.mp4",CV_FOURCC('S','V','Q','3'),fps, frameSize);
=======
>>>>>>> 9e70fe330568262b8611661a3f44c0b1fc02b7cc

    // debugging code
    if (verb) {
      sf_warning("number of frames = %d",nframes);
      sf_warning("width = %d",width);
      sf_warning("height= %d",height);
      sf_warning("cap.get(CAP_PROP_FPS)= %f",writer.get(CAP_PROP_FPS));
      sf_warning("fps= %f",fps);
    }

    float bi, gi, ri;


    double bmin, bmax;
    double gmin, gmax;
    double rmin, rmax;
    // main loop over each frame in video 
    for (int it=0; it<nt; ++it) {

      // fill this frame with values
      for (int iz=0; iz<nz; ++iz) {
        for (int ix=0; ix<nx; ++ix) {
         sf_floatread(&bi,1,Fb1);
         sf_floatread(&gi,1,Fb2);
         sf_floatread(&ri,1,Fb3);
         b.at<float>(ix,iz)=bi;
         g.at<float>(ix,iz)=gi;
         r.at<float>(ix,iz)=ri;
        }
      }
      
      // scale values between zero and one 
      //cv::minMaxLoc(b, &bmin, &bmax);
      //cv::minMaxLoc(g, &gmin, &gmax);
      //cv::minMaxLoc(r, &rmin, &rmax);
      //b=(b-bmin)/(bmax-bmin);
      //g=(g-gmin)/(gmax-gmin);
      //r=(r-rmin)/(rmax-rmin);


      bands[0]=b*255.0;
      bands[1]=g*255.0;
      bands[2]=r*255.0;
      merge(bands,temp_frame);
      //sf_warning("type of temp_frame = %d",temp_frame.type());
      temp_frame.convertTo(fin_img, CV_8UC3);

      //sf_warning("number of channels in temp_frame = %d",temp_frame.channels()); 
      //sf_warning("rows in temp_frame = %d",temp_frame.rows); 
      //sf_warning("cols in temp_frame = %d",temp_frame.cols); 
      //plot_image(temp_frame);


    


      // place next nx*nz values in each channel 
      //channels.push_back(b);
      //channels.push_back(g);
      //channels.push_back(r);

      // merge channels into multichannel frame
<<<<<<< HEAD
      merge(channels,temp_frame);

      
       
  
      writer.write(temp_frame);
=======
      //merge(channels,temp_frame);
       

      writer.write(fin_img);

>>>>>>> 9e70fe330568262b8611661a3f44c0b1fc02b7cc


    }

    // release the kraken 
    //free(b);
    //free(g);
    //free(r);

    return 0;
}



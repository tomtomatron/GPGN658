#include <iostream>
#include <valarray>
#include "rsf.hh"

#include <opencv2/videoio.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

/*

Purpose: A wrapper for cv::pyrUp and cv::pyrDown from OpenCV package 

Inputs:
string src   = source image in .rsf format
string dst   = destination image in .rsf format
bool   verb  = verbose output?  (default is false)
bool   up    = upscaling image? (default is false) 
bool   lap   = want laplacian pyramid at this level? (default is false)

TODO 
int    go_n  = go n levels up or down                (default is one)
int boundary = type of boundary conditions represented as a cv::BorderTypes
               (default is a reflected image across boundary)
filt_type = type of filter (default is Gaussian) 
filt_size = size of filter in samples, must be odd. (default is 5-by-5)

Outputs:
dst contains the upscaled or downscaled image 

Notes:
(see OpenCV documentation for cv::BorderTypes)
boundary type options:
boundary = 0  ->  cv::BORDER_CONSTANT
boundary = 1  ->  cv::BORDER_REPLICATE
boundary = 2  ->  cv::BORDER_REFLECT
boundary = 3  ->  cv::BORDER_WRAP
boundary = 4  ->  cv::BORDER_REFLECT_101 (default)
boundary = 16 ->  cv::BORDER_ISOLATED

*/

using namespace std;

int main(int argc, char* argv[])
{

    /*if (argc < 2) {
        std::cerr << "Must specify input file." << std::endl;
        return 1;
    }*/

    // user inputs to add later if needed
    bool verb, up, lap;
    int boundary=cv::BORDER_REFLECT_101;
    bool is2D=false; // is RSF file 2D?
    int c(0),c1(0);

    // initialize
    sf_init(argc,argv);                 // RSF   
    sf_file Fsrc=NULL, Fdst=NULL;       // I/O rsf files
    sf_axis ax, az, at, axo, azo, ato;  // axis

    // input flag check 
    if(! sf_getbool("verb",&verb)) verb=false;          /* is verbose output? */
    if(! sf_getbool("up",&up)) up=false;                /* is upscaling? */
    if(! sf_getbool("lap",&lap)) lap=false;              /* is Laplacian? */

    // rsf files
    Fsrc = sf_input ("in");   /* standard input */
    Fdst = sf_output ("out"); /* standard output */ 

    // input axis
    ax=sf_iaxa(Fsrc,1); if(verb) sf_raxa(ax);
    az=sf_iaxa(Fsrc,2); if(verb) sf_raxa(az);
    at=sf_iaxa(Fsrc,3); if(verb) sf_raxa(at);
    int nx(sf_n(ax));
    int nz(sf_n(az));
    int nt(sf_n(at));
    if (verb) sf_warning("nx=%d,nz=%d,nt=%d",nx,nz,nt);
    float ox(sf_o(ax));
    float oz(sf_o(az));
    float ot(sf_o(at));
    if (verb) sf_warning("ox=%f,oz=%f,ot=%f",ox,oz,ot);
    float dx(sf_d(ax));
    float dz(sf_d(az));
    float dt(sf_d(at));
    if (verb) sf_warning("dx=%f,dz=%f,dt=%f",dx,dz,dt);

    // image destination
    float *dst;
    float *src_image, *dst_image;
    int nxo,nzo,nto;
    float dxo,dzo,dto;
    float oxo(ox),ozo(oz),oto(ot);
    dto=dt;
    nto=nt;
    if (nt==0) { 
      is2D=true;
      nto=1;
    }
    // compute sizes and warn of odd sizes
    if (lap) {
      nxo=nx;
      nzo=nz;
      dxo=dx;
      dzo=dz;
      if (verb) sf_warning("Going Laplacian!");
      if (verb) sf_warning("Preserving size!");
    } else if (up) {
      nxo=nx*2; 
      nzo=nz*2; 
      dxo=dx/2;
      dzo=dz/2;
      if (verb) sf_warning("Going up!");
    } else {
      nxo=nx/2;
      nzo=nz/2;
      dxo=dx*2;
      dzo=dz*2;
      if (verb) sf_warning("Going down!");
      if (nxo%2 != 0) { 
        sf_warning("The resulting x dimension is odd\n");
        sf_warning("(ambiguous image size if you upscale after downscaling further)");
      }
      if (nzo%2 != 0) {
        sf_warning("The resulting z dimension is odd\n");
        sf_warning("(ambiguous image size if you upscale after downscaling further)");
      }
    // check if size of resulting image is ridiculous
    if (nxo<1 || nzo<1) {
      sf_warning("\n\nSize of resulting image in pyramid is less than one. Not cool.\n");
      sf_error("Please don't downscale this far.");
    }
    }

    // axis for output rsf file
    axo=sf_maxa(nxo,oxo,dxo); sf_setlabel(axo,"x");
    azo=sf_maxa(nzo,ozo,dzo); sf_setlabel(azo,"z");
    ato=sf_maxa(nto,oto,dto); sf_setlabel(ato,"t");
    sf_oaxa(Fdst,axo,1);
    sf_oaxa(Fdst,azo,2);
    sf_oaxa(Fdst,ato,3);
    if (verb) sf_warning("nxo=%d,nzo=%d,nto=%d",nxo,nzo,nto);

    // allocate Mat object and float arrays 
    cv::Mat src_mat(nz,nx,CV_32F);
    cv::Mat dst_mat(nzo,nxo,CV_32F);
    dst      = sf_floatalloc(nxo*nzo*nto);
    src_image= sf_floatalloc(nx*nz*nt);
    dst_image= sf_floatalloc(nxo*nzo*nto);

    // main loop over time axis (not optimized)
    for (int it=0; it<nto; ++it) {

			// read source from RSF
      sf_floatread (src_image, nx*nz, Fsrc);

      // place source image into Mat object
      // TODO: find a way to eliminate this loop
      c1=0;
      for (int iz=0; iz<nz; ++iz) { 
        for (int ix=0; ix<nx; ++ix) { 
          src_mat.at<float>(iz,ix)=src_image[c1];
          c1++;
        }
      }

      // upscale or downscale in pyramid 
      if (lap) {

        // compute next level down from this level
        cv::pyrDown(src_mat,dst_mat,cv::Size(),boundary); 

        // upscale once
        cv::pyrUp(dst_mat,dst_mat,cv::Size(nxo,nzo),boundary); 

        // subtract from this level (DoG ~ LoG)
        dst_mat=src_mat-dst_mat;

      } else if (up) {
        cv::pyrUp(src_mat,dst_mat,cv::Size(nxo,nzo),boundary);
      } else {
        cv::pyrDown(src_mat,dst_mat,cv::Size(nxo,nzo),boundary);
      }

      // get values in dst_mat object into float array 
      // TODO: find a way to eliminate this loop
      for (int iz=0; iz<nzo; ++iz) {
        for (int ix=0; ix<nxo; ++ix) {
          dst[c]=dst_mat.at<float>(iz,ix);
          c++;
        } 
      } 
    }

    // for debugging
    if (verb) sf_warning("type of dst_image = %d",dst_mat.type());
    if (verb) sf_warning("Is machine little endian? %d",sf_endian());

    // write data to destination file
    sf_floatwrite(dst,nxo*nzo*nto,Fdst);
    
    // clean up 
    sf_close();
    free(dst);
    free(dst_image);
    free(src_image);

    exit(0);
}


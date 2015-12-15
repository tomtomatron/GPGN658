//
//  test.cpp
//  MotionMag
//
//  Created by Thomas Rapstine on 9/24/15.
//  Copyright © 2015 Thomas Rapstine. All rights reserved.
//
#include <iostream>
#include "boost/timer.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/core.hpp"
#include "opencv2/highgui.hpp"
#include "test.hpp"
#include "utilities.hpp"

using namespace std;
using namespace cv;



//Testing ability to read and write a video from webcam
void test_read_write_webcam(void){
    string ofile("/Users/thomasrapstine/data/GeoDrone/test_read_write_webcam.mp4");

    //set VideoWriter parameters based on webcam
    cv::VideoCapture cap(0);
    cv::VideoWriter writer;
    double width = cap.get(CV_CAP_PROP_FRAME_WIDTH);
    double height = cap.get(CV_CAP_PROP_FRAME_HEIGHT);
    int fcc = CV_FOURCC('S', 'V', 'Q','3'); //four character code to write video
    int fps(20);
    cv::Size frameSize(width,height);
    string windowName="my_window";

    writer=cv::VideoWriter(ofile,fcc,fps,frameSize);
    if(!writer.isOpened()){
        cerr << "writer not opened" << endl;
        getchar(); //wait for user to press key
        exit(EXIT_FAILURE);
    }
    
    cv::Mat frame(3,3,CV_32F);
    float *a;
    a=&frame.at<float>();
    
    

    //record webcam and write each frame to video
    int c=0;
    while (1) {

        bool bSuccess = cap.read(frame); // read a new frame from camera FEED
                
        if (!bSuccess) //test if frame successfully read
        {
            cout << "ERROR READING FRAME FROM CAMERA FEED" << endl;
            break;
        }

        writer.write(frame);
        
        cv::imshow(windowName, frame); //show the frame in "MyVideo" window
        
        //listen for 10ms for a key to be pressed
        switch(cv::waitKey(10)){
            case 27:
                //'esc' has been pressed (ASCII value for 'esc' is 27)
                //exit program.
                exit(EXIT_FAILURE);
        }
        ++c;
    }
    cout << frame.type() << endl;

}

//Testing ability to write a video that is all red
void test_write_red(void){
    string ofile("/Users/thomasrapstine/data/GeoDrone/test_write_red.mp4");
    
    //set VideoWriter parameters based on webcam
    cv::VideoCapture cap(0);
    cv::VideoWriter writer;
    double width = cap.get(CV_CAP_PROP_FRAME_WIDTH);
    double height = cap.get(CV_CAP_PROP_FRAME_HEIGHT);
    int fcc = CV_FOURCC('X', '2', '6','4'); //four character code to write video
    int fps(20);
    cv::Size frameSize(width,height);
    string windowName="my_window";
    
    writer=cv::VideoWriter(ofile,-1,fps,frameSize);
    if(!writer.isOpened()){
        cerr << "writer not opened" << endl;
        getchar(); //wait for user to press key
        exit(EXIT_FAILURE);
    }
    
    cv::Mat frame(3,3,CV_32F);
    float *a;
    a=&frame.at<float>();
    
    Mat b = Mat::zeros(frameSize,CV_8UC1);
    Mat g = Mat::zeros(frameSize,CV_8UC1);
    Mat r = Mat::ones(frameSize,CV_8UC1);
    r*=255;
    
    vector<Mat> bands;
    bands.push_back(b);
    bands.push_back(g);
    bands.push_back(r);
    merge(bands,frame);
    
    
    //record webcam and write each frame to video
    int c=0;
    while (c<100) {
        
        while (frame.channels() != 3) {
            //do nothing
            
        }
        writer.write(frame);
        
        ++c;
    }
    cout << frame.type() << endl;
    
}


//Testing speed of pyramid computation for a variety of tests
void test_pyramid_speed() {
    
    //test parameters
    string file_input="/Users/thomasrapstine/data/GeoDrone/test_read_write_webcam.mp4";
    int max_pyramids(2E4);
    int max_level(9);
    int width(512);
    int height(512);
    
    test_pyramid();
    test_pyramid_time(20000,9,512,512);
    test_pyramid_time_range(max_pyramids, max_level, width, height);
    test_pyramid_time_video(file_input);
    
    exit(EXIT_SUCCESS);
}

//Test ability to build and understand an image pyramid
void test_pyramid(void){
    cout << "Testing ability to expand and collapse image pyramid" << endl;
    //get image (size must be divisible by 2^n)
    string file="/Users/thomasrapstine/data/GeoDrone/lena.png";
    
    Mat src = imread(file);
    //cv::Size size_image=src.size();
    //cout << size_image.height << "<- This is the height of src" << endl;
    //cout << size_image.width << "<- This is the width src" << endl;
    string windowName="myWindow";

    //build Gaussian pyramid
    if( !src.data )
    { printf(" No data! -- Exiting the program \n");
        exit(EXIT_FAILURE); }
    std::vector<cv::Mat> dst; //a vector of cv::Mat objects
    int maxlevel = get_maxlevel(src);
    cv::buildPyramid(src,dst,maxlevel);
    cout << "Size of pyramid: " << dst.size() << endl;
    
    //View each level of the pyramid
    for (int i=0; i<dst.size(); ++i)
    {
        cout << "At pyramid level = " << i << " | size = " << dst[i].size() << endl;
        plot_image(dst[i],"Image in pyramid");
    }
    
    //View each level of the pyramid upsized to original size
    int k;
    for (int i=0; i<dst.size(); ++i)
    {
        //plot_image(dst[i],"Image in pyramid");
        cout << dst[i].size() << " upsizing to original size: ";
        k=1;
        //upsize until pyramid level is same size as source image
        while (dst[i].cols<src.cols)
        {
            cv::pyrUp(dst[i],dst[i]);
            cout << k << ", ";
            k++;
        }
        cout << endl;
        plot_image(dst[i],"Resized");
    }
}


// Test ability to create a full Laplacian pyramid using lena.png image
void   test_pyramid_Laplacian(void) {
    cout << "Testing formation of Laplacian pyramid" << endl;
    
    // input image
    string file="/Users/thomasrapstine/data/GeoDrone/lena.png";
    Mat src = imread(file);
    Mat src_1, src_11;
    int nlevel=get_maxlevel(src)+1;
    nlevel=9;
    
    // Build Gaussian pyramid
    std::vector<Mat> G;
    Mat mat_temp;
    G.push_back(src); //first level in pyramid is source image
    cout << "Size of G[" << 0 << "] = " << G[0].size() << endl;
    for (int iL=1; iL<nlevel; ++iL) {
        // Downsample and store
        cv::pyrDown(G[iL-1],mat_temp);
        G.push_back(mat_temp);
        cout << "Size of G[" << iL << "] = " << G[iL].size() << endl;
    }
    
    // Build Laplacian pyramid
    std::vector<Mat> L;
    Mat up1, diff;
    for (int iL=0; iL<nlevel-1; ++iL) {
        
        // uplevel the image at the next level up
        cv::pyrUp(G[iL+1],up1);
        
        // subtract from this level
        diff=G[iL]-up1;
        
        // store in L
        L.push_back(diff);
        
        cout << "Size of L[" << iL << "] = " << L[iL].size() << endl;
        
        //plot_image(L[iL],"Laplacian!");

    }
    
    exit(EXIT_SUCCESS);
}

// Test ability to create a 3 level Laplacian pyramid using lena.png image
// investigating effects of interpolation method
void test_pyramid_laplacian_simple() {
    
    // input image
    string file="/Users/thomasrapstine/data/GeoDrone/lena.png";  //air
    //string file="/Users/trap/data/GeoDrone/lena.png";   //beast
    Mat src = imread(file);
    
    //Gaussian pyramid (max level = 3)
    cout << "here1" << endl;
    Mat G0 = src;
    cout << "here2" << endl;
    Mat G1,G2,G3;
    int interp_type=CV_INTER_LINEAR;
    //cv::pyrDown(G0 ,G1);
    //cv::pyrDown(G1 ,G2);
    //cv::pyrDown(G2 ,G3);
    
    //try resizing instead of pyrDown()
    cv::resize(G0,G1,Size(),0.5,0.5,interp_type);
    cv::resize(G1,G2,Size(),0.5,0.5,interp_type);
    cv::resize(G2,G3,Size(),0.5,0.5,interp_type);
    
    Mat G11, G21, G31;
    //cv::pyrUp(G3,G31);
    //cv::pyrUp(G2,G21);
    //cv::pyrUp(G1,G11);
    
    //try resizing instead of pyrUp()
    cv::resize(G3,G31,Size(),2.0,2.0,interp_type);
    cv::resize(G2,G21,Size(),2.0,2.0,interp_type);
    cv::resize(G1,G11,Size(),2.0,2.0,interp_type);
    
    // check sizes
    cout << "size of G0 " << G0.size() << endl;
    cout << "size of G1 " << G1.size() << endl;
    cout << "size of G2 " << G2.size() << endl;
    cout << "size of G11 " << G11.size() << endl;
    cout << "size of G21 " << G21.size() << endl;
    cout << "size of G31 " << G31.size() << endl;
    
    //Laplacian (residuals)
    Mat L0, L1, L2;
    L0=G0-G11;
    L1=G1-G21;
    L2=G2-G31;
    
    // upscale each level of Laplacian to source size
    Mat L00, L11, L22, G33;
    // up 0
    L00=L0;
    // up 1
    //cv::pyrUp(L1 ,L11);
    cv::resize(L1,L11,G0.size(),0,0,interp_type);
    // up 2
    //cv::pyrUp(L2 ,L22);
    //cv::pyrUp(L22,L22);
    cv::resize(L2,L22,G0.size(),0,0,interp_type);
    // up 3
    //cv::pyrUp(G3 ,G33);
    //cv::pyrUp(G33,G33);
    //cv::pyrUp(G33,G33);
    cv::resize(G3,G33,G0.size(),0,0,interp_type);
    
    // check sizes
    cout << "size of L00 " << L00.size() << endl;
    cout << "size of L11 " << L11.size() << endl;
    cout << "size of L22 " << L22.size() << endl;
    cout << "size of G33 " << G33.size() << endl;
    
    // reconstruct image
    Mat src_r=L00+L11+L22+G33;
    Mat dif = src-src_r;
    //cout << "Reconstruction error for each channel: " << sum(dif) << endl;
    
    plot_image(G0,"G0");
    plot_image(G1,"G1");
    plot_image(G2,"G2");
    plot_image(G3,"G3");
    
    plot_image(G11,"G11");
    plot_image(G21,"G21");
    plot_image(G31,"G31");
    
    plot_image(L0,"L0");
    plot_image(L1,"L1");
    plot_image(L2,"L2");
    
    plot_image(L00,"L00");
    plot_image(L11,"L11");
    plot_image(L22,"L22");
    plot_image(G33,"G33");
    
    plot_image(src_r,"Reconstructed");
    plot_image(src  ,"Original");
    //plot_image(dif  ,"Difference");
    
    exit(EXIT_SUCCESS);
}



//Test timing of forming multiple pyramids.
//Returns elapsed time.
double test_pyramid_time(int num_pyramids, int num_levels, int width, int height)
{
    string file="/Users/thomasrapstine/data/GeoDrone/lena.png";
    cv::Mat src = cv::imread(file);
    cv::resize(src,src,Size(width,height));
    if (num_levels > get_maxlevel(src))
    {
        cerr << "num_levels greater than max level possible in pyramid";
        exit(EXIT_FAILURE);
    }

    std::vector<cv::Mat> dst; //a vector of cv::Mat objects
    
    //start clock
    boost::timer t;
    for (int i=0; i<num_pyramids; ++i)
    {
        cv:buildPyramid(src,dst,num_levels);
    }
    //stop clock
    double elapsed_time=t.elapsed();
    printf("It took %f seconds to build %d %d-level [%dx%d] pyramids\n"
           ,elapsed_time,num_pyramids,num_levels,width,height);
    return elapsed_time;
}

//Test timing of forming a range of pyramids.
void test_pyramid_time_range(int max_pyramids, int max_level, int width, int height)
{
    double elapsed_time;
    int num_levels  =max_level;
    int num_pyramids=100;
    while (num_levels>0)
    {
        elapsed_time = test_pyramid_time(num_pyramids,num_levels,width,height);
        --num_levels;
        
    }
    num_levels=max_level;
    while (num_pyramids<=max_pyramids)
    {
        elapsed_time = test_pyramid_time(num_pyramids,num_levels,width,height);
        num_pyramids*=10;
    }
}

//Test how long it takes to compute video, prints time
double test_pyramid_time_video(string file_input) {
    
    double elapsedtime;
    Mat src;
    std::vector<Mat> dst;
    
    VideoCapture cap(file_input);
    int num_frames = cap.get(CAP_PROP_FRAME_COUNT);
    cout << num_frames << endl;
    
    boost::timer t;
    for (int i; i<num_frames; ++i)
    {
        cap >> src;
        //cv:buildPyramid(src, dst, 2);
    }
    elapsedtime = t.elapsed();
    cout << "It took " << elapsedtime << " seconds to build pyramids for " <<
            num_frames << " " << src.size()  << " frames" << endl;
    return elapsedtime;
}

//Test ability to perform a 1D DFT
void test_dft_1D()
{
    //Create synthetic 1D signal
    
    //Perform 1D DFT
    
    //Display signal, amplitude, and phase spectra
    
}


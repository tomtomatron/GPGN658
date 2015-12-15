//
//  utilities.cpp
//  MotionMag
//
//  Created by Thomas Rapstine on 9/25/15.
//  Copyright © 2015 Thomas Rapstine. All rights reserved.
//

#include <iostream>
#include <opencv2/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>

#include "utilities.hpp"

using namespace std;
using namespace cv;

//read video file into Mat
//plot image in a new window
void plot_image(cv::Mat image, std::string windowName)
{
    cv::namedWindow( windowName, CV_WINDOW_AUTOSIZE );
    cv::imshow(windowName,image);
    while (1)
    {
        //listen for 10ms for a key to be pressed
        switch(cv::waitKey(10)){
            case 27:
                //'esc' has been pressed (ASCII value for 'esc' is 27)
                //exit program.
                return;
        }
    }
}

//plays each frame of a video file
void play_video(string filename) {
    Mat temp_image;
    
    //capture video from file
    int fourcc = CV_FOURCC('H','2','6','4');
    VideoCapture cap(filename);

    if (!cap.isOpened()){ cerr << "video file not open" << endl; }
    double fps    = cap.get(CV_CAP_PROP_FPS);
    int num_frames= cap.get(CV_CAP_PROP_FRAME_COUNT);
    int codec     = cap.get(CV_CAP_PROP_FOURCC);
    cout << "Number of frames = " << num_frames << endl;
    cout << "framerate = " << fps << endl;

    int ex = static_cast<int>(cap.get(CV_CAP_PROP_FOURCC));
    
    //create frame
    cvNamedWindow("my_video",CV_WINDOW_AUTOSIZE);
    
    //play video
    int i=1;
    int ndropped=0;
    while (i<num_frames) {
        
        //bool success = cap.read(temp_image);
        cap >> temp_image;
        //cap.retrieve(temp_image);

        //cout << i << endl;
        int x = temp_image.rows;
        //int y = temp_image.rows;
        //cout << "rows = " << temp_image.rows << endl;
        //cout << "cols = " << temp_image.cols << endl;
        if (x == 0) {
          cout << "number of rows in this frame is zero!!!" <<  "skipping this biatch!" << endl;
            ++ndropped;
        } else {
          imshow("my_window", temp_image);
          if(waitKey(1/fps) >= 0 || i>=num_frames) break;
        }
        ++i;
    }
    cout << "ndropped = " << ndropped << endl;
    cout << "i = " << i << endl;
    //clean up
    cap.release();
    destroyAllWindows();
}

//compute maximum level in image pyramid
//image at max level in pyramid is a 1 x 1 pixel
int get_maxlevel(cv::Mat image)
{
    cv::Size size_image = image.size();
    int maxlevel = std::ceil(std::log2(max(size_image.height,size_image.width)));
    return maxlevel;
}

//compute number of frames in a video that are not dropped
int get_num_frames_dropped(string filename, bool verb) {
    Mat temp_image;
    
    //capture video from file
    VideoCapture cap(filename);
    
    if (!cap.isOpened()){ cerr << "video file not open" << endl; }
    int num_frames= cap.get(CV_CAP_PROP_FRAME_COUNT);
    

    // loop through video frames
    int i=1;
    int ndropped=0;
    while (i<num_frames) {
        
        //bool success = cap.read(temp_image);
        cap >> temp_image;
        //cap.retrieve(temp_image);
        
        //cout << i << endl;
        int x = temp_image.rows;
        //int y = temp_image.rows;
        //cout << "rows = " << temp_image.rows << endl;
        //cout << "cols = " << temp_image.cols << endl;
        if (x == 0) {
            if (verb) cout << "found dropped frame" << endl;
            ++ndropped;
        }
        ++i;
    }
    if (verb) {
      cout << "ndropped = " << ndropped << endl;
      cout << "i = " << i << endl;
    }
    return ndropped;
}

//get pyramid for a image object
//Need to check if this is copying image
std::vector<cv::Mat>  get_pyramid(cv::Mat image){
    std::vector<cv::Mat> dst;
    cv::buildPyramid(image,dst,get_maxlevel(image));
    return dst;
}

//get pyramid for each frame in a VideoCapture object
std::vector<cv::Mat> get_pyramid(cv::VideoCapture cap)
{
    std::vector<cv::Mat> dst;
    Mat frame;
    int num_frames = cap.get(CAP_PROP_FRAME_COUNT);
    for (int i=0; i<num_frames; ++i)
    {
        cap >> frame;
       //store current frame in pyramid
    }
    return dst;
}




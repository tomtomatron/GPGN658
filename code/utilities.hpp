//
//  utilities.hpp
//  MotionMag
//
//  Created by Thomas Rapstine on 9/25/15.
//  Copyright © 2015 Thomas Rapstine. All rights reserved.
//

#ifndef utilities_hpp
#define utilities_hpp

#include <stdio.h>
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>

using namespace std;

//plot an image
void plot_image(cv::Mat image, string windowName="my_window");

//play a video file
void play_video(string filename);



//get maximum level in an image pyramid
int get_maxlevel(cv::Mat image);

//get number of frames in a video file that were dropped during video recording
int get_num_frames_dropped(string filename, bool verb=false);


//get pyramid for a Mat object
std::vector<cv::Mat> get_pyramid(cv::Mat image);

//get pyramid for each frame in a VideoCapture object
std::vector<cv::Mat> get_pyramid(cv::VideoCapture cap);







#endif /* utilities_hpp */

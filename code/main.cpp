//
//  main.cpp
//  MotionMag
//
//  Created by Thomas Rapstine on 9/24/15.
//  Copyright © 2015 Thomas Rapstine. All rights reserved.
//  This is the main for the MotionMag XCode project
//  Use this main to test OpenCV methods


#include <iostream>
#include <stdio.h>
#include "test.hpp"
#include "utilities.hpp"

//OpenCV
#include "opencv2/core/core.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

//M8R
#include <valarray>
//#include "rsf.hh"

using namespace std;
using namespace cv;

int main(int argc, char* argv[]) {

    cout << "Hello World" << endl;
    

    //test_write_red();
    test_read_write_webcam();
    //test something here
    //test_pyramid_Laplacian();
    //test_pyramid_laplacian_simple();
    //test_pyramid_time_video(Fv);
    
    return 0;
}

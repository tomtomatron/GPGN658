//
//  test.hpp
//  MotionMag
//
//  Created by Thomas Rapstine on 9/24/15.
//  Copyright © 2015 Thomas Rapstine. All rights reserved.
//

#ifndef test_hpp
#define test_hpp

#include <stdio.h>

//Testing ability to read and write a video from webcam
void   test_read_write_webcam();

//Testing ability to write a video that is all red
void   test_write_red();

//Testing speed of pyramid computation for a variety of tests
void   test_pyramid_speed();

//Test ability to build and understand an image pyramid
void   test_pyramid();

// Test ability to create full Laplacian pyramid using lena.png image
void   test_pyramid_Laplacian();

// Test ability to create a 3 level Laplacian pyramid using lena.png image
void test_pyramid_laplacian_simple();

//Test timing of forming multiple pyramids.
//Returns elapsed time.
double test_pyramid_time(int num_pyramids, int num_levels=10,
                         int width=512   , int height=512);

//Test timing of forming a range of pyramids.
void   test_pyramid_time_range(int max_pyramids, int max_level=10,
                               int width=512   , int height=512);

//Test how long it takes to compute video pyramid, prints time
double test_pyramid_time_video(std::string file_input);

//Test ability to perform a 1D DFT (not passed)
void   test_dft_1D();

#endif /* test_hpp */

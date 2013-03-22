/****************************************************************************
*                                                                           *
*  OpenNI 1.x Alpha                                                         *
*  Copyright (C) 2011 PrimeSense Ltd.                                       *
*                                                                           *
*  This file is part of OpenNI.                                             *
*                                                                           *
*  OpenNI is free software: you can redistribute it and/or modify           *
*  it under the terms of the GNU Lesser General Public License as published *
*  by the Free Software Foundation, either version 3 of the License, or     *
*  (at your option) any later version.                                      *
*                                                                           *
*  OpenNI is distributed in the hope that it will be useful,                *
*  but WITHOUT ANY WARRANTY; without even the implied warranty of           *
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the             *
*  GNU Lesser General Public License for more details.                      *
*                                                                           *
*  You should have received a copy of the GNU Lesser General Public License *
*  along with OpenNI. If not, see <http://www.gnu.org/licenses/>.           *
*                                                                           *
****************************************************************************/
//---------------------------------------------------------------------------
// Includes
//---------------------------------------------------------------------------
#include <math.h>
#include <time.h>
#include <string>
#include <sstream>

#include <boost/archive/iterators/base64_from_binary.hpp>
#include <boost/archive/iterators/ostream_iterator.hpp>
#include <boost/archive/iterators/transform_width.hpp>

#include <opencv/cv.h>
#include <opencv/highgui.h>



#include "SceneDrawer.h"
#include "context.h"
#include "base64.h"
#include "ami_environment.h"
#include "util/Worker.h"
#include "util/StopWatch.h"

#ifndef USE_GLES
#if (XN_PLATFORM == XN_PLATFORM_MACOSX)
    #include <GLUT/glut.h>
#else
    #include <GL/glut.h>
#endif
#else
    #include "opengles.h"
#endif

using namespace std;

static const std::string base64_chars =
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789+/";

extern xn::UserGenerator g_UserGenerator;
extern xn::DepthGenerator g_DepthGenerator;

extern XnBool g_bDrawBackground;
extern XnBool g_bDrawPixels;
extern XnBool g_bDrawSkeleton;
extern XnBool g_bPrintID;
extern XnBool g_bPrintState;

extern XnBool g_bPrintFrameID;
extern XnBool g_bMarkJoints;

#define MIN_DELAY_BETWEEN_SKELETON_MEASUREMENT 10 //ms
#define MIN_DELAY_BETWEEN_RGB_MEASUREMENT 1000
#define MIN_DELAY_BETWEEN_DEPTH_MEASUREMENT 1000


class DataThrottle {
public:
	bool running;
	long min_delay;
	util::StopWatch sw;

	/** min delay is in milliseconds*/
	DataThrottle(long min_delay): running(false), min_delay(min_delay) {}
	bool CanSend() {
		return !running && (sw.GetState() == util::StopWatch::STATE_READY || sw.GetSplitTime() >= min_delay);
	}

	void MarkSend() {
		if (sw.GetState() == util::StopWatch::STATE_READY) {
			sw.Start();
		} else {
			sw.ReStart();
		}
	}
};

DataThrottle skeleton_throttle(MIN_DELAY_BETWEEN_SKELETON_MEASUREMENT);
DataThrottle rgb_throttle(MIN_DELAY_BETWEEN_RGB_MEASUREMENT);
DataThrottle depth_throttle(MIN_DELAY_BETWEEN_DEPTH_MEASUREMENT);


#ifdef USE_MEMCACHE
#include <libmemcached/memcached.h>
extern memcached_st* g_MemCache;

static util::Worker worker(200);

static void SendCompleted(util::Runnable* r, void* arg) {
	DataThrottle* dt = static_cast<DataThrottle*>(arg);
	delete r;
	dt->running = false;
}

class Send : public util::Runnable {
public:
	char* buffer;
	Send(char* b) : buffer(b) {}
	~Send() {
		free(buffer);
	}

	void Run() {
		memcached_return rc;
		size_t len = strlen(buffer);
		rc = memcached_set(g_MemCache,
				"measurements", strlen("measurements"),
				buffer, len,
				(time_t)0, (uint32_t)0);

		if (rc != MEMCACHED_SUCCESS) {
			printf("Could NOT send to memcache. I'm very very sad :-( :-( :-(\n");
		} else {
			printf("I can send %5.3f kB to memcache. HURRAY!! :-) :-) :-)\n", len / 1024.0);
		}
	}

};
#endif



void SceneDrawerInit() {
}

#include <map>
std::map<XnUInt32, std::pair<XnCalibrationStatus, XnPoseDetectionStatus> > m_Errors;
void XN_CALLBACK_TYPE MyCalibrationInProgress(xn::SkeletonCapability& /*capability*/, XnUserID id, XnCalibrationStatus calibrationError, void* /*pCookie*/)
{
    m_Errors[id].first = calibrationError;
}
void XN_CALLBACK_TYPE MyPoseInProgress(xn::PoseDetectionCapability& /*capability*/, const XnChar* /*strPose*/, XnUserID id, XnPoseDetectionStatus poseError, void* /*pCookie*/)
{
    m_Errors[id].second = poseError;
}

unsigned int getClosestPowerOfTwo(unsigned int n)
{
    unsigned int m = 2;
    while(m < n) m<<=1;

    return m;
}
GLuint initTexture(void** buf, int& width, int& height)
{
    GLuint texID = 0;
    glGenTextures(1,&texID);

    width = getClosestPowerOfTwo(width);
    height = getClosestPowerOfTwo(height);
    *buf = new unsigned char[width*height*4];
    glBindTexture(GL_TEXTURE_2D,texID);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    return texID;
}

GLfloat texcoords[8];
void DrawRectangle(float topLeftX, float topLeftY, float bottomRightX, float bottomRightY)
{
    GLfloat verts[8] = {	topLeftX, topLeftY,
        topLeftX, bottomRightY,
        bottomRightX, bottomRightY,
        bottomRightX, topLeftY
    };
    glVertexPointer(2, GL_FLOAT, 0, verts);
    glDrawArrays(GL_TRIANGLE_FAN, 0, 4);

    //TODO: Maybe glFinish needed here instead - if there's some bad graphics crap
    glFlush();
}
void DrawTexture(float topLeftX, float topLeftY, float bottomRightX, float bottomRightY)
{
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    glTexCoordPointer(2, GL_FLOAT, 0, texcoords);

    DrawRectangle(topLeftX, topLeftY, bottomRightX, bottomRightY);

    glDisableClientState(GL_TEXTURE_COORD_ARRAY);
}

XnFloat Colors[][3] =
{
    {0,1,1},
    {0,0,1},
    {0,1,0},
    {1,1,0},
    {1,0,0},
    {1,.5,0},
    {.5,1,0},
    {0,.5,1},
    {.5,0,1},
    {1,1,.5},
    {1,1,1}
};
XnUInt32 nColors = 10;
#ifndef USE_GLES
void glPrintString(void *font, char *str)
{
    int i,l = (int)strlen(str);

    for(i=0; i<l; i++)
    {
        glutBitmapCharacter(font,*str++);
    }
}
#endif

bool DrawLimb(XnUserID player, XnSkeletonJoint eJoint1, XnSkeletonJoint eJoint2)
{
    if (!g_UserGenerator.GetSkeletonCap().IsTracking(player))
    {
        printf("not tracked!\n");
        return true;
    }

    if (!g_UserGenerator.GetSkeletonCap().IsJointActive(eJoint1) ||
        !g_UserGenerator.GetSkeletonCap().IsJointActive(eJoint2))
    {
        return false;
    }

    XnSkeletonJointPosition joint1, joint2;
    g_UserGenerator.GetSkeletonCap().GetSkeletonJointPosition(player, eJoint1, joint1);
    g_UserGenerator.GetSkeletonCap().GetSkeletonJointPosition(player, eJoint2, joint2);

    if (joint1.fConfidence < 0.5 || joint2.fConfidence < 0.5)
    {
        return true;
    }

    XnPoint3D pt[2];
    pt[0] = joint1.position;
    pt[1] = joint2.position;

    g_DepthGenerator.ConvertRealWorldToProjective(2, pt, pt);
#ifndef USE_GLES
    glVertex3i(pt[0].X, pt[0].Y, 0);
    glVertex3i(pt[1].X, pt[1].Y, 0);
#else
    GLfloat verts[4] = {pt[0].X, pt[0].Y, pt[1].X, pt[1].Y};
    glVertexPointer(2, GL_FLOAT, 0, verts);
    glDrawArrays(GL_LINES, 0, 2);
    glFlush();
#endif

    return true;
}

static const float DEG2RAD = 3.14159/180;

void drawCircle(float x, float y, float radius)
{
   glBegin(GL_TRIANGLE_FAN);

   for (int i=0; i < 360; i++)
   {
      float degInRad = i*DEG2RAD;
      glVertex2f(x + cos(degInRad)*radius, y + sin(degInRad)*radius);
   }

   glEnd();
}
void DrawJoint(XnUserID player, XnSkeletonJoint eJoint)
{
    //return;
    if (!g_UserGenerator.GetSkeletonCap().IsTracking(player))
    {
        printf("not tracked!\n");
        return;
    }

    if (!g_UserGenerator.GetSkeletonCap().IsJointActive(eJoint))
    {
        return;
    }

    XnSkeletonJointPosition joint;
    g_UserGenerator.GetSkeletonCap().GetSkeletonJointPosition(player, eJoint, joint);

    if (joint.fConfidence < 0.5)
    {
        return;
    }

    XnPoint3D pt;
    pt = joint.position;

    g_DepthGenerator.ConvertRealWorldToProjective(1, &pt, &pt);

    drawCircle(pt.X, pt.Y, 2);
}

const XnChar* GetCalibrationErrorString(XnCalibrationStatus error)
{
    switch (error)
    {
    case XN_CALIBRATION_STATUS_OK:
        return "OK";
    case XN_CALIBRATION_STATUS_NO_USER:
        return "NoUser";
    case XN_CALIBRATION_STATUS_ARM:
        return "Arm";
    case XN_CALIBRATION_STATUS_LEG:
        return "Leg";
    case XN_CALIBRATION_STATUS_HEAD:
        return "Head";
    case XN_CALIBRATION_STATUS_TORSO:
        return "Torso";
    case XN_CALIBRATION_STATUS_TOP_FOV:
        return "Top FOV";
    case XN_CALIBRATION_STATUS_SIDE_FOV:
        return "Side FOV";
    case XN_CALIBRATION_STATUS_POSE:
        return "Pose";
    default:
        return "Unknown";
    }
}
const XnChar* GetPoseErrorString(XnPoseDetectionStatus error)
{
    switch (error)
    {
    case XN_POSE_DETECTION_STATUS_OK:
        return "OK";
    case XN_POSE_DETECTION_STATUS_NO_USER:
        return "NoUser";
    case XN_POSE_DETECTION_STATUS_TOP_FOV:
        return "Top FOV";
    case XN_POSE_DETECTION_STATUS_SIDE_FOV:
        return "Side FOV";
    case XN_POSE_DETECTION_STATUS_ERROR:
        return "General error";
    default:
        return "Unknown";
    }
}

char* JointToJSON(XnUserID player, XnSkeletonJoint eJoint, const char *name)
{
    XnSkeletonJointPosition joint;
    g_UserGenerator.GetSkeletonCap().GetSkeletonJointPosition(player, eJoint, joint);
    XnPoint3D pt = joint.position;
    char* buf = (char*) malloc(100 * sizeof(char));
    snprintf(buf, 100, "\"%s\": {\"X\": %.2f, \"Y\": %.2f, \"Z\": %.2f}",
         name, pt.X, pt.Y, pt.Z);
    return buf;
}

char* JointTo2DJSON(XnUserID player, XnSkeletonJoint eJoint, const char *name)
{
    XnSkeletonJointPosition joint;
    g_UserGenerator.GetSkeletonCap().GetSkeletonJointPosition(player, eJoint, joint);
    XnPoint3D pt = joint.position;
    g_DepthGenerator.ConvertRealWorldToProjective(1, &pt, &pt);
    char* buf = (char*) malloc(100 * sizeof(char));
    snprintf(buf, 100, "\"%s\": {\"X\": %.2f, \"Y\": %.2f}",
             name, pt.X * 1280/640, pt.Y * 1024/480);
    return buf;
}

/*
 * Saves the skeleton data by deriving a JSON message and enqueueing it to
 * Kestrel, a message-queue system used to communicate with the rest of the
 * system.
 */
static void SaveSkeleton(XnUserID player, const char* player_name, const char* sensor_name)
{
#if USE_MEMCACHE
	char* buf = (char*) malloc(10000 * sizeof(char));
	char* head = JointToJSON(player, XN_SKEL_HEAD, "head");
	char* neck = JointToJSON(player, XN_SKEL_NECK, "neck");
	char* left_shoulder = JointToJSON(player, XN_SKEL_LEFT_SHOULDER, "left_shoulder");
	char* right_shoulder = JointToJSON(player, XN_SKEL_RIGHT_SHOULDER, "right_shoulder");
	char* left_elbow = JointToJSON(player, XN_SKEL_LEFT_ELBOW, "left_elbow");
	char* right_elbow = JointToJSON(player, XN_SKEL_RIGHT_ELBOW, "right_elbow");
	char* left_hand = JointToJSON(player, XN_SKEL_LEFT_HAND, "left_hand");
	char* right_hand = JointToJSON(player, XN_SKEL_RIGHT_HAND, "right_hand");
	char* torso = JointToJSON(player, XN_SKEL_TORSO, "torso");
	char* left_hip = JointToJSON(player, XN_SKEL_LEFT_HIP, "left_hip");
	char* right_hip = JointToJSON(player, XN_SKEL_RIGHT_HIP, "right_hip");
	char* left_knee = JointToJSON(player, XN_SKEL_LEFT_KNEE, "left_knee");
	char* right_knee = JointToJSON(player, XN_SKEL_RIGHT_KNEE, "right_knee");
	char* left_foot = JointToJSON(player, XN_SKEL_LEFT_FOOT, "left_foot");
	char* right_foot = JointToJSON(player, XN_SKEL_RIGHT_FOOT, "right_foot");

	char* head_2d = JointTo2DJSON(player, XN_SKEL_HEAD, "head");
	char* neck_2d = JointTo2DJSON(player, XN_SKEL_NECK, "neck");
	char* left_shoulder_2d = JointTo2DJSON(player, XN_SKEL_LEFT_SHOULDER, "left_shoulder");
	char* right_shoulder_2d = JointTo2DJSON(player, XN_SKEL_RIGHT_SHOULDER, "right_shoulder");
	char* left_elbow_2d = JointTo2DJSON(player, XN_SKEL_LEFT_ELBOW, "left_elbow");
	char* right_elbow_2d = JointTo2DJSON(player, XN_SKEL_RIGHT_ELBOW, "right_elbow");
	char* left_hand_2d = JointTo2DJSON(player, XN_SKEL_LEFT_HAND, "left_hand");
	char* right_hand_2d = JointTo2DJSON(player, XN_SKEL_RIGHT_HAND, "right_hand");
	char* torso_2d = JointTo2DJSON(player, XN_SKEL_TORSO, "torso");
	char* left_hip_2d = JointTo2DJSON(player, XN_SKEL_LEFT_HIP, "left_hip");
	char* right_hip_2d = JointTo2DJSON(player, XN_SKEL_RIGHT_HIP, "right_hip");
	char* left_knee_2d = JointTo2DJSON(player, XN_SKEL_LEFT_KNEE, "left_knee");
	char* right_knee_2d = JointTo2DJSON(player, XN_SKEL_RIGHT_KNEE, "right_knee");
	char* left_foot_2d = JointTo2DJSON(player, XN_SKEL_LEFT_FOOT, "left_foot");
	char* right_foot_2d = JointTo2DJSON(player, XN_SKEL_RIGHT_FOOT, "right_foot");

	char *context = get_context();

	timespec t;
	 clock_gettime(CLOCK_REALTIME, &t);
	snprintf((char*)buf, 10000,
		"{\"created_at\": %ld,"
		"\"context\": \"%s\","
		"\"sensor_type\": \"kinect\","
		"\"sensor_id\": \"%s\","
		"\"sensor_position\": %s,"
		"\"player\": \"%d\", "
		"\"type\": \"skeleton\", "
		"\"skeleton_3D\": {%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s}, "
		"\"skeleton_2D\": {%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s}}",
		 
		t.tv_sec,
		get_context(),
		 getSensorID(),
		 getSensorPosition(),
		 player, //player_name,
		 head, neck, left_shoulder, right_shoulder, left_elbow, right_elbow,
		 left_hand, right_hand, torso, left_hip, right_hip, left_knee, right_knee,
		 left_foot, right_foot,

		 head_2d, neck_2d, left_shoulder_2d, right_shoulder_2d, left_elbow_2d,
		 right_elbow_2d, left_hand_2d, right_hand_2d, torso_2d, left_hip_2d,
		 right_hip_2d, left_knee_2d, right_knee_2d, left_foot_2d, right_foot_2d);


	worker.AddMessage(new Send(buf), &SendCompleted, &skeleton_throttle);

    free(head);
    free(neck);
    free(left_shoulder);
    free(right_shoulder);
    free(left_elbow);
    free(right_elbow);
    free(left_hand);
    free(right_hand);
    free(torso);
    free(left_hip);
    free(right_hip);
    free(left_knee);
    free(right_knee);
    free(left_foot);
    free(right_foot);

    free(head_2d);
    free(neck_2d);
    free(left_shoulder_2d);
    free(right_shoulder_2d);
    free(left_elbow_2d);
    free(right_elbow_2d);
    free(left_hand_2d);
    free(right_hand_2d);
    free(torso_2d);
    free(left_hip_2d);
    free(right_hip_2d);
    free(left_knee_2d);
    free(right_knee_2d);
    free(left_foot_2d);
    free(right_foot_2d);

    free(context);
#endif
}

void SaveImageToFile(unsigned char *img, int width, int height) {
    unsigned char bmpfileheader[14] = {'B','M', 0,0,0,0, 0,0, 0,0, 54,0,0,0};
    unsigned char bmpinfoheader[40] = {40,0,0,0, 0,0,0,0, 0,0,0,0, 1,0, 24,0};
    unsigned char bmppad[3] = {0,0,0};
    unsigned int filesize = 3 * width * height;
    unsigned int i;

    // double word. file size
    bmpfileheader[ 2] = (unsigned char)(filesize    );
    bmpfileheader[ 3] = (unsigned char)(filesize>> 8);
    bmpfileheader[ 4] = (unsigned char)(filesize>>16);
    bmpfileheader[ 5] = (unsigned char)(filesize>>24);

    bmpinfoheader[ 4] = (unsigned char)(   width	);
    bmpinfoheader[ 5] = (unsigned char)(   width>> 8);
    bmpinfoheader[ 6] = (unsigned char)(   width>>16);
    bmpinfoheader[ 7] = (unsigned char)(   width>>24);
    bmpinfoheader[ 8] = (unsigned char)(  height     );
    bmpinfoheader[ 9] = (unsigned char)(  height>> 8);
    bmpinfoheader[10] = (unsigned char)(  height>>16);
    bmpinfoheader[11] = (unsigned char)(  height>>24);


    FILE *f = fopen("/home/ami/AmI-Platform/image.bmp","w");
    fwrite(bmpfileheader,1,14,f);
    fwrite(bmpinfoheader,1,40,f);
    for(i=0; i<height; i++)
    {
        fwrite(img + (3 * width * (height-1-i)), 3, width, f);
    }
    fclose(f);


	cv::Mat mat(height, width, CV_8UC3, img);

	util::StopWatch sw;
	sw.Start();
	vector<int> compression_params;
	compression_params.push_back(CV_IMWRITE_PNG_COMPRESSION);
	compression_params.push_back(3);
	cv::imwrite("/home/ami/AmI-Platform/image.png", mat, compression_params);


	printf("SW: png in %ld ms\n", sw.Stop());

	sw.Reset();
	sw.Start();
	compression_params.clear();
	compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
	compression_params.push_back(95);
	cv::imwrite("/home/ami/AmI-Platform/image.jpg", mat, compression_params);
	printf("SW: jpg in %ld ms\n", sw.Stop());

}

/*
 * Saves the RBG image data by deriving a JSON message and enqueueing it to
 * Kestrel, a message-queue system used to communicate with the rest of the
 * system.
 */
static void SaveImage(char *img, int width, int height, const char* player_name, const char* sensor_type, DataThrottle* throttle) {
#if USE_MEMCACHE
	size_t outlen, outlen2;

	//TODO: maybe move compression to the worker thread
	vector<int> compression_params;
	compression_params.clear();
	compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
	compression_params.push_back(95);

	cv::Mat mat(height, width, CV_8UC3, img);
	vector<unsigned char> c_buf;
	cv::imencode(".jpg", mat, c_buf, compression_params);
	std::basic_stringstream<unsigned char> os;

	using namespace boost::archive::iterators;

	typedef base64_from_binary< transform_width<vector<unsigned char>::iterator , 6, 8> > base64_text;

	std::copy(
		base64_text(c_buf.begin()),
	    base64_text(c_buf.end()),
	    boost::archive::iterators::ostream_iterator<unsigned char>(os)
	 );

	basic_string<unsigned char> encoded = os.str();

	while (encoded.size() % 4 != 0) {
		encoded += '=';
	}


	int buf_size = width * height * 3 * 2;
	char* buf = (char*) malloc(buf_size * sizeof(char));
	char* context = get_context();

	printf("SaveImage: width = %d, height = %d\n", width, height);

	timespec t;
    clock_gettime(CLOCK_REALTIME, &t);

	snprintf(buf, buf_size,
		"{\"created_at\": %ld,"
		"\"context\": \"%s\","
		"\"sensor_type\": \"kinect\","
		"\"sensor_id\": \"%s\","
		"\"sensor_position\": %s,"
		"\"type\": \"%s\","
		"\"%s\": {\"encoder_name\": \"jpg\", \"image\": \"%s\", \"width\": %d, \"height\": %d }}",
		t.tv_sec,
		context,
		getSensorID(),
		getSensorPosition(),
		sensor_type,
		sensor_type,
		encoded.c_str(), width, height);

		printf("sensor_type: %s, %d, %d \n", sensor_type, width, height);


	worker.AddMessage(new Send(buf), &SendCompleted, throttle);

	free(context);
#endif

}

void DrawDepthMap(const xn::DepthMetaData& dmd, const xn::SceneMetaData& smd, const xn::ImageMetaData& imd)
{

    static bool bInitialized = false;
    static GLuint depthTexID;
    static unsigned char* pDepthTexBuf;
    static int texWidth, texHeight;

    float topLeftX;
    float topLeftY;
    float bottomRightY;
    float bottomRightX;
    float texXpos;
    float texYpos;

    if(!bInitialized)
    {
        texWidth =  getClosestPowerOfTwo(dmd.XRes());
        texHeight = getClosestPowerOfTwo(dmd.YRes());

//		printf("Initializing depth texture: width = %d, height = %d\n", texWidth, texHeight);
        depthTexID = initTexture((void**)&pDepthTexBuf,texWidth, texHeight) ;

//		printf("Initialized depth texture: width = %d, height = %d\n", texWidth, texHeight);
        bInitialized = true;

        topLeftX = dmd.XRes();
        topLeftY = 0;
        bottomRightY = dmd.YRes();
        bottomRightX = 0;
        texXpos =(float)dmd.XRes()/texWidth;
        texYpos  =(float)dmd.YRes()/texHeight;

        memset(texcoords, 0, 8*sizeof(float));
        texcoords[0] = texXpos, texcoords[1] = texYpos, texcoords[2] = texXpos, texcoords[7] = texYpos;
    }

    unsigned int nValue = 0;
    unsigned int nHistValue = 0;
    unsigned int nIndex = 0;
    unsigned int nX = 0;
    unsigned int nY = 0;
    unsigned int nNumberOfPoints = 0;
    XnUInt16 g_nXRes = dmd.XRes();
    XnUInt16 g_nYRes = dmd.YRes();

    unsigned char* pDestImage = pDepthTexBuf;

    const XnDepthPixel* pDepth = dmd.Data();
    const XnLabel* pLabels = smd.Data();
    const XnUInt8* pImage = imd.Data();

    static unsigned int nZRes = dmd.ZRes();
    static float* pDepthHist = (float*)malloc(nZRes* sizeof(float));

    // Calculate the accumulative histogram
    memset(pDepthHist, 0, nZRes*sizeof(float));
    for (nY=0; nY<g_nYRes; nY++)
    {
        for (nX=0; nX<g_nXRes; nX++)
        {
            nValue = *pDepth;

            if (nValue != 0)
            {
                pDepthHist[nValue]++;
                nNumberOfPoints++;
            }
            pDepth++;
        }
    }

    for (nIndex=1; nIndex<nZRes; nIndex++)
    {
        pDepthHist[nIndex] += pDepthHist[nIndex-1];
    }
    if (nNumberOfPoints)
    {
        for (nIndex=1; nIndex<nZRes; nIndex++)
        {
            pDepthHist[nIndex] = (unsigned int)(256 * (1.0f - (pDepthHist[nIndex] / nNumberOfPoints)));
        }
    }

    char *img = (char *) malloc (3 * g_nXRes * g_nYRes);
    memset(img, 0, sizeof(img));

    printf("xRes = %d, yRes = %d\n", g_nXRes, g_nYRes);
    pDepth = dmd.Data();
    if (g_bDrawPixels)
    {
        XnUInt32 nIndex = 0;
        // Prepare the texture map
        for (nY=0; nY<g_nYRes; nY++)
        {
            for (nX=0; nX < g_nXRes; nX++, nIndex++)
            {

                pDestImage[0] = 0;
                pDestImage[1] = 0;
                pDestImage[2] = 0;
                if (g_bDrawBackground || *pLabels != 0)
                {
                    nValue = *pDepth;
                    XnLabel label = *pLabels;
                    XnUInt32 nColorID = label % nColors;
                    if (label == 0)
                    {
                        nColorID = nColors;
                    }

                    if (nValue != 0)
                    {
                        nHistValue = pDepthHist[nValue];

                        pDestImage[0] = nHistValue * Colors[nColorID][0];
                        pDestImage[1] = nHistValue * Colors[nColorID][1];
                        pDestImage[2] = nHistValue * Colors[nColorID][2];
                    }
                }

                img[(nY*g_nXRes +nX)*3+0] = (unsigned char) pDestImage[0];
                img[(nY*g_nXRes +nX)*3+1] = (unsigned char) pDestImage[1];
                img[(nY*g_nXRes +nX)*3+2] = (unsigned char) pDestImage[2];

                pDepth++;
                pLabels++;
                pDestImage+=3;
            }

            pDestImage += (texWidth - g_nXRes) *3;
        }


        if (rgb_throttle.CanSend()) {
        	SaveImage(img, g_nXRes, g_nYRes, "player1", "image_depth", &rgb_throttle);
        	rgb_throttle.MarkSend();
        }

        if (depth_throttle.CanSend()) {
        	SaveImage((char*)pImage, 1280, 1024, "player1", "image_rgb", &depth_throttle);
        	depth_throttle.MarkSend();
        }

    }
    else
    {
        xnOSMemSet(pDepthTexBuf, 0, 3*2*g_nXRes*g_nYRes);
    }

    free(img);

    glBindTexture(GL_TEXTURE_2D, depthTexID);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, texWidth, texHeight, 0, GL_RGB, GL_UNSIGNED_BYTE, pDepthTexBuf);

    // Display the OpenGL texture map
    glColor4f(0.75,0.75,0.75,1);

    glEnable(GL_TEXTURE_2D);
    DrawTexture(dmd.XRes(),dmd.YRes(),0,0);
    glDisable(GL_TEXTURE_2D);

    char strLabel[50] = "";
    XnUserID aUsers[15];
    XnUInt16 nUsers = 15;
    g_UserGenerator.GetUsers(aUsers, nUsers);
    for (int i = 0; i < nUsers; ++i)
    {
#ifndef USE_GLES
        if (g_bPrintID)
        {
            XnPoint3D com;
            g_UserGenerator.GetCoM(aUsers[i], com);
            g_DepthGenerator.ConvertRealWorldToProjective(1, &com, &com);

            XnUInt32 nDummy = 0;

            xnOSMemSet(strLabel, 0, sizeof(strLabel));
            if (!g_bPrintState)
            {
                // Tracking
                xnOSStrFormat(strLabel, sizeof(strLabel), &nDummy, "%d", aUsers[i]);
            }
            else if (g_UserGenerator.GetSkeletonCap().IsTracking(aUsers[i]))
            {
                // Tracking
                xnOSStrFormat(strLabel, sizeof(strLabel), &nDummy, "%d - Tracking", aUsers[i]);
            }
            else if (g_UserGenerator.GetSkeletonCap().IsCalibrating(aUsers[i]))
            {
                // Calibrating
                xnOSStrFormat(strLabel, sizeof(strLabel), &nDummy, "%d - Calibrating [%s]", aUsers[i], GetCalibrationErrorString(m_Errors[aUsers[i]].first));
            }
            else
            {
                // Nothing
                xnOSStrFormat(strLabel, sizeof(strLabel), &nDummy, "%d - Looking for pose [%s]", aUsers[i], GetPoseErrorString(m_Errors[aUsers[i]].second));
            }


            glColor4f(1-Colors[i%nColors][0], 1-Colors[i%nColors][1], 1-Colors[i%nColors][2], 1);

            glRasterPos2i(com.X, com.Y);
            glPrintString(GLUT_BITMAP_HELVETICA_18, strLabel);
        }
#endif
        if (g_bDrawSkeleton && g_UserGenerator.GetSkeletonCap().IsTracking(aUsers[i]))
        {
            glColor4f(1-Colors[aUsers[i]%nColors][0], 1-Colors[aUsers[i]%nColors][1], 1-Colors[aUsers[i]%nColors][2], 1);

            // Draw Joints
            if (g_bMarkJoints)
            {
                // Try to draw all joints
                DrawJoint(aUsers[i], XN_SKEL_HEAD);
                DrawJoint(aUsers[i], XN_SKEL_NECK);
                DrawJoint(aUsers[i], XN_SKEL_TORSO);
                DrawJoint(aUsers[i], XN_SKEL_WAIST);

                DrawJoint(aUsers[i], XN_SKEL_LEFT_COLLAR);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_SHOULDER);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_ELBOW);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_WRIST);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_HAND);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_FINGERTIP);

                DrawJoint(aUsers[i], XN_SKEL_RIGHT_COLLAR);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_SHOULDER);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_ELBOW);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_WRIST);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_HAND);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_FINGERTIP);

                DrawJoint(aUsers[i], XN_SKEL_LEFT_HIP);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_KNEE);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_ANKLE);
                DrawJoint(aUsers[i], XN_SKEL_LEFT_FOOT);

                DrawJoint(aUsers[i], XN_SKEL_RIGHT_HIP);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_KNEE);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_ANKLE);
                DrawJoint(aUsers[i], XN_SKEL_RIGHT_FOOT);
            }

            if (skeleton_throttle.CanSend()) {
            	SaveSkeleton(aUsers[i], "player1", "kinect1");
            	skeleton_throttle.MarkSend();
            }
#ifndef USE_GLES
            glBegin(GL_LINES);
#endif

            // Draw Limbs
            DrawLimb(aUsers[i], XN_SKEL_HEAD, XN_SKEL_NECK);

            DrawLimb(aUsers[i], XN_SKEL_NECK, XN_SKEL_LEFT_SHOULDER);
            DrawLimb(aUsers[i], XN_SKEL_LEFT_SHOULDER, XN_SKEL_LEFT_ELBOW);
            if (!DrawLimb(aUsers[i], XN_SKEL_LEFT_ELBOW, XN_SKEL_LEFT_WRIST))
            {
                DrawLimb(aUsers[i], XN_SKEL_LEFT_ELBOW, XN_SKEL_LEFT_HAND);
            }
            else
            {
                DrawLimb(aUsers[i], XN_SKEL_LEFT_WRIST, XN_SKEL_LEFT_HAND);
                DrawLimb(aUsers[i], XN_SKEL_LEFT_HAND, XN_SKEL_LEFT_FINGERTIP);
            }


            DrawLimb(aUsers[i], XN_SKEL_NECK, XN_SKEL_RIGHT_SHOULDER);
            DrawLimb(aUsers[i], XN_SKEL_RIGHT_SHOULDER, XN_SKEL_RIGHT_ELBOW);
            if (!DrawLimb(aUsers[i], XN_SKEL_RIGHT_ELBOW, XN_SKEL_RIGHT_WRIST))
            {
                DrawLimb(aUsers[i], XN_SKEL_RIGHT_ELBOW, XN_SKEL_RIGHT_HAND);
            }
            else
            {
                DrawLimb(aUsers[i], XN_SKEL_RIGHT_WRIST, XN_SKEL_RIGHT_HAND);
                DrawLimb(aUsers[i], XN_SKEL_RIGHT_HAND, XN_SKEL_RIGHT_FINGERTIP);
            }

            DrawLimb(aUsers[i], XN_SKEL_LEFT_SHOULDER, XN_SKEL_TORSO);
            DrawLimb(aUsers[i], XN_SKEL_RIGHT_SHOULDER, XN_SKEL_TORSO);

            DrawLimb(aUsers[i], XN_SKEL_TORSO, XN_SKEL_LEFT_HIP);
            DrawLimb(aUsers[i], XN_SKEL_LEFT_HIP, XN_SKEL_LEFT_KNEE);
            DrawLimb(aUsers[i], XN_SKEL_LEFT_KNEE, XN_SKEL_LEFT_FOOT);

            DrawLimb(aUsers[i], XN_SKEL_TORSO, XN_SKEL_RIGHT_HIP);
            DrawLimb(aUsers[i], XN_SKEL_RIGHT_HIP, XN_SKEL_RIGHT_KNEE);
            DrawLimb(aUsers[i], XN_SKEL_RIGHT_KNEE, XN_SKEL_RIGHT_FOOT);

            DrawLimb(aUsers[i], XN_SKEL_LEFT_HIP, XN_SKEL_RIGHT_HIP);
#ifndef USE_GLES
            glEnd();
#endif
        }
    }

    if (g_bPrintFrameID)
    {
        static XnChar strFrameID[80];
        xnOSMemSet(strFrameID, 0, 80);
        XnUInt32 nDummy = 0;
        xnOSStrFormat(strFrameID, sizeof(strFrameID), &nDummy, "%d", dmd.FrameID());

        glColor4f(1, 0, 0, 1);

        glRasterPos2i(10, 10);

        glPrintString(GLUT_BITMAP_HELVETICA_18, strFrameID);
    }
}

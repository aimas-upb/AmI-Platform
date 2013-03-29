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
#include <stdlib.h>

#include <XnOpenNI.h>
#include <XnCodecIDs.h>
#include <XnCppWrapper.h>
#include "SceneDrawer.h"
#include <XnPropNames.h>
#if USE_MEMCACHE
    #include <libmemcached/memcached.h>
#endif

#include "base64.h"
#include "ami_environment.h"

//---------------------------------------------------------------------------
// Globals
//---------------------------------------------------------------------------
xn::Context g_Context;
xn::ScriptNode g_scriptNode;
xn::DepthGenerator g_DepthGenerator;
xn::UserGenerator g_UserGenerator;
xn::ImageGenerator g_ImageGenerator;
xn::Player g_Player;
#if USE_MEMCACHE
memcached_st* g_MemCache;
#endif

#ifndef USE_GLES
#if (XN_PLATFORM == XN_PLATFORM_MACOSX)
    #include <GLUT/glut.h>
#else
    #include <GL/glut.h>
#endif
#else
    #include "opengles.h"
#endif

#ifdef USE_GLES
static EGLDisplay display = EGL_NO_DISPLAY;
static EGLSurface surface = EGL_NO_SURFACE;
static EGLContext context = EGL_NO_CONTEXT;
#endif

#define GL_WIN_SIZE_X 720
#define GL_WIN_SIZE_Y 480

XnBool g_bQuit = false;

void CleanupExit()
{
    g_scriptNode.Release();
    g_DepthGenerator.Release();
    g_UserGenerator.Release();
    g_Player.Release();
    g_Context.Release();
    g_ImageGenerator.Release();
    exit (1);
}

// Callback: New user was detected
void XN_CALLBACK_TYPE User_NewUser(xn::UserGenerator& /*generator*/, XnUserID nId, void* /*pCookie*/)
{
    g_UserGenerator.GetSkeletonCap().RequestCalibration(nId, TRUE);
}

// Callback: Finished calibration
void XN_CALLBACK_TYPE UserCalibration_CalibrationComplete(xn::SkeletonCapability& /*capability*/, XnUserID nId, XnCalibrationStatus eStatus, void* /*pCookie*/)
{
    if (eStatus == XN_CALIBRATION_STATUS_OK) {
        // Calibration succeeded
        g_UserGenerator.GetSkeletonCap().StartTracking(nId);
    } else {
        // Calibration failed
        if(eStatus==XN_CALIBRATION_STATUS_MANUAL_ABORT) {
            printf("Manual abort occured, stop attempting to calibrate!");
        } else {
            g_UserGenerator.GetSkeletonCap().RequestCalibration(nId, TRUE);
        }
    }
}

// this function is called each frame
void glutDisplay (void)
{
    xn::SceneMetaData sceneMD;
    xn::DepthMetaData depthMD;
    xn::ImageMetaData imageMD;

    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // Setup the OpenGL viewpoint
    glMatrixMode(GL_PROJECTION);
    glPushMatrix();
    glLoadIdentity();

    g_DepthGenerator.GetMetaData(depthMD);
    g_ImageGenerator.GetMetaData(imageMD);

#ifndef USE_GLES
    glOrtho(0, depthMD.XRes(), depthMD.YRes(), 0, -1.0, 1.0);
#else
    glOrthof(0, depthMD.XRes(), depthMD.YRes(), 0, -1.0, 1.0);
#endif

    glDisable(GL_TEXTURE_2D);

    // Read next available data
    g_Context.WaitOneUpdateAll(g_UserGenerator);

    // Process the data
    g_DepthGenerator.GetMetaData(depthMD);
    g_UserGenerator.GetUserPixels(0, sceneMD);
    g_ImageGenerator.GetMetaData(imageMD);

    // Draw the input fetched from the Kinect
    DrawKinectInput(depthMD, sceneMD, imageMD);

#ifndef USE_GLES
    glutSwapBuffers();
#endif
}

#ifndef USE_GLES
void glutIdle (void)
{
    if (g_bQuit) {
        CleanupExit();
    }

    // Display the frame
    glutPostRedisplay();
}

void glutKeyboard (unsigned char key, int /*x*/, int /*y*/)
{
    switch (key)
    {
    case 27:
        CleanupExit();
        break;
    }
}
void glInit (int * pargc, char ** argv)
{
    glutInit(pargc, argv);
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH);
    glutInitWindowSize(GL_WIN_SIZE_X, GL_WIN_SIZE_Y);
    glutCreateWindow ("User Tracker Viewer");
    //glutFullScreen();
    glutSetCursor(GLUT_CURSOR_NONE);

    glutKeyboardFunc(glutKeyboard);
    glutDisplayFunc(glutDisplay);
    glutIdleFunc(glutIdle);

    glDisable(GL_DEPTH_TEST);
    glEnable(GL_TEXTURE_2D);

    glEnableClientState(GL_VERTEX_ARRAY);
    glDisableClientState(GL_COLOR_ARRAY);
}
#endif // USE_GLES

#define CHECK_RC(nRetVal, what)										\
    if (nRetVal != XN_STATUS_OK)									\
    {																\
        printf("%s failed: %s\n", what, xnGetStatusString(nRetVal));\
        exit(nRetVal);												\
    }

void initFromContextFile() {
    /*
        Initialize Context from XML file + lookup generators of the needed type:
        - depth (for depth images)
        - image (for RGB images)
        - skeleton (for Skeleton position and tracking)

        Errors in the XML file, lack thereof or lack of generators of the mentioned types
        will stop the program altogether.
    */

    XnStatus nRetVal = XN_STATUS_OK;
    xn::EnumerationErrors errors;

    if (nRetVal == XN_STATUS_NO_NODE_PRESENT)
    {
        XnChar strError[1024];
        errors.ToString(strError, 1024);
        printf("%s\n", strError);
        exit(1);
    }
    else if (nRetVal != XN_STATUS_OK)
    {
        printf("Open failed: %s\n", xnGetStatusString(nRetVal));
        exit(1);
    }

    nRetVal = g_Context.InitFromXmlFile(getKinectXMLConfig(), g_scriptNode, &errors);
	if (nRetVal == XN_STATUS_NO_NODE_PRESENT)
	{
		XnChar strError[1024];
		errors.ToString(strError, 1024);
		printf("%s\n", strError);
		exit(1);
	}
	else if (nRetVal != XN_STATUS_OK)
	{
		printf("Open failed: %s\n", xnGetStatusString(nRetVal));
		exit(1);
	}

    if (g_Context.FindExistingNode(XN_NODE_TYPE_DEPTH, g_DepthGenerator) != XN_STATUS_OK) {
        printf("XML file should contain a depth generator\n");
        exit(1);
    }

    if (g_Context.FindExistingNode(XN_NODE_TYPE_IMAGE, g_ImageGenerator) != XN_STATUS_OK) {
        printf("XML file should contain an image generator\n");
        exit(1);
    }

    if (g_Context.FindExistingNode(XN_NODE_TYPE_USER, g_UserGenerator) != XN_STATUS_OK) {
        printf("XML file should contain an user generator\n");
        exit(1);
    }

    if (!g_UserGenerator.IsCapabilitySupported(XN_CAPABILITY_SKELETON)) {
        printf("Supplied user generator doesn't support skeleton\n");
        exit(1);
    }
}

void registerUserCallbacks() {
    XnStatus nRetVal = XN_STATUS_OK;
    XnCallbackHandle hCalibrationComplete;

    g_UserGenerator.GetSkeletonCap().SetSkeletonProfile(XN_SKEL_PROFILE_ALL);
    nRetVal = g_UserGenerator.GetSkeletonCap().RegisterToCalibrationComplete(UserCalibration_CalibrationComplete, NULL, hCalibrationComplete);
    CHECK_RC(nRetVal, "Register to calibration complete");
}

void initializeKestrelConnection() {
    /*
     * Kestrel is a distributed queueing system that we use to
     */
    g_MemCache = memcached_create(NULL);
    memcached_server_st* servers = NULL;
    memcached_return rc;
    servers = memcached_server_list_append(servers,
                                           getKestrelServerIP(),
                                           getKestrelServerPort(),
                                           &rc);
    memcached_server_push(g_MemCache, servers);
    printf("Pushed server %s:%d to list of kestrels\n", getKestrelServerIP(), getKestrelServerPort());
    if (rc != MEMCACHED_SUCCESS) {
        printf("Failed to register to memcache library\n");
        exit(-1);
    }
}

void openglMainLoop(int argc, char **argv) {
    /*
     * OpenGL main loop, depending on which type of library is available:
     * - GLUT
     * - OpenGL ES
     */

#ifndef USE_GLES
    glInit(&argc, argv);
    glutMainLoop();
#else
    if (!opengles_init(GL_WIN_SIZE_X, GL_WIN_SIZE_Y, &display, &surface, &context))
    {
        printf("Error initializing opengles\n");
        CleanupExit();
    }

    glDisable(GL_DEPTH_TEST);
    glEnable(GL_TEXTURE_2D);
    glEnableClientState(GL_VERTEX_ARRAY);
    glDisableClientState(GL_COLOR_ARRAY);

    while (!g_bQuit)
    {
        glutDisplay();
        eglSwapBuffers(display, surface);
    }
    opengles_shutdown(display, surface, context);

    base64_done();
    CleanupExit();
#endif
}

int main(int argc, char **argv)
{
    XnStatus nRetVal = XN_STATUS_OK;

    base64_init();
    SceneDrawerInit();
    initFromContextFile();
    registerUserCallbacks();
    nRetVal = g_Context.StartGeneratingAll();
    initializeKestrelConnection();

    CHECK_RC(nRetVal, "StartGenerating");

#if USE_MEMCACHE
    initializeKestrelConnection();
#endif

    openglMainLoop(argc, argv);

    return 0;
}

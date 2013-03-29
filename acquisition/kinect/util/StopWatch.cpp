#include "StopWatch.h"
#include <time.h>

namespace util {

void StopWatch::Start() {
	//state needs to be STATE_READY
	clock_gettime(CLOCK_MONOTONIC, &start);
	state = STATE_RUNNING;
}

long StopWatch::Stop() {
	//state needs to be STATE_RUNNING
	clock_gettime(CLOCK_MONOTONIC, &end);
	state = STATE_STOPPED;
	return TimeDiff(start, end);
}

void StopWatch::Reset() {
	//state needs to be STOPPED or READY
	state = STATE_READY;
}

long StopWatch::ReStart() {
	Stop();
	long time = GetTime();
	Start();
	return time;
}

long StopWatch::GetSplitTime() {
	//state needs to be STATE_RUNNING
	timespec now;
	clock_gettime(CLOCK_MONOTONIC, &now);
	return TimeDiff(start, now);
}

long StopWatch::GetTime() {
	//state needs to be STOPPED
	return TimeDiff(start, end);
}

long StopWatch::TimeDiff(const timespec& start, const timespec& end) {
	long ret = 0;
	//long ret = (end.tv_sec - start.tv_sec - 1) * 1000;

//	ret += (1000000000 + end.tv_nsec - start.tv_nsec) / 1000000;

	ret = (end.tv_nsec - start.tv_nsec) / 1000000;
	ret += (end.tv_sec - start.tv_sec) * 1000;
	return ret;
}

StopWatch::State StopWatch::GetState() {
	return state;
}

StopWatch::StopWatch(): state(STATE_READY){

}

StopWatch::~StopWatch() {
	// TODO Auto-generated destructor stub
}

} /* namespace util */

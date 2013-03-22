#ifndef STOPWATCH_H_
#define STOPWATCH_H_

#include <time.h>

namespace util {

class StopWatch {
public:
	enum State {STATE_RUNNING, STATE_STOPPED, STATE_READY};

private:
	timespec start;
	timespec end;

	State state;

	long TimeDiff(const timespec& start, const timespec& end);

public:
	StopWatch();
	~StopWatch();

	void Start();
	void ReStart();
	/** returns measured time in milliseconds*/
	long  Stop();

	void Reset();

	/** returns measured time in milliseconds*/
	long GetTime();

	/** returns time since it was started*/
	long GetSplitTime();

	State GetState();

};

} /* namespace util */
#endif /* STOPWATCH_H_ */

#ifndef DATATHROTTLE_H_
#define DATATHROTTLE_H_

#include "StopWatch.h"

class DataThrottle {
public:
    long min_delay;
    util::StopWatch sw;
    DataThrottle(long min_delay);
    bool CanSend();
    void MarkSend();
};

#endif

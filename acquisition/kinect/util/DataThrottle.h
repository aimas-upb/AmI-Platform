#ifndef DATATHROTTLE_H_
#define DATATHROTTLE_H_

class DataThrottle {
public:
    long min_delay;
    util::StopWatch sw;
    DataThrottle(long min_delay): min_delay(min_delay) {};
    bool CanSend();
    void MarkSend();
};

#endif

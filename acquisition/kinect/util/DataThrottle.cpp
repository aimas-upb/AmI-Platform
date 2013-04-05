#include "DataThrottle.h"

DataThrottle::DataThrottle(long min_delay): min_delay(min_delay) {}

bool DataThrottle::CanSend() {
    return (sw.GetState() == util::StopWatch::STATE_READY ||
            sw.GetSplitTime() >= min_delay);
}

void DataThrottle::MarkSend() {
    if (sw.GetState() == util::StopWatch::STATE_READY) {
        sw.Start();
    } else {
        sw.ReStart();
    }
}

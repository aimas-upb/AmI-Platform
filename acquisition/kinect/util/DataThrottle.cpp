class DataThrottle {
public:
    long min_delay;
    util::StopWatch sw;

    /** min delay is in milliseconds*/
    DataThrottle(long min_delay): min_delay(min_delay) {}
    bool CanSend() {
        return (sw.GetState() == util::StopWatch::STATE_READY || sw.GetSplitTime() >= min_delay);
    }

    void MarkSend() {
        if (sw.GetState() == util::StopWatch::STATE_READY) {
            sw.Start();
        } else {
            sw.ReStart();
        }
    }
};

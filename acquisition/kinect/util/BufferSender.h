#ifndef BUFFERSENDER_H_
#define BUFFERSENDER_H_

#include "Runnable.h"

namespace util {

class BufferSender: public Runnable {
public:
    char* buffer;
    int send_count;
    int send_size;

    BufferSender(char* b);
    ~BufferSender();
    void Run();
};

}

#endif

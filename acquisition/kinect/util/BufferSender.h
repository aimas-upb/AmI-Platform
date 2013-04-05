#ifndef BUFFERSENDER_H_
#define BUFFERSENDER_H_

#include <libmemcached/memcached.h>
#include "Runnable.h"

namespace util {

class BufferSender: public Runnable {

#ifdef USE_MEMCACHE
private:
	memcached_st* memcache;
#endif

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

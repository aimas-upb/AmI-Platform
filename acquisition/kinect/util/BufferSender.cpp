#include <stdio.h>
#include "BufferSender.h"
#include "../ami_environment.h"


namespace util {

BufferSender::BufferSender(char* b): buffer(b), send_count(0), send_size(0) {
#ifdef USE_MEMCACHE
	memcache = memcached_create(NULL);
	memcached_server_st* servers = NULL;
	memcached_return rc;
	servers = memcached_server_list_append(servers,
	                                       getKestrelServerIP(),
	                                       getKestrelServerPort(),
	                                       &rc);
	memcached_server_push(memcache, servers);
	printf("Pushed server %s:%d to list of kestrels\n", getKestrelServerIP(), getKestrelServerPort());
	if (rc != MEMCACHED_SUCCESS) {
		printf("Failed to register to memcache library\n");
	    exit(-1);
	}
#endif
}

BufferSender::~BufferSender() { free(buffer); }

void BufferSender::Run() {
#ifdef USE_MEMCACHE
    memcached_return rc;
    size_t len = strlen(buffer);
    rc = memcached_set(memcache,
            "measurements", strlen("measurements"),
            buffer, len,
            (time_t)0, (uint32_t)0);

    if (rc != MEMCACHED_SUCCESS) {
        printf("Could NOT send to Kestrel at %s:%d\n",
               getKestrelServerIP(), getKestrelServerPort());
    } else {
        // Only print successful sends once in a while - avoid log pollution
        send_count = send_count + 1;
        send_size = send_size + len;
        if (send_count % 10 == 0) {
            printf("Sent %5.3f KB to Kestrel across the latest %d messages\n",
                   send_size / 1024.0, send_count);
            send_size = 0;
            send_count = 0;
        }
    }
#endif
}


}

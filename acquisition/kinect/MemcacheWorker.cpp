#include <errno.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

#include <libmemcached/memcached.h>
extern memcached_st* g_MemCache;

#include "MemcacheWorker.h"

#ifdef MEMCACHE_WORKER_DEBUG
#define DBG(format, value) printf((format), (value))
#define DBG1(format, value, value2) printf((format), (value), (value2))
#else
#define DBG(format, value)
#define DBG1(format, value, value2)
#endif

////Cosmin: TODO: check for errors
MemcacheWorker::MemcacheWorker(size_t max) : queue_max(max),total_kbytes(0.0) {
    DBG("%s enter\n", __FUNCTION__);
    pthread_condattr_t cond_attr;
    pthread_condattr_init(&cond_attr);
    pthread_cond_init(&cond, &cond_attr);

    pthread_mutexattr_t mutex_attr;
    pthread_mutexattr_init(&mutex_attr);

    pthread_mutex_init(&mutex, &mutex_attr);

    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_create(&thread, &attr, &gRun, this);

    DBG("%s exit\n", __FUNCTION__);

}

bool MemcacheWorker::isFull() {
    bool ret = false;
    pthread_mutex_lock(&mutex);
    ret = queue.size() >= queue_max;
    pthread_mutex_unlock(&mutex);

    return ret;
}

MemcacheWorker::~MemcacheWorker() {
    DBG("%s enter\n", __FUNCTION__);
    pthread_mutex_lock(&mutex);
    done = true;
    pthread_cond_signal(&cond);
    pthread_mutex_unlock(&mutex);

    void *result;
    pthread_join(thread, &result);
    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&cond);
    DBG("%s exit\n", __FUNCTION__);
}

void MemcacheWorker::Run() {
    DBG("%s enter\n", __FUNCTION__);

    bool isDone = false;
    char* message;

    while(!isDone) {
        message = NULL;

        pthread_mutex_lock(&mutex);
        while (!done && queue.size() == 0) {
            pthread_cond_wait(&cond, &mutex);
        }
        isDone = done;
        if (queue.size() != 0) {
            message = queue.front();
            queue.pop_front();
            total_kbytes += strlen(message) / 1024.0;
        }


        pthread_mutex_unlock(&mutex);
        if (!isDone && message != NULL) {
            DBG("%s sending message\n", __FUNCTION__);
            memcached_return rc;
            rc = memcached_set(g_MemCache,
                     "measurements", strlen("measurements"),
                     message, strlen(message),
                     (time_t)0, (uint32_t)0);

            if (rc != MEMCACHED_SUCCESS) {
                printf("Could NOT send to memcache. I'm very very sad :-( :-( :-(\n");
            }

            free(message);
            sleep(1);
        }

    }

    DBG("%s exit\n", __FUNCTION__);
}

bool MemcacheWorker::AddMessage(char* message) {
    DBG("%s enter\n", __FUNCTION__);
    bool ret = true;
    pthread_mutex_lock(&mutex);
    if (queue.size() < queue_max) {
        queue.push_back(message);
        ret = true;
        pthread_cond_signal(&cond);
    } else {
        DBG1("%s full queue. Message ignored (sent %lf)\n", __FUNCTION__, total_kbytes);
        free(message);
        ret = false;
    }
    pthread_mutex_unlock(&mutex);
    DBG("%s exit\n", __FUNCTION__);
    return ret;


}

void* MemcacheWorker::gRun(void* v) {
    ((MemcacheWorker*)v) ->Run();
    return NULL;
}


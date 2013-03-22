#include <errno.h>
#include <malloc.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

#include <libmemcached/memcached.h>

#include "Worker.h"
#include "StopWatch.h"

#ifdef MEMCACHE_WORKER_DEBUG
#define DBG(format, value) printf((format), (value))
#define DBG1(format, value, value2) printf((format), (value), (value2))
#else
#define DBG(format, value)
#define DBG1(format, value, value2)
#endif

namespace util {
////Cosmin: TODO: check for errors
Worker::Worker(size_t max) : queue_max(max), done(false) {
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

bool Worker::isFull() {
	bool ret = false;
	pthread_mutex_lock(&mutex);
	ret = queue.size() >= queue_max;
	pthread_mutex_unlock(&mutex);

	return ret;
}

Worker::~Worker() {
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

void Worker::Run() {
	DBG("%s enter\n", __FUNCTION__);

	bool isDone = false;
	RunnableRegistration* r = NULL;

	while(!isDone) {
		r = NULL;

		pthread_mutex_lock(&mutex);
		while (!done && queue.size() == 0) {
			pthread_cond_wait(&cond, &mutex);
		}
		isDone = done;
		if (queue.size() != 0) {
			r = queue.front();
			queue.pop_front();
		}


		pthread_mutex_unlock(&mutex);
		if (!isDone && r != NULL) {
//			DBG("%s sending message\n", __FUNCTION__);
////			printf("%s\n", message);
//			memcached_return rc;
//			util::StopWatch sw;
//			sw.Start();
//			printf("g_MemCache = %p\n", g_MemCache);
//			size_t size = strlen(message);
//			rc = memcached_set(g_MemCache,
//					 "measurements", strlen("measurements"),
//					 message, size,
//					 (time_t)0, (uint32_t)0);
//
//			if (rc != MEMCACHED_SUCCESS) {
//				printf("Could NOT send to memcache. I'm very very sad :-( :-( :-(\n");
//			} else {
//				printf("I can send to memcache. HURRAY!! :-) :-) :-)\n");
//			}
//			sw.Stop();
//			DBG1("%s sent message in %ld ms\n", __FUNCTION__, sw.GetTime());
//			DBG1("%s sent message of size %ld \n", __FUNCTION__, size);
//			free(message);
			try {
				r->runnable->Run();
			} catch (...) {

			}
			try {
				r->callback(r->runnable, r->arg);
			} catch (...) {

			}

			delete r;
		}

	}

	DBG("%s exit\n", __FUNCTION__);
}

bool Worker::AddMessage(Runnable * runnable, TaskDoneCallback callback, void* arg) {
	DBG("%s enter\n", __FUNCTION__);
	bool ret = true;
	pthread_mutex_lock(&mutex);
	if (queue.size() < queue_max) {
		RunnableRegistration* r = new RunnableRegistration();
		r->arg = arg;
		r->runnable = runnable;
		r->callback = callback;
		queue.push_back(r);
		ret = true;
		pthread_cond_signal(&cond);
	} else {
		DBG("%s full queue. Message ignored \n", __FUNCTION__);
		ret = false;
		callback(runnable, arg);
	}
	pthread_mutex_unlock(&mutex);
	DBG("%s exit\n", __FUNCTION__);
	return ret;


}

void* Worker::gRun(void* v) {
	((Worker*)v) ->Run();
	return NULL;
}

}

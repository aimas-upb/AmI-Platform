#ifndef WORKER_H_
#define WORKER_H_

#include <pthread.h>
#include <deque>

#include "Runnable.h"

namespace util {

typedef void (*TaskDoneCallback)(Runnable* r, void* arg);

class Worker {

private:

	pthread_mutex_t mutex;
	pthread_cond_t cond;
	pthread_t thread;
	const size_t queue_max;
	bool done;

	class RunnableRegistration {
	public:
		Runnable* runnable;
		TaskDoneCallback callback;
		void* arg;
	};

	std::deque<RunnableRegistration*> queue;

	void Run();
	static void* gRun(void* v);

public:
	/*
	 * N is the maximum number of messages to keep in the queue
	 */
	Worker(size_t max);
	virtual ~Worker();

	bool isFull();

	/*
	 * takes ownership of the message
	 * returns true if the message could be added (still takes ownership of message)
	 */
	bool AddMessage(Runnable * runnable, TaskDoneCallback callback, void* arg);


};
}

#endif /* WORKER_H_ */

#ifndef MEMCACHEWORKER_H_
#define MEMCACHEWORKER_H_

#include <pthread.h>
#include <deque>

class MemcacheWorker {

private:

	pthread_mutex_t mutex;
	pthread_cond_t cond;
	pthread_t thread;
	bool done;
	const size_t queue_max;

	std::deque<char*> queue;

	double total_kbytes;


	void Run();
	static void* gRun(void* v);

public:
	/*
	 * N is the maximum number of messages to keep in the queue
	 */
	MemcacheWorker(size_t max);
	virtual ~MemcacheWorker();

	bool isFull();

	/*
	 * takes ownership of the message
	 * returns true if the message could be added (still takes ownership of message)
	 */
	bool AddMessage(char * message);


};

#endif /* MEMCACHEWORKER_H_ */

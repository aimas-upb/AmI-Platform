#ifndef RUNNABLE_H_
#define RUNNABLE_H_

#include <time.h>

namespace util {

class Runnable {
public:
	virtual ~Runnable() {};
	virtual void Run() = 0;

};

}

/* namespace util */
#endif /* RUNNABLE_H_ */


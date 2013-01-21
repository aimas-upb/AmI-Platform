/*
 * uthread.h -- cooperative multi-threading library header
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#ifndef __UTHREAD_H__
#define __UTHREAD_H__

typedef char tid_t;
typedef void (*thread_entry_t)();

#define INVALID_TID -1

tid_t uthread_create(thread_entry_t entry, int stack_size, int suspended);
int uthread_suspend(tid_t id);
void uthread_wait();
void uthread_sleep(unsigned int ms);
int uthread_resume(tid_t id);
int uthread_kill(tid_t id);

#ifdef __cplusplus
extern "C" {
#endif

void uthread_yield(void);
void uthread_exit(void);

#ifdef __cplusplus
}
#endif

#endif

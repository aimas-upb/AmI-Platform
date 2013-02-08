/*
 * uthread.cpp -- cooperative multi-threading library implementation
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "uthread.h"

struct thread_context {
    struct thread_context *next;
    struct thread_context *prev;
    void *sp;
    char suspended;
    tid_t id;
    unsigned char stack[0];
};

#define CONTEXT_SIZE       18
#define PC_SIZE            3
#define INIT_STACK_SIZE    (CONTEXT_SIZE + PC_SIZE * 2)

static tid_t last_id;
static struct thread_context root = { &root };

struct thread_context *_uthread_current = &root;
#define current _uthread_current

/**
 * uthread_create() - create new thread
 * @entry:      entry point for new thread
 * @stack_size: size of new thread's stack
 * @suspended:  mark new thread as suspended
 *
 * Returns id of new thread, or INVALID_TID if there is not enough memory.
 * 
 * New thread will be added after current thread in the scheduling chain.
 * Function returns after creating the thread, it does not switch to it.
 */
tid_t uthread_create(thread_entry_t entry, int stack_size, int suspended)
{
    struct thread_context *ctx;
    unsigned char *p;

    ctx = (struct thread_context *)malloc(sizeof(*ctx) + stack_size + INIT_STACK_SIZE);
    if (!ctx)
        return INVALID_TID;

    /* stack layout (empty-descending stack): [ ][saved regs][saved PC][uthread_exit]
     * saved regs: R2-R17, R28, R29
     * saved PC on stack is 3 bytes, big-endian */

    p = ctx->stack + stack_size;
    ctx->sp = p - 1;
    memset(p, 0, INIT_STACK_SIZE);
    p += CONTEXT_SIZE;
    p++;
    *p++ = ((unsigned int) entry >> 8) & 0xff;
    *p++ = (unsigned int) entry & 0xff;
    p++;
    *p++ = ((unsigned int) uthread_exit >> 8) & 0xff;
    *p++ = (unsigned int) uthread_exit & 0xff;

    ctx->id = ++last_id;
    ctx->suspended = !!suspended;

    ctx->next = current->next;
    ctx->prev = current;
    current->next = ctx;
    ctx->next->prev = ctx;

    return ctx->id;
}

#ifdef __cplusplus
extern "C" {
#endif

void _uthread_free(struct thread_context *ctx)
{
    ctx->prev->next = ctx->next;
    ctx->next->prev = ctx->prev;
    free(ctx);
}

#ifdef __cplusplus
}
#endif

static struct thread_context *find_thread(tid_t id)
{
    struct thread_context *ctx;

    if (id == current->id)
        return current;

    for (ctx = current->next; ctx != current; ctx = ctx->next)
        if (id == ctx->id)
            return ctx;

    return NULL;
}

/**
 * uthread_suspend() - suspends a thread
 * @id: id of thread to suspend
 *
 * Returns 1 on success, and 0 on failure.
 *
 * If id designates the current thread, it will only be marked as suspended,
 * but will continue to run until it yields.
 */
int uthread_suspend(tid_t id)
{
    struct thread_context *ctx;

    ctx = find_thread(id);
    if (!ctx)
        return 0;

    ctx->suspended = 1;

    return 1;
}

/**
 * uthread_wait() - suspend current thread and yield control
 */
void uthread_wait()
{
    current->suspended = 0;
    uthread_yield();
}

/**
 * uthread_sleep() - yields control for some time
 * @ms: minimum number of miliseconds to yield
 */
void uthread_sleep(unsigned int ms)
{
    unsigned long finish;

    finish = millis() + ms;
    while (millis() < finish)
        uthread_yield();
}

/**
 * uthread_resume() - resume a thread
 * @id: id of thread to resume
 *
 * Returns 1 on success, and 0 on failure.
 * 
 * Function returns after marking thread as not suspended, it does not
 * switch to it.
 */
int uthread_resume(tid_t id)
{
    struct thread_context *ctx;

    ctx = find_thread(id);
    if (!ctx)
        return 0;

    ctx->suspended = 0;

    return 1;
}

/**
 * uthread_kill() - kill a thread
 * @id: id of thread to kill
 *
 * Returns 1 on sucess, and 0 on failure.
 * 
 * Current thread cannot be killed with this function
 * (use uthread_exit instead).
 */
int uthread_kill(tid_t id)
{
    struct thread_context *ctx;

    if (id == current->id)
        return 0;

    ctx = find_thread(id);
    if (!ctx)
        return 0;

    _uthread_free(ctx);

    return 1;
}

/**
 * uthread_yield() - yields control to another thread
 *
 * Function is defined in kernel.S.
 */
/* void uthread_yield(); */

/**
 * uthread_exit() - terminate current thread
 *
 * Function is defined in kernel.S.
 */
/* void uthread_exit(); */

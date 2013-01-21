/*
 * kernel.S -- cooperative multi-threading library low-level functions
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

__SP_H__ = 0x3e
__SP_L__ = 0x3d

.global uthread_yield
    .type uthread_yield, @function
uthread_yield:
    /* optimize for single thread execution */
    lds r30, _uthread_current
    lds r31, _uthread_current+1
    ld r26, Z
    ldd r27, Z+1
    cp r26, r30
    cpc r27, r31
    brne more_threads
    ret
more_threads:
    /* save current context */
    push r2
    push r3
    push r4
    push r5
    push r6
    push r7
    push r8
    push r9
    push r10
    push r11
    push r12
    push r13
    push r14
    push r15
    push r16
    push r17
    push r28
    push r29
    cli
    in r22, __SP_L__
    in r23, __SP_H__
    sei
    std Z+4, r22
    std Z+5, r23
    clr r24
    clr r25
    /* advance to next thread that is not suspended; also free
        * terminating thread's context if received as a parameter (r25:r24) */
find_thread:
    movw r30, r26
    ldd r22, Z+6
    cp r22, r1
    breq found
    ld r26, Z
    ldd r27, Z+1
    jmp find_thread
found:
    sts _uthread_current, r30
    sts _uthread_current+1, r31
    /* restore next thread's context */
    ldd r22, Z+4
    ldd r23, Z+5
    cli
    out __SP_L__, r22
    out __SP_H__, r23
    sei
    pop r29
    pop r28
    pop r17
    pop r16
    pop r15
    pop r14
    pop r13
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop r7
    pop r6
    pop r5
    pop r4
    pop r3
    pop r2
    /* check if switch was caused by a terminating thread */
    cp r24, r1
    cpc r25, r1
    breq no_cleanup
    call _uthread_free
no_cleanup:
    ret

.global uthread_exit
    .type uthread_exit, @function
uthread_exit:
    lds r30, _uthread_current
    lds r31, _uthread_current+1
    ld r26, Z
    ldd r27, Z+1
    movw r24, r30
    jmp find_thread

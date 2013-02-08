/*
 * buffer.h -- ring buffer library
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#ifndef __BUFFER_H__
#define __BUFFER_H__

#include <stdint.h>
#include <util/atomic.h>

#ifdef __cplusplus
extern "C" {
#endif

struct ring_buffer
{
    unsigned int size;
    unsigned int len;
    unsigned int ridx;
    unsigned int widx;
    byte buffer[0];
};

static inline void buffer_clear(struct ring_buffer *buf)
{
    buf->len = buf->ridx = buf->widx = 0;
}

static inline void buffer_clear_atomic(struct ring_buffer *buf)
{
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        buf->len = buf->ridx = buf->widx = 0;
}

static inline struct ring_buffer *buffer_alloc(unsigned int size)
{
    struct ring_buffer *buf;
    buf = (struct ring_buffer *)malloc(sizeof(*buf) + size);
    if (!buf)
        return NULL;
    buf->size = size;
    buffer_clear(buf);
    return buf;
}

static inline unsigned int buffer_len(struct ring_buffer *buf)
{
    return buf->len;
}

static inline unsigned int buffer_len_atomic(struct ring_buffer *buf)
{
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        return buf->len;
}

static inline unsigned int buffer_space(struct ring_buffer *buf)
{
    return buf->size - buf->len;
}

static inline unsigned int buffer_space_atomic(struct ring_buffer *buf)
{
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        return buf->size - buf->len;
}

static inline boolean buffer_empty(struct ring_buffer *buf)
{
    return !buffer_len(buf);
}

static inline boolean buffer_empty_atomic(struct ring_buffer *buf)
{
    return !buffer_len_atomic(buf);
}

static inline boolean buffer_full(struct ring_buffer *buf)
{
    return buffer_len(buf) == buf->size;
}

static inline boolean buffer_full_atomic(struct ring_buffer *buf)
{
    return buffer_len_atomic(buf) == buf->size;
}

static inline boolean buffer_peek(struct ring_buffer *buf, byte *c)
{
    if (buffer_empty(buf))
        return false;
    *c = buf->buffer[buf->ridx];
    return true;
}

static inline boolean buffer_peek_atomic(struct ring_buffer *buf, byte *c)
{
    if (buffer_empty_atomic(buf))
        return false;
    *c = buf->buffer[buf->ridx];
    return true;
}

static inline boolean buffer_read(struct ring_buffer *buf, byte *c)
{
    if (buffer_empty(buf))
        return false;
    *c = buf->buffer[buf->ridx];
    buf->ridx = (buf->ridx + 1) % buf->size;
    buf->len--;
    return true;
}

static inline int buffer_read_atomic(struct ring_buffer *buf, byte *c)
{
    if (buffer_empty_atomic(buf))
        return false;
    *c = buf->buffer[buf->ridx];
    buf->ridx = (buf->ridx + 1) % buf->size;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        buf->len--;
    return true;
}

static inline int buffer_write(struct ring_buffer *buf, byte c)
{
    if (buffer_full(buf))
        return false;
    buf->buffer[buf->widx] = c;
    buf->widx = (buf->widx + 1) % buf->size;
    buf->len++;
    return true;
}

static inline int buffer_write_atomic(struct ring_buffer *buf, byte c)
{
    if (buffer_full_atomic(buf))
        return false;
    buf->buffer[buf->widx] = c;
    buf->widx = (buf->widx + 1) % buf->size;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        buf->len++;
    return true;
}

#ifdef __cplusplus
}
#endif

#endif /* __BUFFER_H__ */

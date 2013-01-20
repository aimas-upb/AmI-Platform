/*
 * wifly-bench.c -- tool for benchmarking TCP throughput
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>

/* receive-only mode by default */
#ifndef NOSEND
#define NOSEND      1
#endif

#define BUFSIZE     (1024*200)
#define WINDOW      4096
#define CHUNK       256
#define NREPEATS    10
#define DELAY       3

static int fdump = -1;

static unsigned int resolve(char *host)
{
    int addr;
    struct hostent *he;

    addr = inet_addr(host);
    if (addr < 0) {
        printf("Resolving %s...\n", host);
        he = gethostbyname(host);
        if (!he) {
            perror("gethostbyname");
            exit(1);
        }
        memcpy(&addr, he->h_addr, sizeof(int));
    }

    return addr;
}

static int sock_listen(unsigned int ip, int port)
{
    int sock, optval;
    struct sockaddr_in addr;

    sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0)
    {
        perror("socket");
        return -1;
    }

    optval = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) == -1)
    {
        perror("setsockopt(SO_REUSEADDR)");
        close(sock);
        return -1;
    }

    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = ip;
    addr.sin_port = htons(port);

    if (bind(sock, (struct sockaddr*) &addr, sizeof(addr)) == -1)
    {
        perror("bind");
        close(sock);
        return -1;
    }

    listen(sock, 1);

    return sock;
}

#if 0
static void sock_send(int sock, char *buf, size_t size)
{
    size_t count, total;
    ssize_t ret;

    for (total = 0; total < size; total += ret) {
        count = total + CHUNK > size ? size - total : CHUNK;
        ret = send(sock, buf + total, count, 0);
        if (ret == -1) {
            perror("send");
            exit(1);
        }
    }
}

static void sock_recv(int sock, char *buf, size_t size)
{
    size_t total;
    ssize_t ret;

    for (total = 0; total < size; total += ret) {
        ret = recv(sock, buf + total, size - total, 0);
        if (ret == -1) {
            perror("recv");
            exit(1);
        }
        if (ret == 0) {
            fprintf(stderr, "recv: EOF after %zu bytes, expected %zu\n", total, size);
            exit(1);
        }
    }
}
#endif

static char *alloc_buffer(size_t size)
{
    char *buf;

    buf = (char *)malloc(size);
    if (!buf) {
        perror("malloc");
        exit(1);
    }

    return buf;
}

static void fill_test_buffer(char *buf, size_t size)
{
    int i;

    for (i = 0; i < size; i++)
        buf[i] = rand() & 0xff;
}

static const char *pretty_size(unsigned long long size)
{
    static char buf[32];
    static const char *suffixes[] = {"B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"};
    int i;

    for (i = 0; size > (1 << 10); i++)
        size >>= 10;

    sprintf(buf, "%llu %s", size, suffixes[i]);

    return buf;
}

static void get_tstamp(struct timespec *tstamp)
{
    clock_gettime(CLOCK_MONOTONIC, tstamp);
}

static double tstamp_diff(struct timespec *start, struct timespec *end)
{
    return (double) (end->tv_sec - start->tv_sec) + (end->tv_nsec - start->tv_nsec) / 1000000000.0;
}

static void sock_rube_goldberg(int sock, char *buf1, char *buf2, size_t size)
{
    size_t count, total1, total2;
    ssize_t ret, ret2;
    fd_set wfd, rfd;
    struct timespec wt, rt, t;
    double wspd, rspd;

    get_tstamp(&t);
    wt = rt = t;
    wspd = rspd = 0;

    total1 = total2 = 0;
    while (total2 < size) {
        FD_ZERO(&wfd);
        FD_ZERO(&rfd);
#if !NOSEND
        if (total1 < size && total1 < total2 + WINDOW)
            FD_SET(sock, &wfd);
#endif
        FD_SET(sock, &rfd);
        if (select(sock + 1, &rfd, &wfd, NULL, NULL) == -1) break;
        if (FD_ISSET(sock, &wfd)) {
            get_tstamp(&t);
            count = total1 + CHUNK > size ? size - total1 : CHUNK;
            ret = send(sock, buf1 + total1, count, 0);
            if (ret == -1) {
                perror("send");
                exit(1);
            }
            total1 += ret;
            wspd = ret / tstamp_diff(&wt, &t) / 1024;
            wt = t;
        }
        if (FD_ISSET(sock, &rfd)) {
            get_tstamp(&t);
            ret = recv(sock, buf2 + total2, size - total2, 0);
            if (ret == -1) {
                perror("recv");
                exit(1);
            }
            if (ret == 0) {
                fprintf(stderr, "recv: EOF after %zu bytes, expected %zu\n", total2, size);
                exit(1);
            }
            if (fdump != -1) {
                ret2 = write(fdump, buf2 + total2, ret);
                if (ret2 == -1)
                    perror("write");
                if (ret2 < ret)
                    fprintf(stderr, "write: incomplete write (%zd < %zd)\n", ret2, ret);
            }
            total2 += ret;
            rspd = ret / tstamp_diff(&rt, &t) / 1024;
            rt = t;
        }
        printf("\r%8zu -> [%8.2lf KB/s]   %8zu <- [%8.2lf KB/s]          ",
               total1, wspd, total2, rspd);
        fflush(stdout);
    }

    printf("\n");
}

static void throughput_test(int sock)
{
    int i, nerrors, err;
    size_t size;
    char *buf1, *buf2;
    struct timespec t1, t2;
    double total, diff;

    size = BUFSIZE;

    buf1 = alloc_buffer(size);
    fill_test_buffer(buf1, size);

    buf2 = alloc_buffer(size);

    printf("Starting benchmark in %d seconds...\n", DELAY);
    sleep(DELAY);
    printf("Started.\n");

    nerrors = 0;
    total = 0;
    for (i = 0; i < NREPEATS; i++) {
        memset(buf2, 0x42, size);
        get_tstamp(&t1);
        sock_rube_goldberg(sock, buf1, buf2, size);
        get_tstamp(&t2);
        if (memcmp(buf1, buf2, size)) {
            nerrors++;
            err = 1;
        } else {
            err = 0;
        }
        diff = tstamp_diff(&t1, &t2);
        total += diff;
        printf("Block #%d [%s]: speed=%8.2lf KB/s  avg=%8.2lf KB/s  delta=%5.2lf s  total=%5.2lf s [%s]\n", i, pretty_size(size),
               (double) size / diff / 1024, (double) size * (i + 1) / total / 1024,
               diff, total, err ? "ERR" : "OK!");
    }

    printf("All tests done. Total errors: %d\n\n", nerrors);
}

int new_dump_file()
{
    static int id;
    char fname[20];
    int fd;

    sprintf(fname, "dump%02d.dat", id++);

    fd = open(fname, O_WRONLY | O_CREAT | O_TRUNC, 0666);
    if (fd == -1)
        perror(fname);

    return fd;
}

int main(int argc, char **argv)
{
    int serv, sock;
    unsigned int ip;
    unsigned short port;
    struct sockaddr_in addr;
    socklen_t addrlen;

    srand(42);

    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s [<ip>] <port>\n", argv[0]);
        exit(1);
    }

    if (argc == 2) {
        ip = INADDR_ANY;
        port = atoi(argv[1]);
    } else {
        ip = resolve(argv[1]);
        port = atoi(argv[2]);
    }

    serv = sock_listen(ip, port);
    if (serv == -1)
        exit(1);

    printf("Listening on port %s:%hu...\n\n", inet_ntoa(*(struct in_addr *)&ip), port);

    while (1) {
        addrlen = sizeof(struct sockaddr_in);
        sock = accept(serv, (struct sockaddr *)&addr, &addrlen);
        if (sock == -1)
            continue;

        printf("Accepted connection from %s:%hu.\n\n", inet_ntoa(addr.sin_addr), ntohs(addr.sin_port));

        fdump = new_dump_file();

        throughput_test(sock);

        close(fdump);
        fdump = -1;

        close(sock);

        printf("Connection closed.\n\n");
    }

    close(serv);

    return 0;
}

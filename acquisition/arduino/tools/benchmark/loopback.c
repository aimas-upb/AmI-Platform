/*
 * loopback.c -- connect to server, then loop back everything that is received
 *
 * (c) 2011 Octavian Voicu <octavian.voicu@gmail.com>
 */

#include <netdb.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <arpa/inet.h>

#define BUFSIZE		4096

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

static int sock_connect(unsigned int ip, unsigned short port)
{
    int sock;
    struct sockaddr_in addr;

    sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0)
    {
        perror("socket");
        return -1;
    }

    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = ip;
    addr.sin_port = htons(port);

    if (connect(sock, (struct sockaddr*) &addr, sizeof(addr)) == -1)
    {
        perror("connect");
        close(sock);
        return -1;
    }

    return sock;
}

static void sock_loopback(int sock)
{
    char *buf;
    size_t total, size;
    ssize_t ret;

    buf = (char *)malloc(BUFSIZE);
    if (!buf) {
        perror("malloc");
        return;
    }

    while (1)
    {
        ret = recv(sock, buf, BUFSIZE, 0);
        if (ret == -1) {
            perror("recv");
            break;
        }
        if (!ret)
            break;
        size = ret;
        for (total = 0; total < size; total += ret) {
            ret = send(sock, buf + total, size - total, 0);
            if (ret == -1) {
                perror("send");
                break;
            }
        }
        if (total < size)
            break;
    }

    free(buf);
}

int main(int argc, char **argv)
{
    int sock;
    unsigned int ip;
    unsigned short port;

    if (argc != 3)
    {
        fprintf(stderr, "Usage: %s <ip> <port>\n", argv[0]);
        exit(1);
    }

    ip = resolve(argv[1]);
    port = atoi(argv[2]);

    printf("Connecting to %s:%hu...\n", inet_ntoa(*(struct in_addr*) &ip), port);

    sock = sock_connect(ip, port);
    if (sock == -1)
        exit(1);

    printf("Connected. Starting loopback...\n");

    sock_loopback(sock);
    close(sock);

    printf("Connection closed.\n");

    return 0;
}

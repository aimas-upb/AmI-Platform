CFLAGS = -Wall -O2
LDFLAGS = -lrt
PROGS = wifly-bench loopback

all: $(PROGS)

wifly-bench: wifly-bench.c

loopback: loopback.c

clean:
	rm -f *~ *.o $(PROGS)

CC = gcc
CFLAGS = -Iruntime

all:
	$(CC) $(CFLAGS) -c runtime/pyrinas.c -o runtime/pyrinas.o

clean:
	rm -f runtime/*.o

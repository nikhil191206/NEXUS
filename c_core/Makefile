CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2
TARGET = nexus_engine
SOURCES = nexus_engine.c graph.c hash_table.c trie.c queue.c stack.c
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJECTS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET) nexus_engine.exe

rebuild: clean all

.PHONY: all clean rebuild

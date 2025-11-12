#ifndef QUEUE_H
#define QUEUE_H

#include <stdlib.h>
#include "hash_table.h"

typedef struct QueueNode {
    GraphNode* data;
    struct QueueNode* next;
} QueueNode;

typedef struct Queue {
    QueueNode* front;
    QueueNode* rear;
    int size;
} Queue;

Queue* create_queue();
void enqueue(Queue* q, GraphNode* node);
GraphNode* dequeue(Queue* q);
int is_queue_empty(Queue* q);
void queue_free(Queue* q);

#endif

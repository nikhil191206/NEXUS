#include "queue.h"
#include <stdio.h>

Queue* create_queue() {
    Queue* q = (Queue*)malloc(sizeof(Queue));
    q->front = NULL;
    q->rear = NULL;
    q->size = 0;
    return q;
}

void enqueue(Queue* q, GraphNode* node) {
    QueueNode* new_node = (QueueNode*)malloc(sizeof(QueueNode));
    new_node->data = node;
    new_node->next = NULL;

    if (q->rear == NULL) {
        q->front = new_node;
        q->rear = new_node;
    } else {
        q->rear->next = new_node;
        q->rear = new_node;
    }
    q->size++;
}

GraphNode* dequeue(Queue* q) {
    if (is_queue_empty(q)) {
        return NULL;
    }

    QueueNode* temp = q->front;
    GraphNode* data = temp->data;
    q->front = q->front->next;

    if (q->front == NULL) {
        q->rear = NULL;
    }

    free(temp);
    q->size--;
    return data;
}

int is_queue_empty(Queue* q) {
    return q->front == NULL;
}

void queue_free(Queue* q) {
    while (!is_queue_empty(q)) {
        dequeue(q);
    }
    free(q);
}

#ifndef STACK_H
#define STACK_H

#include <stdlib.h>
#include "hash_table.h"

typedef struct StackNode {
    GraphNode* data;
    struct StackNode* next;
} StackNode;

typedef struct Stack {
    StackNode* top;
    int size;
} Stack;

Stack* create_stack();
void push(Stack* s, GraphNode* node);
GraphNode* pop(Stack* s);
int is_stack_empty(Stack* s);
void stack_free(Stack* s);

#endif

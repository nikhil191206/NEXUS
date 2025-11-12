#include "stack.h"
#include <stdio.h>

Stack* create_stack() {
    Stack* s = (Stack*)malloc(sizeof(Stack));
    s->top = NULL;
    s->size = 0;
    return s;
}

void push(Stack* s, GraphNode* node) {
    StackNode* new_node = (StackNode*)malloc(sizeof(StackNode));
    new_node->data = node;
    new_node->next = s->top;
    s->top = new_node;
    s->size++;
}

GraphNode* pop(Stack* s) {
    if (is_stack_empty(s)) {
        return NULL;
    }

    StackNode* temp = s->top;
    GraphNode* data = temp->data;
    s->top = s->top->next;
    free(temp);
    s->size--;
    return data;
}

int is_stack_empty(Stack* s) {
    return s->top == NULL;
}

void stack_free(Stack* s) {
    while (!is_stack_empty(s)) {
        pop(s);
    }
    free(s);
}

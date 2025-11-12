#include "hash_table.h"
#include <stdio.h>
#include <string.h>

HashTable* create_hash_table() {
    HashTable* ht = (HashTable*)malloc(sizeof(HashTable));
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        ht->buckets[i] = NULL;
    }
    ht->size = 0;
    return ht;
}

unsigned int hash(const char* key) {
    unsigned int hash_value = 0;
    while (*key) {
        hash_value = (hash_value << 5) + hash_value + *key;
        key++;
    }
    return hash_value % HASH_TABLE_SIZE;
}

GraphNode* hash_table_insert(HashTable* ht, const char* name) {
    GraphNode* existing = hash_table_find(ht, name);
    if (existing) {
        return existing;
    }

    unsigned int index = hash(name);
    GraphNode* new_node = (GraphNode*)malloc(sizeof(GraphNode));
    new_node->name = (char*)malloc(strlen(name) + 1);
    strcpy(new_node->name, name);
    new_node->edges = NULL;
    new_node->visited = 0;
    new_node->parent = NULL;
    new_node->next_in_bucket = ht->buckets[index];
    ht->buckets[index] = new_node;
    ht->size++;

    return new_node;
}

GraphNode* hash_table_find(HashTable* ht, const char* name) {
    unsigned int index = hash(name);
    GraphNode* current = ht->buckets[index];

    while (current != NULL) {
        if (strcmp(current->name, name) == 0) {
            return current;
        }
        current = current->next_in_bucket;
    }
    return NULL;
}

void add_edge(GraphNode* source, GraphNode* destination, const char* relation) {
    Edge* new_edge = (Edge*)malloc(sizeof(Edge));
    new_edge->relation = (char*)malloc(strlen(relation) + 1);
    strcpy(new_edge->relation, relation);
    new_edge->destination = destination;
    new_edge->next = source->edges;
    source->edges = new_edge;
}

void reset_visited(HashTable* ht) {
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        GraphNode* current = ht->buckets[i];
        while (current != NULL) {
            current->visited = 0;
            current->parent = NULL;
            current = current->next_in_bucket;
        }
    }
}

void hash_table_free(HashTable* ht) {
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        GraphNode* current = ht->buckets[i];
        while (current != NULL) {
            GraphNode* temp = current;
            current = current->next_in_bucket;

            Edge* edge = temp->edges;
            while (edge != NULL) {
                Edge* temp_edge = edge;
                edge = edge->next;
                free(temp_edge->relation);
                free(temp_edge);
            }

            free(temp->name);
            free(temp);
        }
    }
    free(ht);
}

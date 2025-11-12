#ifndef HASH_TABLE_H
#define HASH_TABLE_H

#include <stdlib.h>
#include <string.h>

#define HASH_TABLE_SIZE 1024

typedef struct Edge {
    char* relation;
    struct GraphNode* destination;
    struct Edge* next;
} Edge;

typedef struct GraphNode {
    char* name;
    Edge* edges;
    int visited;
    struct GraphNode* parent;
    struct GraphNode* next_in_bucket;
} GraphNode;

typedef struct HashTable {
    GraphNode* buckets[HASH_TABLE_SIZE];
    int size;
} HashTable;

HashTable* create_hash_table();
unsigned int hash(const char* key);
GraphNode* hash_table_insert(HashTable* ht, const char* name);
GraphNode* hash_table_find(HashTable* ht, const char* name);
void hash_table_free(HashTable* ht);
void add_edge(GraphNode* source, GraphNode* destination, const char* relation);
void reset_visited(HashTable* ht);

#endif

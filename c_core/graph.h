#ifndef GRAPH_H
#define GRAPH_H

#include "hash_table.h"
#include "trie.h"
#include "queue.h"
#include "stack.h"

typedef struct Graph {
    HashTable* nodes;
    Trie* autocomplete_trie;
} Graph;

Graph* create_graph();
void load_graph_from_file(Graph* graph, const char* filename);
void graph_free(Graph* graph);

void bfs_path(Graph* graph, const char* start, const char* end);
void find_topics(Graph* graph);
void mind_map_dfs(Graph* graph, const char* start_node, int depth);
void answer_question(Graph* graph, const char* node_name);
void autocomplete_search(Graph* graph, const char* prefix);

#endif

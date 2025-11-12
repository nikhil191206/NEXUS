#include "graph.h"
#include <stdio.h>
#include <string.h>

Graph* create_graph() {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->nodes = create_hash_table();
    graph->autocomplete_trie = create_trie();
    return graph;
}

void load_graph_from_file(Graph* graph, const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        printf("ERROR: Could not open file %s\n", filename);
        return;
    }

    // INCREASED BUFFER SIZE to prevent overflow from long AI-generated relations
    char line[4096]; 
    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\r\n")] = 0;

        if (strncmp(line, "NODE:", 5) == 0) {
            char* node_name = line + 6;
            hash_table_insert(graph->nodes, node_name);
            trie_insert(graph->autocomplete_trie, node_name);
        }
        else if (strncmp(line, "EDGE:", 5) == 0) {
            // INCREASED BUFFER SIZE to prevent overflow
            char source[1024], relation[1024], dest[1024];
            char* rest = line + 6;

            char* first_pipe = strchr(rest, '|');
            if (!first_pipe) continue;

            int source_len = first_pipe - rest;
            strncpy(source, rest, source_len);
            source[source_len] = '\0';

            rest = first_pipe + 1;
            char* second_pipe = strchr(rest, '|');
            if (!second_pipe) continue;

            int relation_len = second_pipe - rest;
            strncpy(relation, rest, relation_len);
            relation[relation_len] = '\0';

            strcpy(dest, second_pipe + 1);

            GraphNode* source_node = hash_table_find(graph->nodes, source);
            GraphNode* dest_node = hash_table_find(graph->nodes, dest);

            if (source_node && dest_node) {
                add_edge(source_node, dest_node, relation);
            }
        }
    }

    fclose(file);
}

void bfs_path(Graph* graph, const char* start, const char* end) {
    GraphNode* start_node = hash_table_find(graph->nodes, start);
    GraphNode* end_node = hash_table_find(graph->nodes, end);

    if (!start_node || !end_node) {
        printf("ERROR: Node not found\n");
        return;
    }

    reset_visited(graph->nodes);
    Queue* q = create_queue();

    start_node->visited = 1;
    enqueue(q, start_node);

    int found = 0;
    while (!is_queue_empty(q)) {
        GraphNode* current = dequeue(q);

        if (current == end_node) {
            found = 1;
            break;
        }

        Edge* edge = current->edges;
        while (edge != NULL) {
            if (!edge->destination->visited) {
                edge->destination->visited = 1;
                edge->destination->parent = current;
                enqueue(q, edge->destination);
            }
            edge = edge->next;
        }
    }

    if (found) {
        GraphNode* path[1000];
        int path_length = 0;
        GraphNode* current = end_node;

        while (current != NULL) {
            path[path_length++] = current;
            current = current->parent;
        }

        printf("PATH: ");
        for (int i = path_length - 1; i >= 0; i--) {
            printf("%s", path[i]->name);
            if (i > 0) {
                Edge* edge = path[i]->edges;
                while (edge != NULL) {
                    if (edge->destination == path[i - 1]) {
                        printf(" -[%s]-> ", edge->relation);
                        break;
                    }
                    edge = edge->next;
                }
            }
        }
        printf("\n");
    } else {
        printf("NO_PATH\n");
    }

    queue_free(q);
}

// --- TOPICS FIX ---
// Modified to print as it finds nodes, making it O(N)
void dfs_component(GraphNode* node, int component_id) {
    Stack* s = create_stack();
    push(s, node);

    while (!is_stack_empty(s)) {
        GraphNode* current = pop(s);

        if (current->visited) {
            continue;
        }

        current->visited = component_id;
        // PRINTING NODE HERE
        printf("%s, ", current->name);

        Edge* edge = current->edges;
        while (edge != NULL) {
            if (!edge->destination->visited) {
                push(s, edge->destination);
            }
            edge = edge->next;
        }
    }

    stack_free(s);
}

// --- TOPICS FIX ---
// The O(N^2) printing loop has been removed.
void find_topics(Graph* graph) {
    reset_visited(graph->nodes);
    int component_id = 1;

    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        GraphNode* current = graph->nodes->buckets[i];
        while (current != NULL) {
            if (!current->visited) {
                printf("TOPIC_%d: ", component_id);
                dfs_component(current, component_id);
                
                // The old, inefficient printing loop is now gone.
                printf("\n");
                component_id++;
            }
            current = current->next_in_bucket;
        }
    }
}

// --- MIND MAP FIX (Solution B) ---
// This new recursive function outputs clean data for the frontend.
void mind_map_recursive_data(GraphNode* node, int depth, int max_depth) {
    // If we've seen this node *in this path* OR we're too deep, stop.
    if (node->visited || depth > max_depth) {
        return;
    }
    // Mark as visited *for this query*
    node->visited = 1; 

    Edge* edge = node->edges;
    while (edge != NULL) {
        // Print the clean, machine-readable format: "Source|Relation|Target"
        printf("%s|%s|%s\n", node->name, edge->relation, edge->destination->name);
        
        // Recurse to the destination *before* moving to the next edge
        mind_map_recursive_data(edge->destination, depth + 1, max_depth);
        
        edge = edge->next;
    }
}

// --- MIND MAP FIX (Solution B) ---
// This is the new main function your nexus_engine calls.
void mind_map_dfs(Graph* graph, const char* start_node, int max_depth) {
    GraphNode* node = hash_table_find(graph->nodes, start_node);
    if (!node) {
        printf("ERROR: Node not found\n");
        return;
    }

    // Reset all visited flags before starting
    reset_visited(graph->nodes); 
    
    printf("MINDMAP_DATA:\n"); // Header for the frontend to parse
    
    // Start the recursive call
    mind_map_recursive_data(node, 0, max_depth);
}


void answer_question(Graph* graph, const char* node_name) {
    GraphNode* node = hash_table_find(graph->nodes, node_name);
    if (!node) {
        printf("ERROR: Node not found\n");
        return;
    }

    printf("ANSWER: %s is related to: ", node_name);

    Edge* edge = node->edges;
    int count = 0;
    while (edge != NULL) {
        if (count > 0) printf(", ");
        printf("%s (%s)", edge->destination->name, edge->relation);
        count++;
        edge = edge->next;
    }

    if (count == 0) {
        printf("No relationships found");
    }
    printf("\n");
}

void autocomplete_search(Graph* graph, const char* prefix) {
    char* results[50];
    int count = trie_search_prefix(graph->autocomplete_trie, prefix, results, 50);

    if (count == 0) {
        printf("NO_SUGGESTIONS\n");
    } else {
        printf("SUGGESTIONS: ");
        for (int i = 0; i < count; i++) {
            printf("%s", results[i]);
            if (i < count - 1) printf(", ");
        }
        printf("\n");
    }
}

void graph_free(Graph* graph) {
    hash_table_free(graph->nodes);
    trie_free(graph->autocomplete_trie->root);
    free(graph->autocomplete_trie);
    free(graph);
}
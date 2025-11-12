#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "graph.h"

void print_usage() {
    printf("Usage: nexus_engine --file <graph_file> --query <query_type> [options]\n\n");
    printf("Query Types:\n");
    printf("  path --start <node> --end <node>     Find shortest path between nodes\n");
    printf("  topics                                Discover disconnected topic clusters\n");
    printf("  mindmap --start <node>                Generate mind map from a node\n");
    printf("  qa --node <node>                      Answer questions about a node\n");
    printf("  complete --prefix <prefix>            Autocomplete suggestions\n\n");
    printf("Examples:\n");
    printf("  nexus_engine --file data.txt --query path --start BERT --end NLP\n");
    printf("  nexus_engine --file data.txt --query topics\n");
    printf("  nexus_engine --file data.txt --query complete --prefix Conv\n");
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        print_usage();
        return 1;
    }

    char* filename = NULL;
    char* query_type = NULL;
    char* start_node = NULL;
    char* end_node = NULL;
    char* node_name = NULL;
    char* prefix = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--file") == 0 && i + 1 < argc) {
            filename = argv[++i];
        } else if (strcmp(argv[i], "--query") == 0 && i + 1 < argc) {
            query_type = argv[++i];
        } else if (strcmp(argv[i], "--start") == 0 && i + 1 < argc) {
            start_node = argv[++i];
        } else if (strcmp(argv[i], "--end") == 0 && i + 1 < argc) {
            end_node = argv[++i];
        } else if (strcmp(argv[i], "--node") == 0 && i + 1 < argc) {
            node_name = argv[++i];
        } else if (strcmp(argv[i], "--prefix") == 0 && i + 1 < argc) {
            prefix = argv[++i];
        }
    }

    if (!filename || !query_type) {
        printf("ERROR: Missing required arguments\n");
        print_usage();
        return 1;
    }

    Graph* graph = create_graph();
    load_graph_from_file(graph, filename);

    if (strcmp(query_type, "path") == 0) {
        if (!start_node || !end_node) {
            printf("ERROR: Path query requires --start and --end\n");
            graph_free(graph);
            return 1;
        }
        bfs_path(graph, start_node, end_node);
    }
    else if (strcmp(query_type, "topics") == 0) {
        find_topics(graph);
    }
    else if (strcmp(query_type, "mindmap") == 0) {
        if (!start_node) {
            printf("ERROR: Mindmap query requires --start\n");
            graph_free(graph);
            return 1;
        }
        mind_map_dfs(graph, start_node, 5);
    }
    else if (strcmp(query_type, "qa") == 0) {
        if (!node_name) {
            printf("ERROR: QA query requires --node\n");
            graph_free(graph);
            return 1;
        }
        answer_question(graph, node_name);
    }
    else if (strcmp(query_type, "complete") == 0) {
        if (!prefix) {
            printf("ERROR: Complete query requires --prefix\n");
            graph_free(graph);
            return 1;
        }
        autocomplete_search(graph, prefix);
    }
    else {
        printf("ERROR: Unknown query type: %s\n", query_type);
        print_usage();
        graph_free(graph);
        return 1;
    }

    graph_free(graph);
    return 0;
}

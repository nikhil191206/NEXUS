#ifndef TRIE_H
#define TRIE_H

#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define ALPHABET_SIZE 256

typedef struct TrieNode {
    struct TrieNode* children[ALPHABET_SIZE];
    int is_end_of_word;
    char* word;
} TrieNode;

typedef struct Trie {
    TrieNode* root;
} Trie;

Trie* create_trie();
TrieNode* create_trie_node();
void trie_insert(Trie* trie, const char* word);
void trie_autocomplete(TrieNode* node, char** results, int* count, int max_results);
int trie_search_prefix(Trie* trie, const char* prefix, char** results, int max_results);
void trie_free(TrieNode* node);

#endif

#include "trie.h"
#include <stdio.h>
#include <string.h>

Trie* create_trie() {
    Trie* trie = (Trie*)malloc(sizeof(Trie));
    trie->root = create_trie_node();
    return trie;
}

TrieNode* create_trie_node() {
    TrieNode* node = (TrieNode*)malloc(sizeof(TrieNode));
    node->is_end_of_word = 0;
    node->word = NULL;
    for (int i = 0; i < ALPHABET_SIZE; i++) {
        node->children[i] = NULL;
    }
    return node;
}

void trie_insert(Trie* trie, const char* word) {
    TrieNode* current = trie->root;

    for (int i = 0; word[i] != '\0'; i++) {
        unsigned char index = (unsigned char)word[i];
        if (current->children[index] == NULL) {
            current->children[index] = create_trie_node();
        }
        current = current->children[index];
    }

    current->is_end_of_word = 1;
    current->word = (char*)malloc(strlen(word) + 1);
    strcpy(current->word, word);
}

void trie_autocomplete(TrieNode* node, char** results, int* count, int max_results) {
    if (*count >= max_results) {
        return;
    }

    if (node->is_end_of_word) {
        results[*count] = node->word;
        (*count)++;
    }

    for (int i = 0; i < ALPHABET_SIZE; i++) {
        if (node->children[i] != NULL) {
            trie_autocomplete(node->children[i], results, count, max_results);
        }
    }
}

int trie_search_prefix(Trie* trie, const char* prefix, char** results, int max_results) {
    TrieNode* current = trie->root;

    for (int i = 0; prefix[i] != '\0'; i++) {
        unsigned char index = (unsigned char)prefix[i];
        if (current->children[index] == NULL) {
            return 0;
        }
        current = current->children[index];
    }

    int count = 0;
    trie_autocomplete(current, results, &count, max_results);
    return count;
}

void trie_free(TrieNode* node) {
    if (node == NULL) {
        return;
    }

    for (int i = 0; i < ALPHABET_SIZE; i++) {
        if (node->children[i] != NULL) {
            trie_free(node->children[i]);
        }
    }

    if (node->word != NULL) {
        free(node->word);
    }
    free(node);
}

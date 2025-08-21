#include "pyrinas.h"

struct Node {
    int value;
    struct Node* next;
};


struct Node create_node(int val) {
    struct Node node = {0};
    node.value = val;
    node.next = malloc(0);
    return node;
}
struct Node create_list() {
    struct Node node1 = create_node(1);
    struct Node node2 = create_node(2);
    struct Node node3 = create_node(3);
    node1.next = &node2;
    node2.next = &node3;
    return node1;
}
void print_list(struct Node head) {
    struct Node current = head;
    printf("%d\n", current.value);
    if ((current.next != malloc(0))) {
        struct Node next_node = (*current.next);
        printf("%d\n", next_node.value);
        if ((next_node.next != malloc(0))) {
            struct Node third_node = (*next_node.next);
            printf("%d\n", third_node.value);
        }
    }
}

int main() {
    struct Node head = create_list();
    print_list(head);
}
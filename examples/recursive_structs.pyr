# This tests if we can have recursive struct definitions using pointers
class Node:
    value: int
    next: 'ptr[Node]'  # Recursive reference via pointer

def create_node(val: int) -> Node:
    node: Node = Node()
    node.value = val
    # Initialize next to null pointer (0)
    node.next = malloc(0)  # This will be treated as null
    return node

def create_list() -> Node:
    # Create a simple linked list: 1 -> 2 -> 3
    node1: Node = create_node(1)
    node2: Node = create_node(2) 
    node3: Node = create_node(3)
    
    # Link them together
    node1.next = addr(node2)
    node2.next = addr(node3)
    
    return node1

def print_list(head: Node) -> None:
    current: Node = head
    print(current.value)
    
    # Print second node if it exists
    if current.next != malloc(0):
        next_node: Node = deref(current.next)
        print(next_node.value)
        
        # Print third node if it exists
        if next_node.next != malloc(0):
            third_node: Node = deref(next_node.next)
            print(third_node.value)

def main():
    head: Node = create_list()
    print_list(head)
# Test simple recursive struct capability
class Node:
    value: int
    next: 'ptr[Node]'

def main():
    # Test that recursive struct definition compiles
    node1: Node = Node() 
    node2: Node = Node()
    
    node1.value = 42
    node2.value = 84
    
    # Test pointer field assignment
    node1.next = addr(node2)
    
    # Test access through pointer
    print(node1.value)        # Should print 42
    next_node: Node = deref(node1.next)
    print(next_node.value)    # Should print 84
    
    # Test that struct definition is correct
    print(node2.value)        # Should print 84
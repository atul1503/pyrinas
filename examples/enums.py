from typing import Enum

class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

class Status(Enum):
    PENDING = 1
    RUNNING = 2
    COMPLETED = 3
    FAILED = 4

def main():
    current_color: Color = Color.RED
    status: Status = Status.PENDING
    
    if current_color == Color.RED:
        print("Red color selected")
    
    if status == Status.PENDING:
        print("Status is pending")
    
    # Print enum values as integers
    print(int(current_color))  # Should print 0
    print(int(status))         # Should print 1
    
    # Test different enum values
    next_color: Color = Color.BLUE
    print(int(next_color))     # Should print 2
    
    final_status: Status = Status.COMPLETED
    print(int(final_status))   # Should print 3
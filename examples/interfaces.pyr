# Interface definition
class Drawable:
    def draw(self) -> None: pass
    def get_area(self) -> float: pass

# Struct implementing interface
class Rectangle(Drawable):
    width: int
    height: int
    
    def draw(self) -> None:
        print("Drawing rectangle")
    
    def get_area(self) -> float:
        return float(self.width * self.height)

class Circle(Drawable):
    radius: int
    
    def draw(self) -> None:
        print("Drawing circle")
    
    def get_area(self) -> float:
        return float(3 * self.radius * self.radius)

def main():
    rect: Rectangle = Rectangle()
    rect.width = 10
    rect.height = 5
    rect.draw()
    area: float = rect.get_area()
    print(int(area))
    
    circle: Circle = Circle()
    circle.radius = 3
    circle.draw()
    circle_area: float = circle.get_area()
    print(int(circle_area))
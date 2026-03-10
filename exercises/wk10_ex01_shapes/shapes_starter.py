"""
Shape Drawing System Exercise
==============================

This is your starter file. Implement the Shape, Circle, Rectangle,
Triangle, and Canvas classes above the main() function to make the
program run successfully.

Your task:
1. Create the Shape base class with all required attributes and methods
2. Create Circle, Rectangle, and Triangle subclasses that inherit from Shape
3. Create the Canvas class to hold a collection of shapes
4. Run `python shapes.py` to test your implementation
5. Run `pytest test_shapes.py -v` to verify all tests pass

Key OOP concepts to use:
- class SubClass(ParentClass):  to inherit from a parent
- super().__init__(...)         to call the parent constructor
- def method(self):            to override a parent method
- super().method()             to call the parent version of a method
"""

import math

# ---------------------------------------------------------------------------
# TODO 1: Implement the Shape base class
# ---------------------------------------------------------------------------
#
# Requirements:
#   Class attributes:
#     - VALID_COLORS: list of valid color strings
#         ["red", "blue", "green", "yellow", "orange", "purple", "black", "white"]
#     - _total_shapes: int, counts every Shape (and subclass) instance created
#
#   __init__(self, color: str)
#     - Validate the color using is_valid_color(); raise ValueError if invalid
#     - Increment _total_shapes
#     - Store color as self._color (protected)
#
#   @classmethod get_total_shapes(cls) -> int
#     - Return cls._total_shapes
#
#   @staticmethod is_valid_color(color: str) -> bool
#     - Return True if color.lower() is in VALID_COLORS, False otherwise
#
#   @property color -> str
#     - Return self._color
#
#   @color.setter color(value: str)
#     - Validate with is_valid_color(); raise ValueError if invalid
#     - Update self._color
#
#   def area(self) -> float
#     - raise NotImplementedError("Subclasses must implement area()")
#
#   def perimeter(self) -> float
#     - raise NotImplementedError("Subclasses must implement perimeter()")
#
#   def describe(self) -> str
#     - Return: f"A {self._color} shape with area={self.area():.2f} and perimeter={self.perimeter():.2f}"
#     - (Subclasses will call super().describe() to extend this)
#
#   def __str__(self) -> str
#     - Return: f"Shape(color='{self._color}')"


# ---------------------------------------------------------------------------
# TODO 2: Implement the Circle subclass
# ---------------------------------------------------------------------------
#
# class Circle(Shape):   <-- inherit from Shape
#
#   __init__(self, color: str, radius: float)
#     - Call super().__init__(color)  <-- runs Shape's __init__ first!
#     - Validate radius > 0; raise ValueError if not
#     - Store as self._radius (protected)
#
#   @property radius -> float
#     - Return self._radius
#
#   def area(self) -> float
#     - Return math.pi * self._radius ** 2   (π × r²)
#
#   def perimeter(self) -> float
#     - Return 2 * math.pi * self._radius    (circumference = 2πr)
#
#   def describe(self) -> str
#     - Call base = super().describe()  <-- extends the Shape description
#     - Return f"{base} | Circle with radius={self._radius}"
#
#   def __str__(self) -> str
#     - Return f"Circle(color='{self._color}', radius={self._radius})"


# ---------------------------------------------------------------------------
# TODO 3: Implement the Rectangle subclass
# ---------------------------------------------------------------------------
#
# class Rectangle(Shape):   <-- inherit from Shape
#
#   __init__(self, color: str, width: float, height: float)
#     - Call super().__init__(color)
#     - Validate width > 0 and height > 0; raise ValueError for each if not
#     - Store as self._width and self._height (protected)
#
#   @property width -> float
#   @property height -> float
#
#   def area(self) -> float
#     - Return self._width * self._height
#
#   def perimeter(self) -> float
#     - Return 2 * (self._width + self._height)
#
#   def describe(self) -> str
#     - Call base = super().describe()
#     - Return f"{base} | Rectangle {self._width}×{self._height}"
#
#   def __str__(self) -> str
#     - Return f"Rectangle(color='{self._color}', width={self._width}, height={self._height})"


# ---------------------------------------------------------------------------
# TODO 4: Implement the Triangle subclass
# ---------------------------------------------------------------------------
#
# class Triangle(Shape):   <-- inherit from Shape
#
#   __init__(self, color: str, side_a: float, side_b: float, side_c: float)
#     - Call super().__init__(color)
#     - Validate all sides > 0; raise ValueError if not
#     - Validate triangle inequality (a+b > c, b+c > a, a+c > b)
#       raise ValueError if violated
#     - Store as self._side_a, self._side_b, self._side_c (protected)
#
#   @property sides -> tuple
#     - Return (self._side_a, self._side_b, self._side_c)
#
#   def area(self) -> float
#     - Use Heron's formula:
#         s = perimeter / 2
#         area = math.sqrt(s * (s-a) * (s-b) * (s-c))
#
#   def perimeter(self) -> float
#     - Return self._side_a + self._side_b + self._side_c
#
#   def describe(self) -> str
#     - Call base = super().describe()
#     - Return f"{base} | Triangle with sides {self._side_a}/{self._side_b}/{self._side_c}"
#
#   def __str__(self) -> str
#     - Return f"Triangle(color='{self._color}', sides={self._side_a}/{self._side_b}/{self._side_c})"


# ---------------------------------------------------------------------------
# TODO 5: Implement the Canvas class
# ---------------------------------------------------------------------------
#
# class Canvas:
#
#   __init__(self, name: str)
#     - Store name as self.name (public)
#     - Initialize self._shapes as an empty list
#
#   def add_shape(self, shape: Shape)
#     - Append the shape to self._shapes
#     - Print: f"Added {shape} to '{self.name}'."
#
#   def find_by_color(self, color: str) -> list
#     - Return a list of shapes whose color matches (case-insensitive)
#
#   @property shape_count -> int
#     - Return len(self._shapes)
#
#   @property total_area -> float
#     - Return the sum of area() for all shapes
#
#   def largest_shape(self) -> Shape or None
#     - Return the shape with the greatest area()
#     - Return None if the canvas is empty
#
#   def describe_all(self)
#     - For each shape, print shape.describe()


def main():
    """Demonstration of the shape drawing system with inheritance."""

    # 1. Print header
    print("Shape Drawing System Demo")
    print("=" * 50)

    # 2. Test static method (no object needed)
    print("\nTesting color validation...")
    print(f"Is 'red' a valid color?     {Shape.is_valid_color('red')}")
    print(f"Is 'magenta' a valid color? {Shape.is_valid_color('magenta')}")

    # 3. Display initial shape count (class method, no object needed)
    print(f"\nInitial shape count: {Shape.get_total_shapes()}")

    # 4. Create canvas
    canvas = Canvas("My Drawing")

    # 5. Create shapes — each subclass calls super().__init__(color) internally
    circle = Circle("red", 5.0)
    rect = Rectangle("blue", 4.0, 6.0)
    tri = Triangle("green", 3.0, 4.0, 5.0)

    # 6. Add shapes to canvas (polymorphism — canvas accepts any Shape)
    canvas.add_shape(circle)
    canvas.add_shape(rect)
    canvas.add_shape(tri)

    # 7. Display canvas statistics
    print(f"\nCanvas: '{canvas.name}'")
    print(f"Total shapes on canvas: {canvas.shape_count}")
    print(f"Total area:             {canvas.total_area:.2f}")
    print(f"Total shapes ever created: {Shape.get_total_shapes()}")

    # 8. Describe all shapes — polymorphism: same call, different behavior
    print(f"\nDescribing all shapes:")
    canvas.describe_all()

    # 9. Find the largest shape
    biggest = canvas.largest_shape()
    print(f"\nLargest shape: {biggest}")

    # 10. Find shapes by color
    print(f"\nSearching for red shapes...")
    red_shapes = canvas.find_by_color("red")
    print(f"Found {len(red_shapes)} red shape(s).")

    # 11. Demonstrate isinstance() and polymorphism
    print(f"\nDemonstrating isinstance() checks:")
    for shape in [circle, rect, tri]:
        print(f"  {shape}")
        print(f"    → isinstance(shape, Shape)?     {isinstance(shape, Shape)}")
        print(f"    → isinstance(shape, Circle)?    {isinstance(shape, Circle)}")
        print(f"    → isinstance(shape, Rectangle)? {isinstance(shape, Rectangle)}")

    # 12. Use the inherited color property setter
    print(f"\nChanging circle color from red to purple...")
    circle.color = "purple"
    print(f"Circle color is now: {circle.color}")


if __name__ == "__main__":
    main()

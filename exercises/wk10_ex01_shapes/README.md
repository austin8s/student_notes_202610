# Introduction to OOP Inheritance Exercise

## Overview

In this exercise, you'll build a **Shape Drawing System** to practice
**object-oriented inheritance** — one of the most important concepts in
object-oriented programming.

You will implement:

- A **base class** (`Shape`) that defines a shared interface
- Three **subclasses** (`Circle`, `Rectangle`, `Triangle`) that inherit
  from `Shape`
- A **container class** (`Canvas`) that holds a collection of shapes

**Concepts practiced:**

- Defining a subclass: `class Circle(Shape):`
- Calling the parent constructor: `super().__init__(color)`
- Overriding methods: `area()`, `perimeter()`, `describe()`, `__str__()`
- Extending parent methods: `base = super().describe()`
- Polymorphism — calling the same method on different object types
- `isinstance()` checks

**Estimated Time:** 60 minutes

**Files Provided:**

- `test_shapes.py` — A comprehensive pytest test suite (do not modify)
- `shapes_starter.py` — Starter template with `main()` provided

**Files You'll Create:**

- `shapes.py` — Your implementation of all five classes

---

## Background: What Is Inheritance?

Inheritance lets one class **reuse and extend** the behavior of another:

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Subclasses must implement speak()")


class Dog(Animal):           # Dog inherits from Animal
    def __init__(self, name, breed):
        super().__init__(name)   # Call Animal's __init__ first
        self.breed = breed

    def speak(self):             # Override Animal's speak()
        return "Woof!"


class Cat(Animal):
    def speak(self):
        return "Meow!"


# Polymorphism: same code, different behavior
animals = [Dog("Rex", "Labrador"), Cat("Whiskers")]
for animal in animals:
    print(animal.speak())   # Calls Dog.speak() or Cat.speak() automatically
```

**Key rules:**

| Concept | Syntax | When to use |
|---|---|---|
| Inherit from a class | `class Sub(Parent):` | When Sub IS-A Parent |
| Call parent constructor | `super().__init__(...)` | Always in `__init__` |
| Override a method | Redefine `def method(self):` in the subclass | When behavior differs |
| Extend a method | `result = super().method()` then add more | When you want parent + extra |

---

## Scenario

You are building a simple shape drawing system. There are three types of
shapes — circles, rectangles, and triangles. All shapes share certain
properties (a color) and behaviors (they have an area and a perimeter), but
each shape calculates these differently.

**Your Goal:** Implement the five classes so that the provided `main()`
function runs successfully and all pytest tests pass.

---

## Project Setup

### 1. Create Project Directory

```powershell
mkdir shapes_inheritance_oo
cd shapes_inheritance_oo
```

### 2. Initialize Python Environment with uv

```powershell
uv init
uv venv

# Activate (Windows PowerShell):
.venv\Scripts\Activate.ps1

# Activate (macOS/Linux):
source .venv/bin/activate
```

### 3. Install Dependencies

```powershell
uv add --dev pytest
```

### 4. Configure VSCode

Create `.vscode/settings.json`:

```json
{
  "python.testing.pytestArgs": ["."],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true
}
```

### 5. Copy Provided Files

Copy both files into your project directory:

- [`test_shapes.py`](./test_shapes.py) — pytest test suite
- [`shapes_starter.py`](./shapes_starter.py) — Starter template

Rename `shapes_starter.py` to `shapes.py` to begin working:

```powershell
Copy-Item shapes_starter.py shapes.py
```

### 6. Verify Setup

```powershell
pytest --version
python shapes.py   # Will fail until you implement the classes
```

### Project Structure

```
shapes_inheritance_oo/
├── .venv/
├── .vscode/
│   └── settings.json
├── test_shapes.py       # Provided — do not modify
└── shapes.py            # Your implementation (copy of shapes_starter.py)
```

---

## Your Goal: Complete the Classes

The `shapes_starter.py` file contains a complete `main()` function. **Your
job is to implement the five classes above it so the program runs and all
tests pass.**

---

## Class Requirements

### Class 1: `Shape` (Base Class)

The `Shape` class defines the shared interface for all shapes.

#### Class Attributes

```python
VALID_COLORS = ["red", "blue", "green", "yellow",
                "orange", "purple", "black", "white"]
_total_shapes = 0   # counts every Shape and subclass instance
```

#### `__init__(self, color: str)`

- Validate `color` using `is_valid_color()`; raise `ValueError` if invalid
- Increment `Shape._total_shapes`
- Store as `self._color` (protected)

#### `@classmethod get_total_shapes(cls) -> int`

Return `cls._total_shapes`.

#### `@staticmethod is_valid_color(color: str) -> bool`

Return `True` if `color.lower()` is in `VALID_COLORS`.

#### `@property color` and `@color.setter`

- Getter: return `self._color`
- Setter: validate with `is_valid_color()`, raise `ValueError` if invalid,
  otherwise update `self._color`

#### `def area(self) -> float`

Raise `NotImplementedError("Subclasses must implement area()")`.

#### `def perimeter(self) -> float`

Raise `NotImplementedError("Subclasses must implement perimeter()")`.

#### `def describe(self) -> str`

Return:
```
f"A {self._color} shape with area={self.area():.2f} and perimeter={self.perimeter():.2f}"
```

#### `def __str__(self) -> str`

Return `f"Shape(color='{self._color}')"`.

---

### Class 2: `Circle(Shape)` (Subclass)

```python
class Circle(Shape):   # <-- inherits from Shape
```

#### `__init__(self, color: str, radius: float)`

```python
super().__init__(color)   # MUST call parent constructor first
```

- Validate `radius > 0`; raise `ValueError` if not
- Store as `self._radius`

#### `@property radius -> float`

Return `self._radius`.

#### `def area(self) -> float`

Area of a circle: **π × r²**

```python
import math
return math.pi * self._radius ** 2
```

#### `def perimeter(self) -> float`

Circumference: **2 × π × r**

```python
return 2 * math.pi * self._radius
```

#### `def describe(self) -> str`

```python
base = super().describe()   # call Shape's describe() first
return f"{base} | Circle with radius={self._radius}"
```

#### `def __str__(self) -> str`

Return `f"Circle(color='{self._color}', radius={self._radius})"`.

---

### Class 3: `Rectangle(Shape)` (Subclass)

#### `__init__(self, color: str, width: float, height: float)`

```python
super().__init__(color)
```

- Validate `width > 0` and `height > 0`; raise `ValueError` for each
- Store as `self._width`, `self._height`

#### Properties: `width`, `height`

Return `self._width` and `self._height` respectively.

#### `def area(self) -> float`

Area of a rectangle: **width × height**

#### `def perimeter(self) -> float`

Perimeter: **2 × (width + height)**

#### `def describe(self) -> str`

```python
base = super().describe()
return f"{base} | Rectangle {self._width}×{self._height}"
```

#### `def __str__(self) -> str`

Return `f"Rectangle(color='{self._color}', width={self._width}, height={self._height})"`.

---

### Class 4: `Triangle(Shape)` (Subclass)

#### `__init__(self, color: str, side_a: float, side_b: float, side_c: float)`

```python
super().__init__(color)
```

- Validate all sides > 0; raise `ValueError` if not
- Validate the **triangle inequality**: any two sides must sum to more than
  the third side. Raise `ValueError` if violated:
  - `side_a + side_b > side_c`
  - `side_b + side_c > side_a`
  - `side_a + side_c > side_b`
- Store as `self._side_a`, `self._side_b`, `self._side_c`

#### `@property sides -> tuple`

Return `(self._side_a, self._side_b, self._side_c)`.

#### `def area(self) -> float`

Use **Heron's formula**:

```
s = perimeter / 2
area = √(s × (s - a) × (s - b) × (s - c))
```

```python
s = self.perimeter() / 2
return math.sqrt(s * (s - self._side_a) * (s - self._side_b) * (s - self._side_c))
```

Tip: a 3-4-5 right triangle has area = **6.0**. Use this to check your work.

#### `def perimeter(self) -> float`

Return `self._side_a + self._side_b + self._side_c`.

#### `def describe(self) -> str`

```python
base = super().describe()
return f"{base} | Triangle with sides {self._side_a}/{self._side_b}/{self._side_c}"
```

#### `def __str__(self) -> str`

Return `f"Triangle(color='{self._color}', sides={self._side_a}/{self._side_b}/{self._side_c})"`.

---

### Class 5: `Canvas`

A container that holds shapes and demonstrates **polymorphism**.

#### `__init__(self, name: str)`

- Store `self.name` (public)
- Initialize `self._shapes = []`

#### `def add_shape(self, shape: Shape)`

Append `shape` to `self._shapes` and print:

```
Added <shape> to '<canvas_name>'.
```

#### `def find_by_color(self, color: str) -> list`

Return a list of shapes whose `color` matches (case-insensitive).

#### `@property shape_count -> int`

Return `len(self._shapes)`.

#### `@property total_area -> float`

Return the sum of `area()` for all shapes on the canvas.

#### `def largest_shape(self)`

Return the shape with the greatest `area()`, or `None` if the canvas is empty.

Hint: define a helper function `def get_area(shape): return shape.area()` and pass it as the `key` argument to `max()`.

#### `def describe_all(self)`

For each shape in `self._shapes`, print `shape.describe()`.

---

## Running Your Code

```powershell
# Run the main() function
python shapes.py

# Run all tests
pytest test_shapes.py -v

# Run a specific test class
pytest test_shapes.py::TestInheritance -v

# Run with coverage
pytest test_shapes.py --cov=shapes --cov-report=term-missing
```

---

## Suggested Order of Implementation

Work through the classes in this order — the tests build on each other:

1. **`Shape`** — base class (static method, class method, property, stubs)
2. **`Circle`** — simplest subclass (one extra attribute: radius)
3. **`Rectangle`** — two extra attributes (width, height)
4. **`Triangle`** — three sides, two validation checks, Heron's formula
5. **`Canvas`** — container; tests polymorphism across all three shape types

Run `pytest test_shapes.py -v` after each class to track progress.

---

## Discussion Questions

After completing the exercise, discuss with your partner:

1. What would happen if `Circle.__init__` forgot to call `super().__init__(color)`?
   Try it and observe the error.

2. Why does `Shape._total_shapes` increment correctly even when you create a
   `Circle` or `Rectangle`? Where does the increment happen?

3. In `Canvas.describe_all()`, Python calls a different `describe()` method
   for each shape. How does Python know which one to call?

4. The `Canvas.find_by_color()` and `Canvas.total_area` work with any shape
   type. What OOP concept makes this possible?

5. What is the difference between `isinstance(c, Circle)` and
   `isinstance(c, Shape)` for a `Circle` object `c`?

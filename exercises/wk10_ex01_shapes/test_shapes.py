"""
Test suite for the Shape Drawing System (Inheritance Exercise).

This test file demonstrates pytest class-based test organization and
provides comprehensive testing for the Shape, Circle, Rectangle, Triangle,
and Canvas classes.

Run tests with: pytest test_shapes.py -v

Tests cover:
- Static methods (color validation)
- Class methods and attributes (shape counter)
- Base class behavior (NotImplementedError, property, setter)
- Circle, Rectangle, Triangle creation and calculations
- Inheritance relationships (isinstance, polymorphism)
- super() usage verified through describe() output
- Canvas container methods
"""

import math

import pytest
from shapes import Canvas, Circle, Rectangle, Shape, Triangle

# ---------------------------------------------------------------------------
# Static Methods
# ---------------------------------------------------------------------------


class TestShapeStaticMethods:
    """Test static methods of the Shape class."""

    def test_is_valid_color_with_valid_colors(self):
        """All VALID_COLORS entries are accepted."""
        for color in Shape.VALID_COLORS:
            assert Shape.is_valid_color(color) is True

    def test_is_valid_color_case_insensitive(self):
        """Color validation is case-insensitive."""
        assert Shape.is_valid_color("RED") is True
        assert Shape.is_valid_color("Blue") is True
        assert Shape.is_valid_color("GREEN") is True

    def test_is_valid_color_with_invalid_color(self):
        """Unknown color names return False."""
        assert Shape.is_valid_color("magenta") is False
        assert Shape.is_valid_color("pink") is False
        assert Shape.is_valid_color("") is False

    def test_is_valid_color_returns_bool(self):
        """Return type is always bool."""
        assert isinstance(Shape.is_valid_color("red"), bool)
        assert isinstance(Shape.is_valid_color("neon"), bool)


# ---------------------------------------------------------------------------
# Class Methods / Class Attribute
# ---------------------------------------------------------------------------


class TestShapeClassMethods:
    """Test class methods and the _total_shapes class attribute."""

    def setup_method(self):
        """Reset the shape counter before each test."""
        Shape._total_shapes = 0

    def test_total_shapes_starts_at_zero(self):
        """Counter starts at zero after reset."""
        assert Shape.get_total_shapes() == 0

    def test_total_shapes_increments_for_circle(self):
        """Creating a Circle increments the counter."""
        Circle("red", 5.0)
        assert Shape.get_total_shapes() == 1

    def test_total_shapes_increments_for_rectangle(self):
        """Creating a Rectangle increments the counter."""
        Rectangle("blue", 4.0, 6.0)
        assert Shape.get_total_shapes() == 1

    def test_total_shapes_increments_for_triangle(self):
        """Creating a Triangle increments the counter."""
        Triangle("green", 3.0, 4.0, 5.0)
        assert Shape.get_total_shapes() == 1

    def test_total_shapes_counts_all_subclasses(self):
        """Counter accumulates across all subclass instances."""
        Circle("red", 5.0)
        Rectangle("blue", 4.0, 6.0)
        Triangle("green", 3.0, 4.0, 5.0)
        assert Shape.get_total_shapes() == 3


# ---------------------------------------------------------------------------
# Base Class Behavior
# ---------------------------------------------------------------------------


class TestShapeBase:
    """Test Shape base class behavior."""

    def test_invalid_color_raises_value_error(self):
        """Creating any shape with an invalid color raises ValueError."""
        with pytest.raises(ValueError, match="Invalid color"):
            Circle("magenta", 5.0)

    def test_area_raises_not_implemented(self):
        """Calling area() on a bare Shape instance raises NotImplementedError."""
        shape = Shape.__new__(Shape)
        shape._color = "red"
        with pytest.raises(NotImplementedError):
            shape.area()

    def test_perimeter_raises_not_implemented(self):
        """Calling perimeter() on a bare Shape raises NotImplementedError."""
        shape = Shape.__new__(Shape)
        shape._color = "red"
        with pytest.raises(NotImplementedError):
            shape.perimeter()

    def test_color_property_returns_color(self):
        """color property returns the color string."""
        c = Circle("red", 5.0)
        assert c.color == "red"

    def test_color_setter_accepts_valid_color(self):
        """color setter updates the color when valid."""
        c = Circle("red", 5.0)
        c.color = "blue"
        assert c.color == "blue"

    def test_color_setter_rejects_invalid_color(self):
        """color setter raises ValueError for invalid colors."""
        c = Circle("red", 5.0)
        with pytest.raises(ValueError):
            c.color = "magenta"

    def test_color_property_is_read_write(self):
        """color can be read and written via the property."""
        c = Circle("red", 5.0)
        c.color = "green"
        assert c.color == "green"


# ---------------------------------------------------------------------------
# Circle
# ---------------------------------------------------------------------------


class TestCircle:
    """Test the Circle subclass."""

    def test_circle_creation_stores_attributes(self):
        """Circle stores color and radius correctly."""
        c = Circle("red", 5.0)
        assert c.color == "red"
        assert c.radius == 5.0

    def test_circle_invalid_radius_zero_raises_error(self):
        """Zero radius raises ValueError."""
        with pytest.raises(ValueError):
            Circle("red", 0.0)

    def test_circle_invalid_radius_negative_raises_error(self):
        """Negative radius raises ValueError."""
        with pytest.raises(ValueError):
            Circle("red", -3.0)

    def test_circle_area_formula(self):
        """Area = π × r²."""
        c = Circle("red", 5.0)
        assert c.area() == pytest.approx(math.pi * 25.0, rel=1e-6)

    def test_circle_area_radius_one(self):
        """Area of unit circle = π."""
        c = Circle("blue", 1.0)
        assert c.area() == pytest.approx(math.pi, rel=1e-6)

    def test_circle_perimeter_formula(self):
        """Perimeter (circumference) = 2 × π × r."""
        c = Circle("red", 5.0)
        assert c.perimeter() == pytest.approx(2 * math.pi * 5.0, rel=1e-6)

    def test_circle_str_contains_expected_info(self):
        """__str__ includes class name, color, and radius."""
        c = Circle("red", 5.0)
        s = str(c)
        assert "Circle" in s
        assert "red" in s
        assert "5.0" in s

    def test_circle_describe_contains_color(self):
        """describe() output contains the color (inherited from Shape.describe)."""
        c = Circle("red", 5.0)
        assert "red" in c.describe()

    def test_circle_describe_contains_circle_keyword(self):
        """describe() includes the word 'Circle' (subclass extension)."""
        c = Circle("red", 5.0)
        assert "Circle" in c.describe()

    def test_circle_describe_contains_radius(self):
        """describe() output mentions the radius value."""
        c = Circle("red", 5.0)
        assert "5.0" in c.describe()


# ---------------------------------------------------------------------------
# Rectangle
# ---------------------------------------------------------------------------


class TestRectangle:
    """Test the Rectangle subclass."""

    def test_rectangle_creation_stores_attributes(self):
        """Rectangle stores color, width, and height correctly."""
        r = Rectangle("blue", 4.0, 6.0)
        assert r.color == "blue"
        assert r.width == 4.0
        assert r.height == 6.0

    def test_rectangle_invalid_width_raises_error(self):
        """Non-positive width raises ValueError."""
        with pytest.raises(ValueError):
            Rectangle("blue", -1.0, 6.0)
        with pytest.raises(ValueError):
            Rectangle("blue", 0.0, 6.0)

    def test_rectangle_invalid_height_raises_error(self):
        """Non-positive height raises ValueError."""
        with pytest.raises(ValueError):
            Rectangle("blue", 4.0, -1.0)
        with pytest.raises(ValueError):
            Rectangle("blue", 4.0, 0.0)

    def test_rectangle_area_formula(self):
        """Area = width × height."""
        r = Rectangle("blue", 4.0, 6.0)
        assert r.area() == pytest.approx(24.0, rel=1e-6)

    def test_rectangle_perimeter_formula(self):
        """Perimeter = 2 × (width + height)."""
        r = Rectangle("blue", 4.0, 6.0)
        assert r.perimeter() == pytest.approx(20.0, rel=1e-6)

    def test_rectangle_square_area(self):
        """A square is a valid rectangle; area = side²."""
        r = Rectangle("green", 5.0, 5.0)
        assert r.area() == pytest.approx(25.0, rel=1e-6)

    def test_rectangle_square_perimeter(self):
        """A square's perimeter = 4 × side."""
        r = Rectangle("green", 5.0, 5.0)
        assert r.perimeter() == pytest.approx(20.0, rel=1e-6)

    def test_rectangle_str_contains_expected_info(self):
        """__str__ includes class name, color, width, and height."""
        r = Rectangle("blue", 4.0, 6.0)
        s = str(r)
        assert "Rectangle" in s
        assert "blue" in s

    def test_rectangle_describe_contains_color(self):
        """describe() output contains the color (inherited from Shape.describe)."""
        r = Rectangle("blue", 4.0, 6.0)
        assert "blue" in r.describe()

    def test_rectangle_describe_contains_rectangle_keyword(self):
        """describe() includes the word 'Rectangle' (subclass extension)."""
        r = Rectangle("blue", 4.0, 6.0)
        assert "Rectangle" in r.describe()


# ---------------------------------------------------------------------------
# Triangle
# ---------------------------------------------------------------------------


class TestTriangle:
    """Test the Triangle subclass."""

    def test_triangle_creation_stores_attributes(self):
        """Triangle stores color and sides correctly."""
        t = Triangle("green", 3.0, 4.0, 5.0)
        assert t.color == "green"
        assert t.sides == (3.0, 4.0, 5.0)

    def test_triangle_invalid_side_zero_raises_error(self):
        """A side of zero raises ValueError."""
        with pytest.raises(ValueError):
            Triangle("green", 0.0, 4.0, 5.0)

    def test_triangle_invalid_side_negative_raises_error(self):
        """A negative side raises ValueError."""
        with pytest.raises(ValueError):
            Triangle("green", -1.0, 4.0, 5.0)

    def test_triangle_inequality_violation_raises_error(self):
        """Sides that violate the triangle inequality raise ValueError."""
        with pytest.raises(ValueError):
            Triangle("green", 1.0, 2.0, 10.0)

    def test_triangle_area_345_right_triangle(self):
        """3-4-5 right triangle has area = 6.0 (½ × base × height)."""
        t = Triangle("green", 3.0, 4.0, 5.0)
        assert t.area() == pytest.approx(6.0, rel=1e-6)

    def test_triangle_area_equilateral(self):
        """Equilateral triangle with side 2: area = √3."""
        t = Triangle("yellow", 2.0, 2.0, 2.0)
        assert t.area() == pytest.approx(math.sqrt(3), rel=1e-6)

    def test_triangle_perimeter(self):
        """Perimeter = sum of all three sides."""
        t = Triangle("green", 3.0, 4.0, 5.0)
        assert t.perimeter() == pytest.approx(12.0, rel=1e-6)

    def test_triangle_str_contains_expected_info(self):
        """__str__ includes class name and color."""
        t = Triangle("green", 3.0, 4.0, 5.0)
        s = str(t)
        assert "Triangle" in s
        assert "green" in s

    def test_triangle_describe_contains_color(self):
        """describe() output contains the color (inherited from Shape.describe)."""
        t = Triangle("green", 3.0, 4.0, 5.0)
        assert "green" in t.describe()

    def test_triangle_describe_contains_triangle_keyword(self):
        """describe() includes the word 'Triangle' (subclass extension)."""
        t = Triangle("green", 3.0, 4.0, 5.0)
        assert "Triangle" in t.describe()


# ---------------------------------------------------------------------------
# Inheritance and Polymorphism
# ---------------------------------------------------------------------------


class TestInheritance:
    """
    Test inheritance relationships and polymorphic behavior.

    These tests verify that subclasses truly IS-A Shape, that isinstance()
    works correctly, and that the same interface (area, perimeter, describe)
    works uniformly across all shape types.
    """

    def test_circle_is_instance_of_shape(self):
        """Circle IS-A Shape (inherits from Shape)."""
        assert isinstance(Circle("red", 5.0), Shape)

    def test_circle_is_instance_of_circle(self):
        """Circle IS-A Circle."""
        assert isinstance(Circle("red", 5.0), Circle)

    def test_rectangle_is_instance_of_shape(self):
        """Rectangle IS-A Shape."""
        assert isinstance(Rectangle("blue", 4.0, 6.0), Shape)

    def test_triangle_is_instance_of_shape(self):
        """Triangle IS-A Shape."""
        assert isinstance(Triangle("green", 3.0, 4.0, 5.0), Shape)

    def test_circle_is_not_rectangle(self):
        """Circle IS-NOT-A Rectangle."""
        assert not isinstance(Circle("red", 5.0), Rectangle)

    def test_rectangle_is_not_triangle(self):
        """Rectangle IS-NOT-A Triangle."""
        assert not isinstance(Rectangle("blue", 4.0, 6.0), Triangle)

    def test_polymorphism_area_works_for_all_shapes(self):
        """area() can be called uniformly on any Shape subclass."""
        shapes = [
            Circle("red", 5.0),
            Rectangle("blue", 4.0, 6.0),
            Triangle("green", 3.0, 4.0, 5.0),
        ]
        areas = [s.area() for s in shapes]
        assert len(areas) == 3
        assert all(a > 0 for a in areas)

    def test_polymorphism_perimeter_works_for_all_shapes(self):
        """perimeter() can be called uniformly on any Shape subclass."""
        shapes = [
            Circle("red", 5.0),
            Rectangle("blue", 4.0, 6.0),
            Triangle("green", 3.0, 4.0, 5.0),
        ]
        for shape in shapes:
            assert shape.perimeter() > 0

    def test_polymorphism_describe_works_for_all_shapes(self):
        """describe() can be called uniformly and always returns a string."""
        shapes = [
            Circle("red", 5.0),
            Rectangle("blue", 4.0, 6.0),
            Triangle("green", 3.0, 4.0, 5.0),
        ]
        for shape in shapes:
            result = shape.describe()
            assert isinstance(result, str)
            assert len(result) > 0

    def test_super_describe_called_in_circle(self):
        """Circle.describe() calls super().describe(): color appears in output."""
        c = Circle("red", 5.0)
        # The base Shape.describe() includes the color string
        assert "red" in c.describe()

    def test_super_describe_called_in_rectangle(self):
        """Rectangle.describe() calls super().describe(): color appears in output."""
        r = Rectangle("blue", 4.0, 6.0)
        assert "blue" in r.describe()

    def test_super_describe_called_in_triangle(self):
        """Triangle.describe() calls super().describe(): color appears in output."""
        t = Triangle("green", 3.0, 4.0, 5.0)
        assert "green" in t.describe()

    def test_color_property_inherited_by_all_subclasses(self):
        """The color property defined in Shape is accessible on all subclasses."""
        shapes = [
            Circle("red", 5.0),
            Rectangle("blue", 4.0, 6.0),
            Triangle("green", 3.0, 4.0, 5.0),
        ]
        expected = ["red", "blue", "green"]
        for shape, expected_color in zip(shapes, expected):
            assert shape.color == expected_color

    def test_color_setter_inherited_by_all_subclasses(self):
        """The color setter defined in Shape works on all subclasses."""
        shapes = [
            Circle("red", 5.0),
            Rectangle("blue", 4.0, 6.0),
            Triangle("green", 3.0, 4.0, 5.0),
        ]
        for shape in shapes:
            shape.color = "orange"
            assert shape.color == "orange"


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------


class TestCanvas:
    """Test the Canvas container class."""

    def setup_method(self):
        """Create a fresh canvas and shapes before each test."""
        Shape._total_shapes = 0
        self.canvas = Canvas("Test Canvas")
        self.circle = Circle("red", 5.0)
        self.rect = Rectangle("blue", 4.0, 6.0)
        self.tri = Triangle("green", 3.0, 4.0, 5.0)

    def test_canvas_creation_stores_name(self):
        """Canvas stores its name correctly."""
        canvas = Canvas("My Canvas")
        assert canvas.name == "My Canvas"

    def test_canvas_starts_empty(self):
        """A new canvas has no shapes."""
        canvas = Canvas("Empty Canvas")
        assert canvas.shape_count == 0

    def test_add_shape_increases_count(self):
        """Adding a shape increases shape_count by 1."""
        self.canvas.add_shape(self.circle)
        assert self.canvas.shape_count == 1

    def test_shape_count_property(self):
        """shape_count reflects the number of shapes added."""
        assert self.canvas.shape_count == 0
        self.canvas.add_shape(self.circle)
        assert self.canvas.shape_count == 1
        self.canvas.add_shape(self.rect)
        assert self.canvas.shape_count == 2

    def test_total_area_property_empty_canvas(self):
        """total_area is 0.0 for an empty canvas."""
        assert self.canvas.total_area == pytest.approx(0.0, abs=1e-9)

    def test_total_area_property_sums_all_shapes(self):
        """total_area equals the sum of all shape areas."""
        self.canvas.add_shape(self.circle)
        self.canvas.add_shape(self.rect)
        expected = self.circle.area() + self.rect.area()
        assert self.canvas.total_area == pytest.approx(expected, rel=1e-6)

    def test_find_by_color_returns_matching_shapes(self):
        """find_by_color returns shapes that match the given color."""
        self.canvas.add_shape(self.circle)
        self.canvas.add_shape(self.rect)
        self.canvas.add_shape(self.tri)

        red_shapes = self.canvas.find_by_color("red")
        assert len(red_shapes) == 1
        assert self.circle in red_shapes

    def test_find_by_color_is_case_insensitive(self):
        """find_by_color works regardless of case."""
        self.canvas.add_shape(self.circle)
        assert len(self.canvas.find_by_color("RED")) == 1
        assert len(self.canvas.find_by_color("Red")) == 1

    def test_find_by_color_returns_empty_list_when_not_found(self):
        """find_by_color returns [] when no shapes match."""
        self.canvas.add_shape(self.circle)
        assert self.canvas.find_by_color("yellow") == []

    def test_largest_shape_returns_shape_with_max_area(self):
        """largest_shape returns the shape with the greatest area."""
        self.canvas.add_shape(self.circle)  # area ≈ 78.54
        self.canvas.add_shape(self.rect)  # area = 24.0
        self.canvas.add_shape(self.tri)  # area = 6.0
        assert self.canvas.largest_shape() is self.circle

    def test_largest_shape_returns_none_when_empty(self):
        """largest_shape returns None on an empty canvas."""
        canvas = Canvas("Empty")
        assert canvas.largest_shape() is None

    def test_add_different_shape_types(self):
        """Canvas accepts all Shape subclasses (polymorphism)."""
        self.canvas.add_shape(self.circle)
        self.canvas.add_shape(self.rect)
        self.canvas.add_shape(self.tri)
        assert self.canvas.shape_count == 3

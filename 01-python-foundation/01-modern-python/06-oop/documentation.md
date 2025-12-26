# Chapter 6: Object-Oriented Programming

> _"OOP is not about objects. It's about organizing code so that change is cheap and safe."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Classes and instances
- The `__init__` method and `self`
- Instance vs. class attributes
- Methods: instance, class, static
- Inheritance and method resolution
- Dunder methods (magic methods)
- Properties and encapsulation
- Composition vs. inheritance

---

## Prerequisites

- Chapters 1-5: All previous content

---

## 1. Classes and Objects

### 1.1 Defining a Class

```python
class User:
    """A user in our system."""

    def __init__(self, name: str, email: str):
        """Initialize a user with name and email."""
        self.name = name
        self.email = email

    def greet(self) -> str:
        """Return a greeting."""
        return f"Hello, I'm {self.name}"

# Creating instances
alice = User("Alice", "alice@example.com")
bob = User("Bob", "bob@example.com")

print(alice.name)     # "Alice"
print(alice.greet())  # "Hello, I'm Alice"
```

### 1.2 Understanding `self`

`self` is the instance the method is called on.

```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self  # Return self for chaining

c = Counter()
c.increment().increment().increment()
print(c.count)  # 3
```

### 1.3 Instance vs. Class Attributes

```python
class User:
    # Class attribute (shared by all instances)
    default_role = "user"
    instance_count = 0

    def __init__(self, name: str):
        # Instance attribute (unique per instance)
        self.name = name
        User.instance_count += 1

# Class attributes
print(User.default_role)  # "user"

# Instance attributes
alice = User("Alice")
bob = User("Bob")
print(alice.name)  # "Alice"
print(bob.name)    # "Bob"

# Shared class attribute
print(User.instance_count)  # 2
```

#### ⚠️ Common Mistake: Mutable Class Attributes

```python
# WRONG — all instances share the same list!
class User:
    items = []  # Class attribute!

    def add_item(self, item):
        self.items.append(item)

a = User()
b = User()
a.add_item("apple")
print(b.items)  # ["apple"] — BUG! b sees a's item

# CORRECT — use instance attributes
class User:
    def __init__(self):
        self.items = []  # Instance attribute
```

---

## 2. Methods

### 2.1 Instance Methods

Regular methods that operate on instance data.

```python
class BankAccount:
    def __init__(self, balance: float = 0):
        self.balance = balance

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> bool:
        if amount > self.balance:
            return False
        self.balance -= amount
        return True
```

### 2.2 Class Methods

Operate on the class, not instances. Use `@classmethod`.

```python
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    @classmethod
    def from_string(cls, user_string: str) -> "User":
        """Alternative constructor from 'name:email' string."""
        name, email = user_string.split(":")
        return cls(name, email)

# Regular instantiation
alice = User("Alice", "alice@example.com")

# Alternative constructor
bob = User.from_string("Bob:bob@example.com")
```

### 2.3 Static Methods

Utility functions that don't need class or instance. Use `@staticmethod`.

```python
class MathUtils:
    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0

# Call without instantiation
MathUtils.add(3, 5)     # 8
MathUtils.is_even(4)    # True
```

---

## 3. Inheritance

### 3.1 Basic Inheritance

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "Some sound"

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says: Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} says: Meow!"

dog = Dog("Buddy")
cat = Cat("Whiskers")
print(dog.speak())  # "Buddy says: Woof!"
print(cat.speak())  # "Whiskers says: Meow!"
```

### 3.2 Using `super()`

Call parent class methods.

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)  # Call parent's __init__
        self.breed = breed

buddy = Dog("Buddy", "Golden Retriever")
print(buddy.name)   # "Buddy"
print(buddy.breed)  # "Golden Retriever"
```

### 3.3 Multiple Inheritance and MRO

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

d = D()
print(d.method())  # "B" — follows MRO

# View MRO
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

---

## 4. Dunder Methods (Magic Methods)

### 4.1 String Representation

```python
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"User(name={self.name!r}, age={self.age})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"{self.name} ({self.age} years old)"

user = User("Alice", 30)
print(repr(user))  # User(name='Alice', age=30)
print(str(user))   # Alice (30 years old)
print(user)        # Alice (30 years old) — uses __str__
```

### 4.2 Comparison Methods

```python
class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.price == other.price

    def __lt__(self, other: "Product") -> bool:
        return self.price < other.price

    def __le__(self, other: "Product") -> bool:
        return self.price <= other.price

a = Product("A", 10)
b = Product("B", 20)
print(a < b)   # True
print(a == b)  # False

# Sorting works!
products = [Product("C", 30), Product("A", 10), Product("B", 20)]
sorted_products = sorted(products)  # Sorted by price
```

### 4.3 Container Methods

```python
class Playlist:
    def __init__(self):
        self._songs = []

    def add(self, song: str):
        self._songs.append(song)

    def __len__(self) -> int:
        return len(self._songs)

    def __getitem__(self, index: int) -> str:
        return self._songs[index]

    def __contains__(self, song: str) -> bool:
        return song in self._songs

    def __iter__(self):
        return iter(self._songs)

playlist = Playlist()
playlist.add("Song A")
playlist.add("Song B")

print(len(playlist))       # 2
print(playlist[0])         # "Song A"
print("Song A" in playlist)  # True

for song in playlist:
    print(song)
```

### 4.4 Context Manager

```python
class FileHandler:
    def __init__(self, filename: str, mode: str = "r"):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions

with FileHandler("test.txt", "w") as f:
    f.write("Hello")
# File automatically closed
```

---

## 5. Properties and Encapsulation

### 5.1 Properties

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius  # Convention: _prefix = "private"

    @property
    def radius(self) -> float:
        """Get the radius."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        """Set the radius with validation."""
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self) -> float:
        """Computed property (read-only)."""
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.radius)    # 5
print(c.area)      # 78.54...

c.radius = 10      # Uses setter
# c.radius = -1    # Raises ValueError
# c.area = 100     # AttributeError (no setter)
```

### 5.2 Name Mangling

```python
class Account:
    def __init__(self, balance: float):
        self.__balance = balance  # "Private" via name mangling

    def get_balance(self) -> float:
        return self.__balance

acc = Account(100)
# print(acc.__balance)  # AttributeError
print(acc._Account__balance)  # 100 — still accessible, but discouraged
```

---

## 6. Composition vs. Inheritance

### 6.1 Prefer Composition

```python
# INHERITANCE — tight coupling
class EmailNotifier:
    def send(self, message: str):
        print(f"Email: {message}")

class OrderSystem(EmailNotifier):  # IS-A EmailNotifier?
    def place_order(self, item: str):
        # ... order logic
        self.send(f"Order placed: {item}")

# COMPOSITION — loose coupling (preferred)
class EmailNotifier:
    def send(self, message: str):
        print(f"Email: {message}")

class OrderSystem:
    def __init__(self, notifier: EmailNotifier):
        self.notifier = notifier  # HAS-A notifier

    def place_order(self, item: str):
        # ... order logic
        self.notifier.send(f"Order placed: {item}")

# Easier to test, swap implementations
notifier = EmailNotifier()
orders = OrderSystem(notifier)
```

### 6.2 When to Use Inheritance

Use inheritance when:

- True "is-a" relationship exists
- You need polymorphism
- Subclass is a specialization of parent

```python
# Good use of inheritance
class Shape:
    def area(self) -> float:
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

# Polymorphism
shapes: list[Shape] = [Circle(5), Rectangle(4, 3)]
for shape in shapes:
    print(shape.area())
```

---

## Quick Reference

### Class Structure

```python
class MyClass:
    class_attr = "shared"

    def __init__(self, x):
        self.instance_attr = x

    def instance_method(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass

    @property
    def computed(self):
        return self.instance_attr * 2
```

### Key Dunder Methods

```python
__init__    # Constructor
__repr__    # Developer string
__str__     # User string
__eq__      # Equality
__lt__      # Less than
__len__     # Length
__getitem__ # Indexing
__iter__    # Iteration
__enter__   # Context manager enter
__exit__    # Context manager exit
```

---

## Summary

You've learned:

1. **Classes and instances** — blueprints and objects
2. **Instance vs class attributes** — unique vs shared data
3. **Method types** — instance, class, static
4. **Inheritance** — code reuse and polymorphism
5. **Dunder methods** — Python's special protocols
6. **Properties** — controlled attribute access
7. **Composition** — prefer over inheritance

Next chapter: Type System — generics, protocols, and advanced typing.

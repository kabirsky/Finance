# Python for JS/C++ Developers

A quick reference guide comparing Python syntax to JavaScript and C++.

## The Big Differences

### 1. Indentation IS the syntax
```python
# Python - indentation defines blocks (usually 4 spaces)
if condition:
    do_something()
    do_more()
# Back to normal indentation = end of block

# NO braces {} like in JS/C++!
```

```javascript
// JavaScript equivalent
if (condition) {
    doSomething();
    doMore();
}
```

### 2. No semicolons needed
```python
x = 5        # No semicolon
y = 10       # Just newlines
```

### 3. `self` instead of `this`
```python
class Dog:
    def bark(self):           # self MUST be first parameter
        print(self.name)      # Use self.field, not this.field
```

```javascript
// JavaScript equivalent
class Dog {
    bark() {                  // 'this' is implicit
        console.log(this.name);
    }
}
```

---

## Variables & Types

### Declaration - no keywords needed!
```python
# Python - just assign
x = 5
name = "Alice"
items = [1, 2, 3]

# No const/let/var/int/string keywords
```

```javascript
// JavaScript
const x = 5;
let name = "Alice";
const items = [1, 2, 3];
```

```cpp
// C++
int x = 5;
std::string name = "Alice";
std::vector<int> items = {1, 2, 3};
```

### Type hints (optional, like TypeScript)
```python
# Python 3.8+ type hints - NOT enforced at runtime!
x: int = 5
name: str = "Alice"
items: list[int] = [1, 2, 3]

def greet(name: str) -> str:
    return f"Hello {name}"

# Type hints are just documentation - Python won't stop you from doing:
x: int = "oops"  # Runs fine! Use mypy for static checking
```

### Common types comparison
| Python | JavaScript | C++ |
|--------|------------|-----|
| `int` | `number` | `int`, `long` |
| `float` | `number` | `float`, `double` |
| `str` | `string` | `std::string` |
| `bool` | `boolean` | `bool` |
| `None` | `null`/`undefined` | `nullptr` |
| `True`/`False` | `true`/`false` | `true`/`false` |

---

## Strings

### f-strings (like template literals)
```python
name = "World"
age = 25

# f-string - note the 'f' prefix!
message = f"Hello {name}, you are {age} years old"

# Expression inside braces
result = f"2 + 2 = {2 + 2}"
```

```javascript
// JavaScript equivalent
const message = `Hello ${name}, you are ${age} years old`;
```

### String methods
```python
s = "hello world"
s.upper()          # "HELLO WORLD"
s.split(" ")       # ["hello", "world"]
s.replace("o", "0") # "hell0 w0rld"
s.strip()          # Remove whitespace from ends
"x" in s           # False (membership test)
```

---

## Data Structures

### List = Array
```python
# Python list
items = [1, 2, 3]
items.append(4)         # [1, 2, 3, 4]
items[0]                # 1
items[-1]               # 4 (last item - negative indexing!)
items[1:3]              # [2, 3] (slicing)
len(items)              # 4
```

```javascript
// JavaScript equivalent
const items = [1, 2, 3];
items.push(4);
items[0];               // 1
items.at(-1);           // 4
items.slice(1, 3);      // [2, 3]
items.length;           // 4
```

### Dict = Object/Map
```python
# Python dict
person = {
    "name": "Alice",
    "age": 30
}
person["name"]          # "Alice"
person.get("name")      # "Alice" (won't throw if missing)
person.get("x", "default")  # "default" if key missing
person["city"] = "NYC"  # Add new key

# Iterate
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(key, value)
```

```javascript
// JavaScript equivalent
const person = {
    name: "Alice",
    age: 30
};
person.name;            // or person["name"]
person.city = "NYC";

for (const [key, value] of Object.entries(person)) {
    console.log(key, value);
}
```

### Tuple = Immutable list
```python
# Tuple - can't be modified after creation
point = (10, 20)
x, y = point           # Unpacking! x=10, y=20

# Great for returning multiple values
def get_bounds():
    return (0, 100)    # Returns a tuple

min_val, max_val = get_bounds()  # Unpack the result
```

### Set = Unique values
```python
unique = {1, 2, 3, 2, 1}  # {1, 2, 3}
unique.add(4)
1 in unique               # True (fast lookup!)
```

---

## Functions

### Basic syntax
```python
def greet(name):
    return f"Hello {name}"

# With type hints
def greet(name: str) -> str:
    return f"Hello {name}"
```

```javascript
// JavaScript
function greet(name) {
    return `Hello ${name}`;
}
// or
const greet = (name) => `Hello ${name}`;
```

### Default arguments
```python
def greet(name, greeting="Hello"):
    return f"{greeting} {name}"

greet("Alice")              # "Hello Alice"
greet("Alice", "Hi")        # "Hi Alice"
greet(greeting="Hey", name="Bob")  # Named arguments!
```

### *args and **kwargs (rest/spread)
```python
def func(*args, **kwargs):
    # args = tuple of positional args
    # kwargs = dict of keyword args
    print(args)    # (1, 2, 3)
    print(kwargs)  # {"x": 10, "y": 20}

func(1, 2, 3, x=10, y=20)
```

```javascript
// JavaScript equivalent
function func(...args) {      // Rest parameters
    console.log(args);
}
func(1, 2, 3);

// Spread
const arr = [1, 2, 3];
func(...arr);                 // Spread into arguments
```

### Lambda (arrow functions)
```python
# Python lambda - single expression only
double = lambda x: x * 2
add = lambda x, y: x + y

# Used often with sort, filter, map
items.sort(key=lambda x: x.name)
```

```javascript
// JavaScript arrow functions - can have bodies
const double = x => x * 2;
const add = (x, y) => x + y;
items.sort((a, b) => a.name.localeCompare(b.name));
```

---

## List Comprehensions (Python's superpower!)

### Basic - like .map()
```python
# Python - list comprehension
numbers = [1, 2, 3, 4, 5]
doubled = [n * 2 for n in numbers]
# [2, 4, 6, 8, 10]
```

```javascript
// JavaScript equivalent
const doubled = numbers.map(n => n * 2);
```

### With filter
```python
# Python - filter in comprehension
evens = [n for n in numbers if n % 2 == 0]
# [2, 4]
```

```javascript
// JavaScript
const evens = numbers.filter(n => n % 2 === 0);
```

### Transform + filter
```python
# Python - both at once
doubled_evens = [n * 2 for n in numbers if n % 2 == 0]
# [4, 8]
```

```javascript
// JavaScript - need to chain
const doubledEvens = numbers
    .filter(n => n % 2 === 0)
    .map(n => n * 2);
```

### Dict comprehension
```python
# Create dict from list
names = ["alice", "bob"]
name_lengths = {name: len(name) for name in names}
# {"alice": 5, "bob": 3}
```

---

## Classes

### Basic class
```python
class Dog:
    # Class variable (shared by all instances)
    species = "Canis familiaris"

    # Constructor - note the double underscores!
    def __init__(self, name, age):
        # Instance variables
        self.name = name      # self.x = assign to instance
        self.age = age

    # Instance method - self is always first param
    def bark(self):
        print(f"{self.name} says woof!")

    # String representation (like toString())
    def __str__(self):
        return f"Dog({self.name})"

# Create instance - no 'new' keyword!
dog = Dog("Rex", 3)
dog.bark()
```

```javascript
// JavaScript equivalent
class Dog {
    static species = "Canis familiaris";

    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    bark() {
        console.log(`${this.name} says woof!`);
    }

    toString() {
        return `Dog(${this.name})`;
    }
}

const dog = new Dog("Rex", 3);
```

### Inheritance
```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):                    # Inherit from Animal
    def __init__(self, name, breed):
        super().__init__(name)        # Call parent constructor
        self.breed = breed
```

### @property (getters/setters)
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius         # Convention: _ = "private"

    @property
    def radius(self):                 # Getter
        return self._radius

    @radius.setter
    def radius(self, value):          # Setter
        if value < 0:
            raise ValueError("Radius can't be negative")
        self._radius = value

    @property
    def area(self):                   # Computed property
        return 3.14159 * self._radius ** 2

c = Circle(5)
print(c.radius)     # Calls getter: 5
c.radius = 10       # Calls setter
print(c.area)       # Computed: 314.159
```

### @dataclass (like TypeScript interfaces!)
```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    city: str = "Unknown"    # Default value

# Automatically generates:
# - __init__(self, name, age, city="Unknown")
# - __repr__ for printing
# - __eq__ for comparison
# - And more!

p = Person("Alice", 30)
print(p)  # Person(name='Alice', age=30, city='Unknown')
```

---

## Error Handling

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero!")
except Exception as e:          # Catch-all
    print(f"Error: {e}")
finally:
    print("This always runs")

# Raise exception (like throw)
raise ValueError("Something went wrong")
```

```javascript
// JavaScript equivalent
try {
    const result = 10 / 0;
} catch (e) {
    console.log(`Error: ${e.message}`);
} finally {
    console.log("This always runs");
}

throw new Error("Something went wrong");
```

---

## Context Managers (the `with` statement)

```python
# Python's "with" - automatic resource cleanup
# Like RAII in C++, or try-finally in JS

# File handling
with open("file.txt", "r") as f:
    content = f.read()
# File is automatically closed here, even if exception occurs!

# Without "with" - you'd need:
f = open("file.txt", "r")
try:
    content = f.read()
finally:
    f.close()
```

```javascript
// JavaScript has no direct equivalent
// You'd typically use try-finally or callbacks
const fs = require('fs');
const content = fs.readFileSync('file.txt', 'utf8');
// Or with streams, handle 'close' event
```

---

## Imports and Modules

### Import styles
```python
# Import entire module
import json
data = json.loads('{"x": 1}')

# Import specific items
from json import loads, dumps
data = loads('{"x": 1}')

# Import with alias
import numpy as np
from collections import defaultdict as dd

# Import all (avoid this!)
from json import *
```

```javascript
// JavaScript equivalent
import * as json from 'json';
import { loads, dumps } from 'json';
import json as j from 'json';
```

### The `if __name__ == "__main__":` pattern
```python
# my_module.py

def useful_function():
    return "I'm useful!"

# This code only runs when file is executed directly,
# NOT when imported as a module
if __name__ == "__main__":
    print("Running as script!")
    print(useful_function())
```

This is Python's way of having a "main" function. When you run `python my_module.py`,
`__name__` is set to `"__main__"`. When you `import my_module`, `__name__` is `"my_module"`.

---

## Common Gotchas for JS/C++ Devs

### 1. Indentation errors are real errors
```python
if True:
print("This will fail!")  # IndentationError!
```

### 2. No increment operators
```python
x++    # SyntaxError!
x += 1 # Use this instead
```

### 3. Boolean operators are words
```python
# Python          # JS/C++
and               # &&
or                # ||
not               # !

if x > 0 and y > 0:
    pass
```

### 4. == vs is
```python
# == compares values
# is compares identity (same object in memory)

a = [1, 2, 3]
b = [1, 2, 3]
a == b    # True (same values)
a is b    # False (different objects)

# Use 'is' for None checks
if x is None:
    pass
```

### 5. Mutable default arguments trap!
```python
# WRONG - the list is shared between calls!
def add_item(item, items=[]):
    items.append(item)
    return items

# RIGHT - use None as default
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 6. No switch statement (until Python 3.10)
```python
# Python < 3.10: use if/elif
if x == 1:
    pass
elif x == 2:
    pass
else:
    pass

# Python 3.10+: match statement
match x:
    case 1:
        pass
    case 2:
        pass
    case _:   # default
        pass
```

---

## Quick Reference

| Concept | Python | JavaScript | C++ |
|---------|--------|------------|-----|
| Print | `print(x)` | `console.log(x)` | `std::cout << x` |
| String length | `len(s)` | `s.length` | `s.length()` |
| Array/List length | `len(arr)` | `arr.length` | `arr.size()` |
| Check if in | `x in arr` | `arr.includes(x)` | `std::find(...)` |
| For loop | `for x in arr:` | `for (x of arr)` | `for (auto x : arr)` |
| Range loop | `for i in range(10):` | `for (let i=0; i<10; i++)` | `for (int i=0; i<10; i++)` |
| Null check | `x is None` | `x === null` | `x == nullptr` |
| Type check | `isinstance(x, int)` | `typeof x === 'number'` | N/A (static) |
| String format | `f"{x}"` | `` `${x}` `` | `std::format("{}", x)` |

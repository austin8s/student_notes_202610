# ACIT 2515

## Week 01

### Presentation

1. [Class Introduction](notes/001_intro.md)

### Notes

1. [Python Basics Review](notes/010_basics_review.md)
2. [How to Write Beautiful Code with PEP8](https://realpython.com/python-pep8)
3. [Google Python Style Guide: Comments and Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
4. [Basic Code Layout: Flat Project Layout](notes/012_flat_project_layout.md)
5. Configure VSCode Python Debugging and creating `.vscode/launch.json`
   1. [Python debugging in VS Code](https://code.visualstudio.com/docs/python/debugging)
   1. [Debugging With Arguments](how_to/debug_with_arguments.md)

### Demo

The following demonstrate key concepts required to complete this weeks exercises
and labs

1. [Argparse Demo](demos/argparse/argparse_demo.py)
1. [File Reading Intro](demos/file_intro/file_reading_demo.py)

### Exercises

1. [Setup Python 3.14](how_to/install_python_314_windows.md)
1. [Turn Off Copilot Autocomplete](https://code.visualstudio.com/docs/copilot/ai-powered-suggestions#_enable-or-disable-code-completions)
1. [WK01EX01 Character and Letter Frequencies](/exercises/wk01_ex01_character_frequency.md)

### Lab

1. [WK01EX02 Contacts File Reading](/exercises/wk01_ex02_contacts.md)
1. [WK01EX02 Data](/excercises/wk01_ex02_contacts_data/)

## References

1. [Python Howto: Argparse Tutorial](https://docs.python.org/3/howto/argparse.html)
1. [Building CLI Interfaces with Argparse](https://realpython.com/command-line-interfaces-python-argparse/)

## Week 02

### Flipped

1. Read:
   [Problem Solving and Decomposition](https://learning.oreilly.com/library/view/computational-thinking/9781780173641/html/15_Ch03.xhtml)

1. Review: Type annotations
   1. [Type Hints and Documentation](https://learning.oreilly.com/library/view/introducing-python-3rd/9781098174392/ch14.html)
   1. [Basic Typing Python](https://learning.oreilly.com/videos/practical-typing-in/0636920961307/0636920961307-video360000/)
   1. [Annotating Functions](https://learning.oreilly.com/videos/practical-typing-in/0636920961307/0636920961307-video360008/)

1. Review:
   [Defining Your Own Python Functions](https://realpython.com/defining-your-own-python-function/)

## Week 02

### Modules and Packages

1. [Demo: Modules, Packages, Notes](/demos/modules_packages)
1. [Notes: Modules, Packages, Imports](/notes/020_modules_packages_imports.md)

### Recursion

1. [Demo: Recursion Intro](/demos/recursion_intro)
1. [Exercise: Recursive Traceroute](/exercises/wk02_ex01_traceroute/instructions.md)
1. [Lab: Recursion - Task Flattener](/labs/wk02_lab01_recursion/README.md)

### References

#### Packages and Modules

1. [Python Tutorial: Modules and Packages](https://docs.python.org/3/tutorial/modules.html)
1. [Project Structure and Imports](https://learning.oreilly.com/library/view/dead-simple-python/9781098156671/c04.xhtml)

#### Recursion

1. [Recursive Functions (Learning Python)](https://learning.oreilly.com/library/view/learning-python-6th/9781098171292/ch19.html#recursive_functions)

### Flipped

1. [Virtual Environments: Background](/notes/030_venv_background.md)
2. [Virtual Environments: Operations](/notes/031_venv_operations.md)
3. [Managing Python Projects With uv: An All-in-One Solution](https://realpython.com/python-uv/)

## Week 03

### Argument Unpacking

1. [Notes: Argument Unpacking: Args, Kwargs, \*, \*\*](/notes/032_argument_unpacking_args_kwargs.md)
1. [Exercise: Unpacking by Position](/exercises/wk03_ex01_unpacking_py_position_args.md)
1. [Exercise: Unpacking with Keywords](/exercises/wk03_ex02_unpacking_w_keywords_kwargs.md)

### Decorators

1. [Demo: decorators](/demos/decorators/decorators.py)
1. [Notes: Higher Order Functions, Closures, and Decorators](/notes/033_higher_order_functions_decorators.md)
1. [Exercise: `call_count` decorator](/exercises/wk03_ex03_call_count_decorator.md)
1. [Exercise: Scopes, Closures, and Decorators](exercises/wk03_ex04_scopes_w_decorators/scopes_w_decorators_exploration.md)

### Virtual Environments and `uv`

1. [Excercise: Rest-Client Implementation](/exercises/wk03_ex05_rest_client/exploration_activity.md)
   1. [Rest-Client README](/exercises/wk03_ex05_rest_client/README.md)
1. [Lab: `process_snapshot`](/labs/wk03_lab01_process_snapshot/)

### References

1. [`nonlocal`](https://realpython.com/ref/keywords/nonlocal/)
1. [Closures](https://realpython.com/python-closure/)
1. [Decorators](https://realpython.com/primer-on-python-decorators)
1. [VSCode Environments](https://code.visualstudio.com/docs/python/environments)

### Flipped

1. [Testing with Pytest](https://learning.oreilly.com/videos/python-testing-for/27675040VIDEOPAIML/27675040VIDEOPAIML-c1_s4/)
2. [Using Asserts Pytest](https://learning.oreilly.com/videos/python-testing-for/27675040VIDEOPAIML/27675040VIDEOPAIML-c2_s2/)

## Week 04

### Testing and `pytest`

1. [`pytest` Introduction](notes/040_pytest.md)
1. [Exercise: Introduction to `pytest`](exercises/wk04_ex01_intro_pytest.md)
1. [`pytest` Fixtures](notes/041_pytest_fixtures.md)
1. [Lab: `pytest` Fixtures](labs/wk04_lab01_pytest_fixtures/intro_pytest_fixtures.md)
   1. Set C Submissions: https://classroom.github.com/a/vM4w7g-P
   1. Set B Submissions: https://classroom.github.com/a/O5GHbXUg

### References

1. [Getting Started with Pytest](https://learning.oreilly.com/library/view/python-testing-with/9781680509427/f_0013.xhtml#ch.getting_started)]
2. [Writing Test Functions](https://learning.oreilly.com/library/view/python-testing-with/9781680509427/f_0019.xhtml#ch.test_functions)
3. [Pytest Fixtures](https://learning.oreilly.com/library/view/python-testing-with/9781680509427/f_0032.xhtml#ch.fixtures)
4. [Pytest Builtin-Fixtures](https://learning.oreilly.com/library/view/python-testing-with/9781680509427/f_0047.xhtml#ch.builtin_fixtures)

### Flipped

1. [Python Exceptions: An Introduction](https://realpython.com/python-exceptions/)
1. [Python `with` Statement](https://realpython.com/python-with-statement/) - up
   to Summarizing with statements advantages.

## Week 06

### Reading and Writing Structured Files

1. [Working with JSON Data](https://realpython.com/python-json/)
1. [Reading and Writing CSV Files](https://realpython.com/python-csv/)

### Exceptions

#### Demo

1. [`exceptions_intro.py`](./demos/exceptions/exceptions_intro.py)
1. [`basic_exceptions.py`](./demos/exceptions/basic_exceptions.py)
1. [`checkin.py`](./demos/exceptions/checkin.py) Simple App With Exception
   Handling

#### Lab

1. Week 06 Lab 01 - Exceptions and Structured Data
   1. Set A: https://classroom.github.com/a/G21567OP
   1. Set B: https://classroom.github.com/a/xjMybz08
   1. Set C: https://classroom.github.com/a/pwking59

#### References

1. [Builtin Exceptions](https://docs.python.org/3/library/exceptions.html)

### Flipped

#### OO Introduction and Review: Video

1. [OOP Concepts](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video1_2/)
1. [Creating Object Attributes](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video1_3/)
1. [Creating Object Methods](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video1_4/)
1. [Printing Objects](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video1_5/)
1. [Inheritance and Abstraction](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video2_1/)
1. [Class vs Object Attributes](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video3_1/)
1. [Class Methods](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video3_2/)
1. [Encapsulation: Public and Private Visibility](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video4_1/)
1. [Encapsulation: Getters and Setters](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video4_2/)
1. [Encapsulation: Methods as Attributes](https://learning.oreilly.com/videos/python-object-oriented/9781837638765/9781837638765-video4_3/)

## Week 07

Review

## Week 08

Mid-term

## Week 09

### Object Orientation

### Notes

1. [Object Oriented Python](./notes/090_oop_python_intro.md)
1. [Documenting Classes: UML](./notes/091_uml.md)

### Exercises

1. [WK09EX01 Introduction to Object Orientation](./exercises/wk09_ex01_oo_intro/intro_oo.md)
1. [WK09EX02 Object Oriented Programming: Blackjack](./exercises/wk09_ex02_blackjack/README.md)

### Lab

1. wk09lab01: Network Host:
   1. [ Set A wk09lab01](https://classroom.github.com/a/KM6dGwEJ)
   1. [ Set B wk09lab01](https://classroom.github.com/a/A_f4Omlq)
   1. [ Set C wk09lab01](https://classroom.github.com/a/zwk1pSKn)

### Flipped

1. [Iheritence and Composition: A Python OOP Guide](https://realpython.com/inheritance-composition-python/)
1. [Pytest Fixtures: Monkeypatch](https://learning.oreilly.com/library/view/python-testing-with/9781680509427/f_0047.xhtml#ch.builtin_fixtures)

## Week 10

### Inheritance, ABC

#### Notes

1. [Inheritence, Abstract Base Classes](./notes/100_oo_inheritence_abc.md)

##### Exercise

1. [wk10_ex01_shapes](/exercises/wk10_ex01_shapes/README.md)
1. [wk10_ex02: Warlord's Siege](/exercises/wk10_ex02_fantasy_game.md)

##### Lab

1. [wk10_lab01 Warlords Siege](/labs/wk10_lab01_warlords_siege.md)

   Starter and Submissions Repos:
   1. Set A: https://classroom.github.com/a/GXYPf8Q7
   1. Set B: https://classroom.github.com/a/zdYHanJY
   1. Set C: https://classroom.github.com/a/Ih8N1nWz

## Week 11

Reading Week

## Week 12

### Demonstration Flask App

The following is a demo of a Flask app that you can reference throughout the
remainder of the course:

[Flask ORM API Demo](/demos/flask_orm_api_demo/)

### HTTP and WSGI

#### Notes

1. [HTTP Review](/notes/110_http_review.md)
1. [WSGI](/notes/111_wsgi_overview.md)

#### Exercises

1. [wk11_ex01: Bruno, REST API's](/exercises/wk11_ex01_bruno_rest_api/bruno_rest_api_exercise.md)

### Flask

#### Notes

1. [Flask Introduction](/notes/112_flask_intro.md)

### Exercises

1. [wk11_ex02: Flask Introduction](/exercises/wk11_ex02_intro_flask_exercise.md)

## Week 13

### HTTP Clients

#### Notes

1. [HTTP Python Clients using HTTPX](/notes/120_httpx_python_http_clients.md)

#### Exercise

1. [wk12_ex01_simple_http_client](/exercises/wk12_ex01_simple_http_client/simple_http_client_exercise.md)

### ORM

#### Demo

1. [Simple ORM Demo: Flask and Peewee](/demos/simple_orm_demo/README.md)

#### Notes

1. [Flask ORM](/notes/121_flask_orm.md)
1. [Flask Application Lifecycle and Contexts](/notes/122_flask_application_lifecycle_contexts.md)

#### Exercises

1. [wk12_ex02_simple_orm](/exercises/wk12_ex02_simple_orm_exercise.md)


## Week 14

### GUI's and Text User Interfaces

#### Demo

1. [Basic TUI with Textualize](demos/tui_demo_inventory_app/)
1. [TUI Monitor](demos/tui_monitor/)

#### Notes

1.[GUI's and Textual Library](/notes/130_gui_textual.md)

## Project

This is the project that you will be working on for the duration of the course.

1. [Project: Server Fleet Monitor Overview](/project/project_server_fleet_monitor_overview.md)
1. [Project: Part 1 - Server Fleet Monitor Agent](/project/project_server_fleet_monitor_agent.md)
1. [Project: Part 2 - Server Fleet Poller and Aggregator ](/project/project_server_fleet_monitor_poller_aggregator.md)
   1. [Project: Part 2 Supplied Code](/project/fleet_monitor_aggregator_starter/)
1. [Project: Part 3 - Server Fleet Dashboard](project/project_server_fleet_monitor_dashboard.md)

### Per Set Project Part 1 Repositories

1. Set A: https://classroom.github.com/a/5oRNAnDv
1. Set B: https://classroom.github.com/a/1WY4wnJL
1. Set C: [https://classroom.github.com/a/hC37POJ_](https://classroom.github.com/a/hC37POJ_)

### Per Set Project Part 1 Repositories
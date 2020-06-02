`pybotx` has a dependency injection mechanism heavily inspired by [`FastAPI`](https://fastapi.tiangolo.com/tutorial/dependencies/).

## Usage

First, create a function that will execute some logic. It can be a coroutine or a simple function.
Then write a handler for bot that will use this dependency:

```python3
{!./src/development/dependencies_injection/dependencies_injection0.py!}
```

## Dependencies with dependencies

Each of your dependencies function can contain parameters with other dependencies. And all this will be solved at the runtime:

```python3
{!./src/development/dependencies_injection/dependencies_injection1.py!}
```

## Special dependencies: Bot and Message

[Bot][botx.bots.bots.Bot] and `Message` objects and special case of dependencies. 
If you put an annotation for them into your function then this objects will be passed inside. 
It can be useful if you write something like authentication dependency:

```python3
{!./src/development/dependencies_injection/dependencies_injection2.py!}
```

[DependencyFailure][botx.exceptions.DependencyFailure] exception is used for preventing execution
of dependencies after one that failed.

Also, if you define a list of dependencies objects in the initialization of [collector][botx.collecting.collectors.collector.Collector] or [bot][botx.bots.bots.Bot] or in `.handler` decorator or others,
then these dependencies will be processed as background dependencies. 
They will be executed before the handler and its' dependencies:
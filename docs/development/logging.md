`pybotx` uses `loguru` internally to log things. 

To enable it, just import `logger` from `loguru` and call `logger.enable("botx")`:

```Python3
{!./src/development/logging/logging0.py!}
```
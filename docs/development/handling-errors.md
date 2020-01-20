`pybotx` provides a mechanism for registering a handler for exceptions that may occur in your command handlers. 
By default, these errors are simply logged to the console, but you can register different behavior and perform some actions.
For example, you can handle database disconnection or another runtime errors. You can also use this mechanism to 
register the handler for an `Excpetion` error and send info about it to the Sentry with additional information.

## Usage Example

```python3
{!./src/development/handling_errors/handling_errors0.py!}
```
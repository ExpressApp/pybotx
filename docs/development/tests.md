You can test the behaviour of your bot by writing unit tests. Since the main goal of the bot is to process commands and send 
results to the BotX API, you should be able to intercept the result between sending data to the API. You can do this by using [TestClient][botx.testing.TestClient]. 
Then you write some mocks and test your logic inside tests. In this example we will `pytest` for unit tests.

## Example

### Bot

Suppose we have a bot that returns a message in the format `"Hello, {username}"` with the command `/hello`:

`bot.py`:
```python3
{!./src/development/tests/tests0/bot.py!}
```

### Fixtures

Now let's write some fixtures to use them in our tests:

`conftest.py`: 
```python3
{!./src/development/tests/tests0/conftest.py!}
```

### Tests

Now we have fixtures for writing tests. Let's write a test to verify that the message body is in the required format:

`test_format_command.py`
```python3
{!./src/development/tests/tests0/test_format_command.py!}
```
### Single process

The main note about deploying bots from `pybotx` is that if you are using `next step handlers`, you must run your web application 
in a single process mode.

### Using `gunicorn`

If you are using `gunicorn`, then you must use the `gthread worker` class to simultaneously serve several requests:

```bash
gunicorn --workers=1 --threads=4 application:app 
```

### Using `uvicorn`

If you have an `ASGI` application, then most likely it is asynchronous, 
so you can safely load it using a single thread without significant loss in performance.

```bash
uvicorn app:app
```
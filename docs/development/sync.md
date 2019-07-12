By default, `pybotx` provides asynchronous methods through the `Bot` class, since this is more efficient. 
But as an alternative, you can import the `Bot` from the `botx.sync` module and use all the methods as normal blockable
functions. Handlers will then be dispatched using the `concurrent.futures.threads.ThreadPoolExecutor` object.
#!/usr/bin/env python3
"""
Test to verify that callbacks work correctly across different threads/event loops.
"""
import asyncio
import threading
import time
from uuid import uuid4

import pytest

from pybotx.bot.callbacks.callback_manager import CallbackManager
from pybotx.bot.callbacks.callback_memory_repo import CallbackMemoryRepo
from pybotx.models.method_callbacks import BotAPIMethodSuccessfulCallback


@pytest.mark.asyncio
async def test_cross_thread_callback_handling():
    """Test that callbacks work correctly when created in one thread and resolved in another."""
    
    # Create callback repository and manager
    callback_repo = CallbackMemoryRepo()
    callback_manager = CallbackManager(callback_repo)
    
    # Set up the main event loop
    main_loop = asyncio.get_running_loop()
    callback_manager.set_main_loop(main_loop)
    callback_repo.set_main_loop(main_loop)
    
    sync_id = uuid4()
    callback_result = None
    callback_error = None
    
    # Function to create callback and wait for it in a different thread
    def create_and_wait_callback():
        nonlocal callback_result, callback_error
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def callback_task():
            try:
                # Create callback in different thread
                await callback_manager.create_botx_method_callback(sync_id)
                
                # Wait for callback with short timeout
                result = await callback_manager.wait_botx_method_callback(sync_id, 2.0)
                return result
            except Exception as e:
                raise e
        
        try:
            result = loop.run_until_complete(callback_task())
            callback_result = result
        except Exception as e:
            callback_error = e
        finally:
            loop.close()
    
    # Start the thread that creates and waits for callback
    thread = threading.Thread(target=create_and_wait_callback)
    thread.start()
    
    # Give the thread time to create the callback
    await asyncio.sleep(0.1)
    
    # Set the callback result from the main thread
    test_callback = BotAPIMethodSuccessfulCallback(
        sync_id=sync_id,
        status="ok",
        result={"message": "success"}
    )
    
    await callback_manager.set_botx_method_callback_result(test_callback)
    
    # Wait for the thread to complete
    thread.join(timeout=5.0)
    
    # Verify the callback was received successfully
    assert callback_error is None, f"Callback failed with error: {callback_error}"
    assert callback_result is not None, "Callback result should not be None"
    assert callback_result.sync_id == sync_id
    assert callback_result.status == "ok"
    assert callback_result.result == {"message": "success"}


@pytest.mark.asyncio
async def test_same_thread_callback_handling():
    """Test that callbacks still work correctly in the same thread (regression test)."""
    
    # Create callback repository and manager
    callback_repo = CallbackMemoryRepo()
    callback_manager = CallbackManager(callback_repo)
    
    # Set up the main event loop
    main_loop = asyncio.get_running_loop()
    callback_manager.set_main_loop(main_loop)
    callback_repo.set_main_loop(main_loop)
    
    sync_id = uuid4()
    
    # Create callback in same thread
    await callback_manager.create_botx_method_callback(sync_id)
    
    # Set the callback result
    test_callback = BotAPIMethodSuccessfulCallback(
        sync_id=sync_id,
        status="ok",
        result={"message": "success"}
    )
    
    # Set result and wait for callback concurrently
    async def set_result():
        await asyncio.sleep(0.1)  # Small delay
        await callback_manager.set_botx_method_callback_result(test_callback)
    
    # Start setting result in background
    asyncio.create_task(set_result())
    
    # Wait for callback
    result = await callback_manager.wait_botx_method_callback(sync_id, 2.0)
    
    # Verify the callback was received successfully
    assert result.sync_id == sync_id
    assert result.status == "ok"
    assert result.result == {"message": "success"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
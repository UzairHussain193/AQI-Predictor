"""Retry decorator with exponential backoff"""
import time
import functools
from src.config import Config


def exponential_backoff(max_retries=None, initial_delay=None, backoff_factor=None):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay between retries
    """
    max_retries = max_retries or Config.MAX_RETRIES
    initial_delay = initial_delay or Config.RETRY_DELAY
    backoff_factor = backoff_factor or Config.RETRY_BACKOFF
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
                    delay *= backoff_factor
            
        return wrapper
    return decorator

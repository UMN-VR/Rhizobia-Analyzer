import os
import psutil

def log_memory_usage(logger):
    # Get the process
    process = psutil.Process(os.getpid())

    # Get the memory info
    mem_info = process.memory_info()

    # Log the memory usage
    logger.info(f'Current memory usage: {mem_info.rss / (1024 * 1024)} MB')

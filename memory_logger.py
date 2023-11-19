import os
import psutil

def log_memory_usage(logger):
    # Get the process
    process = psutil.Process(os.getpid())

    # Get the memory info
    mem_info = process.memory_info()

    mem = mem_info.rss / (1024 * 1024)

    msg = f'Current memory usage: {mem} MB\n'

    # Log the memory usage
    logger.info(msg)

    # Print the memory usage

    print(msg)
    

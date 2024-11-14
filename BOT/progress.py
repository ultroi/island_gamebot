# progress.py

def example_function():
    filled_length = 0  # Initialize the variable
    total_length = 100

    # Use the variable
    filled_length = total_length // 2
    print(f"Filled length: {filled_length}")

example_function()

# Example of a progress bar implementation
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()

# Example usage
import time

# A List of Items
items = list(range(0, 57))
l = len(items)

# Initial call to print 0% progress
print_progress_bar(0, l, prefix='Progress:', suffix='Complete', length=50)
for i, item in enumerate(items):
    # Do stuff...
    time.sleep(0.1)
    # Update Progress Bar
    print_progress_bar(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
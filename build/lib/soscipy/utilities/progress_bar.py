import sys


def update_progress(progress):
    """
    Update_progress() : Displays or updates a console progress bar
    Accepts a float between 0 and 1. Any int will be converted to a float.
    A value under 0 represents a 'halt'.
    A value at 1 or bigger represents 100%
    :param progress: Float as input
    :return: A standard output to display a progress bar
    """
    barLength = 10  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength * progress))
    text = f"\rPercent Completion: [{'#' * block + '-' * (barLength - block)}] {progress * 100:.2f}% {status}"
    sys.stdout.write(text)
    sys.stdout.flush()
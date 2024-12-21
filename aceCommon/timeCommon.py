from datetime import datetime

def create_time_stamp(output_format="%Y%m%d%H%M%S"):
    """
    Generates a timestamp in the specified format.

    Args:
        output_format (str): The desired timestamp format. Defaults to "%Y%m%d%H%M%S".

    Returns:
        str: The current time formatted as per the provided format.

    Example:
        create_time_stamp("%Y-%m-%d %H:%M:%S")
        # Output: "2024-12-21 14:35:42"
    """
    return datetime.now().strftime(output_format)
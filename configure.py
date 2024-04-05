from configparser import ConfigParser

def config(filename="database.ini", section="postgresql"):
    """
    Read database configuration from an INI file.

    Args:
        filename (str): The name of the INI file to read from.
        section (str): The section in the INI file containing the database configuration.

    Returns:
        dict: A dictionary containing the database configuration parameters.

    Raises:
        Exception: If the specified section is not found in the INI file.
    """
    # Create a ConfigParser object
    parser = ConfigParser()

    # Read the specified INI file
    parser.read(filename)

    # Initialize an empty dictionary to store database configuration parameters
    db = {}

    # Check if the specified section exists in the INI file
    if parser.has_section(section):

        # If the section exists, retrieve all parameters in the section
        params = parser.items(section)

        # Iterate over the parameters and populate the dictionary
        for param in params:
            db[param[0]] = param[1]
    else:
        # If the specified section is not found, raise an exception
        raise Exception(f"Section '{section}' not found in the '{filename}' file.")
    
    # print(db)
    return db



# config()



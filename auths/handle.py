import os
def get_db_uri():
    """
    Returns a list containing the database credentials, with "localhost" at index 0.
    """
    with open('creds', 'r') as file:
        content = file.read().strip()
    credentials = content.split(",")
    return credentials
db_credentials = get_db_uri()  # Output: ['localhost', 'portfolio', 'portfolio']

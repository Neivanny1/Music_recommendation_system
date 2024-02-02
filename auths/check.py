from handle import get_db_uri
db_credentials = get_db_uri()
print(db_credentials[2])  # Output: ['localhost', 'portfolio', 'portfolio']

import re

def tokenize(query):
    # Add spaces around special characters
    query = re.sub(r'([(),;])', r' \1 ', query)

    # Remove multiple spaces
    query = re.sub(r'\s+', ' ', query)

    return query.strip().split()
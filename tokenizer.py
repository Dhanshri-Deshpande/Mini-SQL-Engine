def tokenize(query):
    return query.strip().replace("(", " ( ").replace(")", " ) ").split()

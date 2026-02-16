import os
import json

STORAGE = "storage/"
def load_schema_from_csv(table):
    file_path = STORAGE + f"{table}.csv"

    if not os.path.exists(file_path):
        return None

    import csv
    with open(file_path, "r") as f:
        reader = list(csv.reader(f))

    header = reader[0]

    schema = {
        table: {
            "columns": header,
            "types": {},
            "primary": None,
            "indexed": []
        }
    }

    schema_path = STORAGE + "schema.json"

    with open(schema_path, "w") as f:
        json.dump(schema, f, indent=4)

    return schema






if not os.path.exists(STORAGE):
    os.makedirs(STORAGE)


def create_table(table, columns):
    schema_path = STORAGE + "schema.json"

    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            schema = json.load(f)
    else:
        schema = {}

    col_names = []
    primary = None
    indexed = []
    types_dict = {}   # ✅ define once

    for col in columns:
        parts = col.split()
        col_def = parts[0]
        name, datatype = col_def.split(":")

        col_names.append(name)
        types_dict[name] = datatype

        if "PRIMARY" in col:
            primary = name
        if "INDEX" in col:
            indexed.append(name)

    schema[table] = {
        "columns": col_names,
        "types": types_dict,
        "primary": primary,
        "indexed": indexed
    }

    with open(schema_path, "w") as f:
        json.dump(schema, f, indent=4)

    with open(STORAGE + f"{table}.csv", "w") as f:
        f.write(",".join(col_names) + "\n")

    print("Table Created Successfully")

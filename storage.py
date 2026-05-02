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
    types_dict = {}

    unique_cols = []
    not_null_cols = []
    foreign_keys = {}
    check_constraints = {}
    len_constraints = {}
    positive_cols = []

    for col in columns:

        parts = col.split()
        col_def = parts[0]

        name, datatype = col_def.split(":")

        col_names.append(name)

        types_dict[name] = {"type": datatype}

        if "PRIMARY" in col:
            primary = name

        if "INDEX" in col:
            indexed.append(name)

        if "UNIQUE" in col:
            unique_cols.append(name)

        if "NOTNULL" in col:
            not_null_cols.append(name)

        # LEN constraint
        if "LEN(" in col:
            try:
                size = int(col.split("LEN(")[1].split(")")[0])
                len_constraints[name] = size
            except:
                print("Invalid LEN syntax")

        # CHECK constraint
        if "CHECK" in col:

            condition = col.split("CHECK(")[1].split(")")[0]

            if "<" in condition:
                operator = "<"
                value = condition.split("<")[1]

            elif ">" in condition:
                operator = ">"
                value = condition.split(">")[1]

            check_constraints[name] = {
                "operator": operator,
                "value": value
            }
        if "POSITIVE" in col:
            positive_cols.append(name)

    schema[table] = {
        "columns": col_names,
        "types": types_dict,
        "primary": primary,
        "indexed": indexed,
        "unique": unique_cols,
        "not_null": not_null_cols,
        "foreign_keys": foreign_keys,
        "check": check_constraints,
        "len": len_constraints,
        "positive": positive_cols
    }

    with open(schema_path, "w") as f:
        json.dump(schema, f, indent=4)

    with open(STORAGE + f"{table}.csv", "w") as f:
        f.write(",".join(col_names) + "\n")

    print("Table Created Successfully")
import os
import json
import csv
from storage import create_table


STORAGE = "storage/"



import re
def validate_constraints(table, header, row_values):
    schema_path = STORAGE + "schema.json"

    if not os.path.exists(schema_path):
        print("Metadata missing.")
        return False

    with open(schema_path, "r") as f:
        schema = json.load(f)

    if table not in schema:
        file_path = STORAGE + f"{table}.csv"
        if os.path.exists(file_path):
            print(f"Rebuilding schema for '{table}' from CSV...")
            schema = load_schema_from_csv(table)
        else:
            print(f"Table '{table}' does not exist.")
            return False

    table_schema = schema[table]
    types = table_schema.get("types", {})

    for i, col in enumerate(header):
        value = row_values[i]
        datatype = types.get(col)

        if datatype == "int":
            if not value.isdigit():
                print(f"Constraint Error: {col} must be integer")
                return False

        if col == "name":
            if not value.isalpha():
                print("Constraint Error: Name must contain only letters")
                return False

        if col == "age":
            if not value.isdigit() or int(value) <= 0:
                print("Constraint Error: Age must be positive integer")
                return False

        if col == "mobile":
            if not re.fullmatch(r"\d{10}", value):
                print("Constraint Error: Mobile must be exactly 10 digits")
                return False

    return True



def execute_query(parsed_query, plan):

    action = parsed_query["action"]
    table = parsed_query["table"]

    if action == "CREATE":
        create_table(table, parsed_query["columns"])
        return None

    if action == "INSERT":
        file_path = STORAGE + f"{table}.csv"

        if not os.path.exists(file_path):
            return "Error: Table does not exist"

        with open(file_path, "r") as f:
            reader = list(csv.reader(f))

        header = reader[0]
        values = parsed_query["values"]

        # 🔥 Column count check
        if len(values) != len(header):
            return f"Error: Expected {len(header)} values, got {len(values)}"

        # 🔥 Validate constraints
        if not validate_constraints(table, header, values):
            return "Error: Constraint violation"

        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(values)

        return "Inserted Successfully"


    if action == "SELECT":
        file_path = STORAGE + f"{table}.csv"

        if not os.path.exists(file_path):
            print("Table not found")
            return None

        with open(file_path, "r") as f:
            rows = f.readlines()

        if not parsed_query["condition"]:
            return [row.strip() for row in rows]

        column = parsed_query["condition"]["column"]
        value = parsed_query["condition"]["value"]

        schema_path = STORAGE + "schema.json"
        with open(schema_path, "r") as f:
            schema = json.load(f)

        col_index = schema[table]["columns"].index(column)

        result = []
        for row in rows:
            data = row.strip().split(",")
            if data[col_index] == value:
                result.append(row.strip())

        return result

    if action == "DELETE":
        file_path = STORAGE + f"{table}.csv"

        if not os.path.exists(file_path):
            print("Table not found")
            return None

        with open(file_path, "r") as f:
            reader = list(csv.reader(f))

        header = reader[0]
        rows = reader[1:]

        column = parsed_query["condition"]["column"]
        value = parsed_query["condition"]["value"]

        if column not in header:
            print("Column not found")
            return None

        col_index = header.index(column)

        new_rows = []
        deleted = False

        for row in rows:
            if row[col_index] != value:
                new_rows.append(row)
            else:
                deleted = True

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(new_rows)

        if deleted:
            print("Deleted Successfully")
        else:
            print("No matching record found")

        return None
    if action == "DROP":
        schema_path = STORAGE + "schema.json"
        file_path = STORAGE + f"{table}.csv"

        # Remove from schema
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema = json.load(f)

            if table in schema:
                del schema[table]

                with open(schema_path, "w") as f:
                    json.dump(schema, f, indent=4)

        # Remove CSV file
        if os.path.exists(file_path):
            os.remove(file_path)

        print(f"Table '{table}' removed successfully.")
        return None


    if action == "UPDATE":
        file_path = STORAGE + f"{table}.csv"



        with open(file_path, "r") as f:
            reader = list(csv.reader(f))

        header = reader[0]
        rows = reader[1:]

        set_column = parsed_query["set"]["column"]
        set_value = parsed_query["set"]["value"]

        where_column = parsed_query["condition"]["column"]
        where_value = parsed_query["condition"]["value"]

        set_index = header.index(set_column)
        where_index = header.index(where_column)

        updated = False
        
        for row in rows:
            if row[where_index] == where_value:

                # 🔥 Create temporary updated row
                new_row = row.copy()
                new_row[set_index] = set_value

                # 🔥 Validate updated row BEFORE applying
                if not validate_constraints(table, header, new_row):
                    return None

        # 🔥 Apply update only if valid
        row[set_index] = set_value
        updated = True

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

        if updated:
            print("Updated Successfully")
        else:
            print("No matching record found")

        return None

def load_schema_from_csv(table):
    file_path = STORAGE + f"{table}.csv"

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

    # If schema.json exists, merge
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            existing_schema = json.load(f)
    else:
        existing_schema = {}

    existing_schema.update(schema)

    with open(schema_path, "w") as f:
        json.dump(existing_schema, f, indent=4)

    return existing_schema

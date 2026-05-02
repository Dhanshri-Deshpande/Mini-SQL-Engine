import os
import json
import csv
from storage import create_table
import re


STORAGE = "storage/"




def validate_constraints(table, header, row_values):

    schema_path = STORAGE + "schema.json"

    with open(schema_path, "r") as f:
        schema = json.load(f)

    table_schema = schema[table]

    types = table_schema.get("types", {})
    primary = table_schema.get("primary")
    unique_cols = table_schema.get("unique", [])
    not_null_cols = table_schema.get("not_null", [])
    foreign_keys = table_schema.get("foreign_keys", {})
    check_constraints = table_schema.get("check", {})
    file_path = STORAGE + f"{table}.csv"
    len_constraints = table_schema.get("len", {})
    positive_cols = table_schema.get("positive", [])

    existing_rows = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            reader = list(csv.reader(f))
            existing_rows = reader[1:]

    for i, col in enumerate(header):

        value = row_values[i].strip()
        datatype = types.get(col)

        if datatype is None:
            continue

    
        if col in not_null_cols and value.strip() == "":
            print(f"{col} cannot be NULL")
            return False
        
       

        if datatype["type"] == "int":
            if not value.isdigit():
                print(f"{col} must be integer")
                return False

        elif datatype["type"] in ["float", "double"]:
            try:
                float(value)
            except:
                print(f"{col} must be numeric")
                return False

        elif datatype["type"] == "boolean":
            value_clean = value.strip().lower()
            if value_clean not in ["true", "false"]:
                print(f"{col} must be TRUE or FALSE")
                return False

        elif datatype["type"] == "varchar":
            if len(value) > datatype["size"]:
                print(f"{col} exceeds varchar({datatype['size']}) limit")
                return False

        elif datatype["type"] == "char":
            if len(value) != datatype["size"]:
                print(f"{col} must be exactly {datatype['size']} characters")
                return False

        elif datatype["type"] == "date":
            value_clean = value.strip()
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value_clean):
                print(f"{col} must be YYYY-MM-DD")
                return False

        elif datatype["type"] == "time":
            value_clean = value.strip()
            if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", value_clean):
                print(f"{col} must be HH:MM:SS")
                return False

        elif datatype["type"] == "datetime":
            value_clean = value.strip()
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", value_clean):
                print(f"{col} must be YYYY-MM-DD HH:MM:SS")
                return False
                
        # POSITIVE constraint
        if col in positive_cols:
            try:
                if float(value) <= 0:
                    print(f"{col} must be positive")
                    return False
            except:
                print(f"{col} must be numeric for POSITIVE constraint")
                return False
        # -------------------------
        # 🔹 LEN CONSTRAINT
        # -------------------------

        if col in len_constraints:

            expected_len = len_constraints[col]

            if len(value) != expected_len:
                print(f"LEN constraint failed: {col} must be exactly {expected_len} characters")
                return False

        # -------------------------
        # 🔹 CHECK CONSTRAINT
        # -------------------------

        if col in check_constraints:

            rule = check_constraints[col]
            operator = rule["operator"]
            check_value = rule["value"]

            try:
                val = float(value)
                check_val = float(check_value)
            except:
                print(f"Invalid value for CHECK constraint on {col}")
                return False

            if operator == "<" and not (val < check_val):
                print(f"CHECK constraint failed: {col} must be < {check_val}")
                return False

            elif operator == ">" and not (val > check_val):
                print(f"CHECK constraint failed: {col} must be > {check_val}")
                return False

            elif operator == "<=" and not (val <= check_val):
                print(f"CHECK constraint failed: {col} must be <= {check_val}")
                return False

            elif operator == ">=" and not (val >= check_val):
                print(f"CHECK constraint failed: {col} must be >= {check_val}")
                return False

            elif operator == "==" and not (val == check_val):
                print(f"CHECK constraint failed: {col} must be == {check_val}")
                return False

        if col == primary:
            for existing_row in existing_rows:
                if existing_row == row_values:
                    continue
                if existing_row[i] == value:
                    print("Primary key violation")
                    return False

        if col in unique_cols:
            for existing_row in existing_rows:
                if existing_row == row_values:
                    continue
                if existing_row[i] == value:
                    print(f"Unique constraint failed on {col}")
                    return False

        if col in foreign_keys:
            ref_table = foreign_keys[col]["ref_table"]
            ref_column = foreign_keys[col]["ref_column"]

            ref_file = STORAGE + f"{ref_table}.csv"

            if not os.path.exists(ref_file):
                print("Referenced table not found")
                return False

            with open(ref_file, "r") as f:
                reader = list(csv.reader(f))
                ref_header = reader[0]
                ref_rows = reader[1:]

            ref_index = ref_header.index(ref_column)

            found = False
            for ref_row in ref_rows:
                if ref_row[ref_index] == value:
                    found = True
                    break

            if not found:
                print("Foreign key constraint violation")
                return False
    return True

        
def execute_query(parsed_query, plan):

    action = parsed_query["action"]

    table = parsed_query.get("table")   # safer

    if action == "CREATE":

        schema_path = STORAGE + "schema.json"

        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema = json.load(f)
        else:
            schema = {}

        schema[table] = {
        "columns": parsed_query["columns"],
        "types": parsed_query["types"],
        "primary": parsed_query["primary"],
        "unique": parsed_query["unique"],
        "not_null": parsed_query["not_null"],
        "foreign_keys": parsed_query["foreign_keys"],
        "check": parsed_query.get("check", {}),
        "len": parsed_query.get("len", {}),
        "positive": parsed_query.get("positive", [])  
    }

        with open(schema_path, "w") as f:
            json.dump(schema, f, indent=4)

        file_path = STORAGE + f"{table}.csv"

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(parsed_query["columns"])

        print(f"Table '{table}' created with constraints.")
        return None

    if action == "ALTER_MODIFY":

        file_path = STORAGE + f"{table}.csv"
        schema_path = STORAGE + "schema.json"

        if not os.path.exists(file_path):
            print("Table not found")
            return None

        with open(schema_path, "r") as f:
            schema = json.load(f)

        if table not in schema:
            print("Schema not found")
            return None

        column = parsed_query["column"]

        if column not in schema[table]["columns"]:
            print("Column not found")
            return None

        # Update datatype in schema
        schema[table]["types"][column] = parsed_query["type"]

        with open(schema_path, "w") as f:
            json.dump(schema, f, indent=4)

        print("Column modified successfully")
        return None
    if action == "RENAME":

        old_name = parsed_query["old_name"]
        new_name = parsed_query["new_name"]

        old_file = STORAGE + f"{old_name}.csv"
        new_file = STORAGE + f"{new_name}.csv"
        schema_path = STORAGE + "schema.json"

        if not os.path.exists(old_file):
            print("Table not found")
            return None

        # Rename CSV file
        os.rename(old_file, new_file)

        # Update schema.json
        with open(schema_path, "r") as f:
            schema = json.load(f)

        if old_name in schema:
            schema[new_name] = schema.pop(old_name)

            with open(schema_path, "w") as f:
                json.dump(schema, f, indent=4)

        print("Table renamed successfully")
        return None
        
    if action == "INSERT":
        file_path = STORAGE + f"{table}.csv"

        if not os.path.exists(file_path):
            return "Error: Table does not exist"

        with open(file_path, "r") as f:
            reader = list(csv.reader(f))

        header = reader[0]

        # Now values contains multiple rows
        all_rows = parsed_query["values"]

        for values in all_rows:

            if len(values) != len(header):
                return f"Error: Expected {len(header)} values, got {len(values)}"

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
        schema_path = STORAGE + "schema.json"

        if not os.path.exists(file_path):
            print("Table not found")
            return None

        # Load schema
        with open(schema_path, "r") as f:
            schema = json.load(f)

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

        # -----------------------------
        # FOREIGN KEY DELETE CHECK
        # -----------------------------
        primary_col = schema[table].get("primary")

        if column == primary_col:

            for other_table, other_schema in schema.items():

                if other_table == table:
                    continue

                foreign_keys = other_schema.get("foreign_keys", {})

                for fk_col, fk_info in foreign_keys.items():

                    if (
                        fk_info["ref_table"] == table
                        and fk_info["ref_column"] == column
                    ):

                        child_file = STORAGE + f"{other_table}.csv"

                        if os.path.exists(child_file):

                            with open(child_file, "r") as f:
                                child_reader = list(csv.reader(f))

                            child_header = child_reader[0]
                            child_rows = child_reader[1:]

                            fk_index = child_header.index(fk_col)

                            for child_row in child_rows:
                                if child_row[fk_index] == value:
                                    print("Cannot delete: record is referenced in another table")
                                    return None

        # -----------------------------
        # SAFE DELETE
        # -----------------------------
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

        if not os.path.exists(schema_path):
            print("Schema not found")
            return None

        with open(schema_path, "r") as f:
            schema = json.load(f)

        if table not in schema:
            print("Table not found")
            return None

        # ---------------------------------
        # FOREIGN KEY DROP CHECK
        # ---------------------------------
        for other_table, other_schema in schema.items():

            if other_table == table:
                continue

            foreign_keys = other_schema.get("foreign_keys", {})

            for fk_col, fk_info in foreign_keys.items():

                if fk_info["ref_table"] == table:
                    print(
                        f"Cannot remove table: referenced by '{other_table}' table"
                    )
                    return None

        # ---------------------------------
        # SAFE DROP
        # ---------------------------------
        del schema[table]

        with open(schema_path, "w") as f:
            json.dump(schema, f, indent=4)

        if os.path.exists(file_path):
            os.remove(file_path)

        print(f"Table '{table}' removed successfully.")
        return None


    if action == "TRUNCATE":

        file_path = STORAGE + f"{table}.csv"

        if not os.path.exists(file_path):
            print("Table not found")
            return None

        with open(file_path, "r") as f:
            header = f.readline()

        with open(file_path, "w") as f:
            f.write(header)

        print("Table truncated successfully")
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

                new_row = row.copy()
                new_row[set_index] = set_value

                if not validate_constraints(table, header, new_row):
                    return None

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

    if action == "ALTER_ADD":

        file_path = STORAGE + f"{table}.csv"
        schema_path = STORAGE + "schema.json"

        if not os.path.exists(file_path):
            print("Table not found")
            return None

        # Load schema
        with open(schema_path, "r") as f:
            schema = json.load(f)

        if table not in schema:
            print("Schema not found")
            return None

        # Update schema
        schema[table]["columns"].append(parsed_query["column"])
        schema[table]["types"][parsed_query["column"]] = parsed_query["type"]

        with open(schema_path, "w") as f:
            json.dump(schema, f, indent=4)

        # Update CSV (add empty value for existing rows)
        with open(file_path, "r") as f:
            rows = list(csv.reader(f))

        rows[0].append(parsed_query["column"])  # header

        for i in range(1, len(rows)):
            rows[i].append("")  # empty default value

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print("Column added successfully")
        return None
    if action == "ALTER_DROP":

        file_path = STORAGE + f"{table}.csv"
        schema_path = STORAGE + "schema.json"

        if not os.path.exists(file_path):
            print("Table not found")
            return None

        # Load schema
        with open(schema_path, "r") as f:
            schema = json.load(f)

        if table not in schema:
            print("Schema not found")
            return None

        column = parsed_query["column"]

        if column not in schema[table]["columns"]:
            print("Column not found")
            return None

        col_index = schema[table]["columns"].index(column)

        # Update schema
        schema[table]["columns"].remove(column)
        schema[table]["types"].pop(column, None)

        with open(schema_path, "w") as f:
            json.dump(schema, f, indent=4)

        # Update CSV
        with open(file_path, "r") as f:
            rows = list(csv.reader(f))

        for row in rows:
            row.pop(col_index)

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print("Column dropped successfully")
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

    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            existing_schema = json.load(f)
    else:
        existing_schema = {}

    existing_schema.update(schema)

    with open(schema_path, "w") as f:
        json.dump(existing_schema, f, indent=4)

    return existing_schema

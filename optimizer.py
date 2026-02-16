import json
import os

STORAGE = "storage/"

def optimize_query(parsed_query):
    if parsed_query["action"] != "SELECT" or not parsed_query["condition"]:
        return None

    table = parsed_query["table"]
    column = parsed_query["condition"]["column"]

    schema_path = STORAGE + "schema.json"
    if not os.path.exists(schema_path):
        return None

    with open(schema_path, "r") as f:
        schema = json.load(f)

    if table not in schema:
        return None

    total_rows = count_rows(table)

    # Check primary or secondary index
    if column == schema[table]["primary"]:
        return {
            "plan": f"INDEX_SCAN on {table}.{column}",
            "cost": 1
        }

    elif column in schema[table]["indexed"]:
        return {
            "plan": f"INDEX_SCAN on {table}.{column}",
            "cost": 2
        }

    else:
        return {
            "plan": "FULL_TABLE_SCAN",
            "cost": total_rows
        }


def count_rows(table):
    file_path = STORAGE + f"{table}.csv"
    if not os.path.exists(file_path):
        return 0

    with open(file_path, "r") as f:
        return len(f.readlines())

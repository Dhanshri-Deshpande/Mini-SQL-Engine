def parse_query(tokens):
    if not tokens:
        return None

    command = tokens[0].upper()

    if command == "MAKE":
        table = tokens[1]
        columns = " ".join(tokens[3:-1])
        columns = columns.split(",")
        return {
            "action": "CREATE",
            "table": table,
            "columns": [col.strip() for col in columns]
        }

    elif command == "REMOVE":
        return {
            "action": "DROP",
            "table": tokens[1]
        }

    elif command == "ADD":
        table = tokens[1]
        values = " ".join(tokens[3:-1])
        values = values.split(",")
        return {
            "action": "INSERT",
            "table": table,
            "values": [v.strip() for v in values]
        }

    elif command == "SHOW":
        table = tokens[1]
        if "WHERE" in tokens:
            condition = tokens[tokens.index("WHERE") + 1]
            column, value = condition.split("=")
            return {
                "action": "SELECT",
                "table": table,
                "condition": {"column": column, "value": value}
            }
        else:
            return {
                "action": "SELECT",
                "table": table,
                "condition": None
            }

    elif command == "ERASE":
        table = tokens[1]
        condition = tokens[tokens.index("WHERE") + 1]
        column, value = condition.split("=")
        return {
            "action": "DELETE",
            "table": table,
            "condition": {"column": column, "value": value}
        }

    elif command == "CHANGE":
        table = tokens[1]

        set_index = tokens.index("SET")
        where_index = tokens.index("WHERE")

        set_part = tokens[set_index + 1]
        where_part = tokens[where_index + 1]

        set_column, set_value = set_part.split("=")
        where_column, where_value = where_part.split("=")

        return {
            "action": "UPDATE",
            "table": table,
            "set": {
                "column": set_column,
                "value": set_value
            },
            "condition": {
                "column": where_column,
                "value": where_value
            }
        }


        return None

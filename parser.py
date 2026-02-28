def parse_query(tokens):
    if not tokens:
        return None

    command = tokens[0].upper()

    if command == "MAKE":
        table = tokens[1]

        # Join everything after table name
        full_query = " ".join(tokens[2:])

        # Extract content inside parentheses
        if "(" not in full_query or ")" not in full_query:
            print("Invalid CREATE syntax")
            return None

        definition = full_query[
            full_query.find("(")+1 : full_query.rfind(")")
        ]

        columns_raw = definition.split(",")

        columns = []
        types = {}
        primary = None
        unique = []
        not_null = []
        foreign_keys = {}

        for col_def in columns_raw:

            col_def = col_def.strip()

            if not col_def:
                continue

            parts = col_def.split()

            if len(parts) < 2:
                print("Invalid column definition:", col_def)
                return None

            col_name = parts[0]
            col_type_raw = parts[1].lower()

            columns.append(col_name)

            # --------------------
            # DATA TYPES
            # --------------------

            if col_type_raw == "int":
                types[col_name] = {"type": "int"}



            
            elif col_type_raw == "varchar":
                try:
                    # Expect format: varchar ( 50 )
                    if len(parts) >= 5 and parts[2] == "(" and parts[4] == ")":
                        size = int(parts[3])
                        types[col_name] = {"type": "varchar", "size": size}
                    else:
                        print("Invalid varchar syntax")
                        return None
                except:
                    print("Invalid varchar syntax")
                    return None
            else:
                print(f"Unsupported data type: {col_type_raw}")
                return None

            # --------------------
            # CONSTRAINTS
            # --------------------

            if "PRIMARY" in parts:
                primary = col_name

            if "UNIQUE" in parts:
                unique.append(col_name)

            if "NOT" in parts and "NULL" in parts:
                not_null.append(col_name)

        return {
            "action": "CREATE",
            "table": table,
            "columns": columns,
            "types": types,
            "primary": primary,
            "unique": unique,
            "not_null": not_null,
            "foreign_keys": foreign_keys
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
    elif command == "TRUNCATE":

        if len(tokens) < 2:
            print("Invalid TRUNCATE syntax")
            return None

        table = tokens[1]

        # remove trailing semicolon if present
        if table.endswith(";"):
            table = table[:-1]

        return {
            "action": "TRUNCATE",
            "table": table
        }
    elif command == "RENAME":
        if len(tokens) < 4 or tokens[2].upper() != "TO":
            print("Invalid RENAME syntax. Use: RENAME old TO new")
            return None

        return {
            "action": "RENAME",
            "old_name": tokens[1],
            "new_name": tokens[3]
        }
    elif command == "ALTER":

        if len(tokens) < 4:
            print("Invalid ALTER syntax")
            return None

        table = tokens[1]

        # ------------------ ADD COLUMN ------------------
        if tokens[2].upper() == "ADD":

            col_name = tokens[3]

            # INT
            if tokens[4].lower() == "int":
                return {
                    "action": "ALTER_ADD",
                    "table": table,
                    "column": col_name,
                    "type": {"type": "int"}
                }

            # VARCHAR
            elif tokens[4].lower() == "varchar":
                if len(tokens) >= 8 and tokens[5] == "(" and tokens[7] == ")":
                    size = int(tokens[6])
                    return {
                        "action": "ALTER_ADD",
                        "table": table,
                        "column": col_name,
                        "type": {"type": "varchar", "size": size}
                    }
                else:
                    print("Invalid varchar syntax")
                    return None

            else:
                print("Unsupported datatype in ALTER")
                return None

        # ------------------ DROP COLUMN ------------------
        elif tokens[2].upper() == "DROP":

            col_name = tokens[3]

            return {
                "action": "ALTER_DROP",
                "table": table,
                "column": col_name
            }

        else:
            print("Invalid ALTER operation")
            return None
     
    
    elif command == "SHOW":

        # SHOW table;
        if len(tokens) == 2:
            return {
                "action": "SELECT",
                "table": tokens[1],
                "condition": None
            }

        # SHOW * FROM table;
        if tokens[1] == "*":
            table = tokens[3]
        else:
            table = tokens[1]

        if "WHERE" in tokens:
            condition = tokens[tokens.index("WHERE") + 1]
            column, value = condition.split("=")
            return {
                "action": "SELECT",
                "table": table,
                "condition": {"column": column, "value": value}
            }

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

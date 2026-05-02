def parse_query(tokens):
    if not tokens:
        return None

    command = tokens[0].upper()

    if command == "MAKE":
        table = tokens[1]

        full_query = " ".join(tokens[2:])
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
        check_constraints = {}
        len_constraints = {}
        positive = []
        for col_def in columns_raw:

            col_def = col_def.strip()
            if not col_def:
                continue

            parts = col_def.split()

            # FIRST check FOREIGN KEY
            if col_def.upper().startswith("FOREIGN KEY"):

                try:
                    fk_col = col_def.split("(")[1].split(")")[0].strip()

                    ref_table = col_def.split("REFERENCES")[1].split("(")[0].strip().lower()

                    ref_column = col_def.split("REFERENCES")[1].split("(")[1].split(")")[0].strip()

                    foreign_keys[fk_col] = {
                        "ref_table": ref_table,
                        "ref_column": ref_column
                    }

                    continue

                except:
                    print("Invalid FOREIGN KEY syntax")
                    return None

            # THEN normal column parsing
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
            elif col_type_raw in ["float", "double"]:
                types[col_name] = {"type": col_type_raw}

            elif col_type_raw == "boolean":
                types[col_name] = {"type": "boolean"}

            elif col_type_raw == "date":
                types[col_name] = {"type": "date"}

            elif col_type_raw == "time":
                types[col_name] = {"type": "time"}

            elif col_type_raw == "datetime":
                types[col_name] = {"type": "datetime"}
            elif col_type_raw == "varchar":
                if len(parts) >= 5 and parts[2] == "(" and parts[4] == ")":
                    size = int(parts[3])
                    types[col_name] = {"type": "varchar", "size": size}
                else:
                    print("Invalid varchar syntax")
                    return None
            elif col_type_raw == "char":
                if len(parts) >= 5 and parts[2] == "(" and parts[4] == ")":
                    size = int(parts[3])
                    types[col_name] = {
                        "type": "char",
                        "size": size
                    }
                else:
                    print("Invalid char syntax")
                    return None
            else:
                print(f"Unsupported data type: {col_type_raw}")
                return None

            # --------------------
            # CONSTRAINTS
            # --------------------

            if "PRIMARY" in parts and "KEY" in parts:
                primary = col_name

            if "UNIQUE" in parts:
                unique.append(col_name)

            if "NOT" in parts and "NULL" in parts:
                not_null.append(col_name)
            
            # POSITIVE constraint
            if "POSITIVE" in parts:
                positive.append(col_name)
            # --------------------
            # LEN CONSTRAINT
            # --------------------
            for i in range(len(parts)):

                # Case 1 → LEN(10)
                if parts[i].upper().startswith("LEN(") and parts[i].endswith(")"):
                    try:
                        size = int(parts[i][4:-1])
                        len_constraints[col_name] = size
                    except:
                        print("Invalid LEN syntax")
                        return None

                # Case 2 → LEN ( 10 )
                elif parts[i].upper() == "LEN":
                    try:
                        if i + 3 < len(parts):
                            if parts[i+1] == "(" and parts[i+3] == ")":
                                size = int(parts[i+2])
                                len_constraints[col_name] = size
                    except:
                        print("Invalid LEN syntax")
                        return None
            if "CHECK" in parts:

                check_str = col_def[col_def.find("CHECK"):]

                try:
                    condition = check_str.split("(")[1].split(")")[0]

                    if ">=" in condition:
                        col, val = condition.split(">=")
                        operator = ">="

                    elif "<=" in condition:
                        col, val = condition.split("<=")
                        operator = "<="

                    elif ">" in condition:
                        col, val = condition.split(">")
                        operator = ">"

                    elif "<" in condition:
                        col, val = condition.split("<")
                        operator = "<"

                    check_constraints[col_name] = {
                        "operator": operator,
                        "value": val.strip()
                    }

                except:
                    print("Invalid CHECK syntax")
                    return None

        return {
            "action": "CREATE",
            "table": table,
            "columns": columns,
            "types": types,
            "primary": primary,
            "unique": unique,
            "not_null": not_null,
            "foreign_keys": foreign_keys,
            "check": check_constraints,
            "len": len_constraints,
            "positive": positive
        }
            
    elif command == "REMOVE":
        return {
            "action": "DROP",
            "table": tokens[1]
        }
    
    elif command == "ADD":
        table = tokens[1]

        full_query = " ".join(tokens[2:]).strip()

        # Remove ending semicolon
        if full_query.endswith(";"):
            full_query = full_query[:-1]

        all_rows = []
        current = ""
        bracket_count = 0

        for ch in full_query:
            if ch == "(":
                bracket_count += 1

            if ch == ")":
                bracket_count -= 1

            current += ch

            # One full row completed
            if bracket_count == 0 and current.strip():
                row = current.strip().strip(",")

                row = row.replace("(", "").replace(")", "").strip()

                if row:
                    values = [v.strip() for v in row.split(",")]
                    all_rows.append(values)

                current = ""

        return {
            "action": "INSERT",
            "table": table,
            "values": all_rows
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

            if len(tokens) < 5:
                print("Invalid ALTER ADD syntax")
                return None

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
                print("Unsupported datatype in ALTER ADD")
                return None

        # ------------------ DROP COLUMN ------------------
        elif tokens[2].upper() == "DROP":

            if len(tokens) < 4:
                print("Invalid ALTER DROP syntax")
                return None

            return {
                "action": "ALTER_DROP",
                "table": table,
                "column": tokens[3]
            }

        # ------------------ MODIFY COLUMN ------------------
        elif tokens[2].upper() == "MODIFY":

            if len(tokens) < 5:
                print("Invalid ALTER MODIFY syntax")
                return None

            col_name = tokens[3]

            # INT
            if tokens[4].lower() == "int":
                return {
                    "action": "ALTER_MODIFY",
                    "table": table,
                    "column": col_name,
                    "type": {"type": "int"}
                }

            # VARCHAR
            elif tokens[4].lower() == "varchar":
                if len(tokens) >= 8 and tokens[5] == "(" and tokens[7] == ")":
                    size = int(tokens[6])
                    return {
                        "action": "ALTER_MODIFY",
                        "table": table,
                        "column": col_name,
                        "type": {"type": "varchar", "size": size}
                    }
                else:
                    print("Invalid varchar syntax")
                    return None

            else:
                print("Unsupported datatype in ALTER MODIFY")
                return None

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

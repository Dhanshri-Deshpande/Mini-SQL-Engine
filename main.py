import sys
from tokenizer import tokenize
from parser import parse_query
from optimizer import optimize_query
from executor import execute_query

def run_query(query):
    tokens = tokenize(query)
    parsed = parse_query(tokens)
    plan = optimize_query(parsed)
    result = execute_query(parsed, plan)
    return result

def display_banner():
    print("=" * 50)
    print("        Supports DDL + DML + Optimizer")
    print("=" * 50)


def main():
    display_banner()

    while True:
        try:
            query = input("DB> ").strip()

       
            if query.lower() in ["exit", "quit"]:
                print("Exiting MiniDB...")
                sys.exit(0)

            if not query:
                continue

        
            tokens = tokenize(query)

          
            parsed_query = parse_query(tokens)

            if parsed_query is None:
                print("Invalid Query Syntax")
                continue

            execution_plan = optimize_query(parsed_query)

      
            if execution_plan:
                print("\nExecution Plan:")
                print(f"→ {execution_plan['plan']}")
                print(f"→ Estimated Cost: {execution_plan['cost']}\n")

            
            result = execute_query(parsed_query, execution_plan)

         
            if result:
                print("Result:")
                for row in result:
                    print(row)

        except Exception as e:
            print(f"⚠ Error: {e}")


if __name__ == "__main__":
    main()

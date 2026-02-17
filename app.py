from flask import Flask, request, jsonify
from main import run_query
from flask_cors import CORS
import os
import csv
from executor import load_schema_from_csv
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE = os.path.join(BASE_DIR, "storage")
if not os.path.exists(STORAGE):
    os.makedirs(STORAGE)


# 🔥 Get all tables
@app.route("/tables")
def get_tables():
    tables = []
    for file in os.listdir(STORAGE):
        if file.endswith(".csv"):
            tables.append(file.replace(".csv", ""))
    return jsonify(tables)


# 🔥 Open table
@app.route("/table/<name>")
def get_table(name):
    file_path = os.path.join(STORAGE, f"{name}.csv")

    print("🔍 Looking for:", file_path)

    if not os.path.exists(file_path):
        return jsonify({"error": "Table not found"}), 404

    with open(file_path, "r") as f:
        reader = csv.reader(f)
        data = list(reader)

    return jsonify(data)


@app.route("/upload", methods=["POST"])
def upload_csv():
    file = request.files.get("file")

    if not file:
        return jsonify({"message": "No file selected"}), 400

    if not file.filename.endswith(".csv"):
        return jsonify({"message": "Only CSV files allowed"}), 400

    save_path = os.path.join(STORAGE, file.filename)
    file.save(save_path)

    # 🔥 Auto-generate schema
    table_name = file.filename.replace(".csv", "")
    load_schema_from_csv(table_name)

    return jsonify({"message": "CSV uploaded successfully"})


# 🔥 Execute Query
@app.route("/query", methods=["POST"])
def execute():
    try:
        data = request.json
        query = data.get("query")

        print("🔥 Received Query:", query)

        result = run_query(query)

        # Refresh tables
        tables = []
        for file in os.listdir(STORAGE):
            if file.endswith(".csv"):
                tables.append(file.replace(".csv", ""))

        return jsonify({
            "result": result,
            "tables": tables
        })

    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})


@app.route("/")
def home():
    return "Mini SQL Backend Running 🚀"


if __name__ == "__main__":
    app.run(debug=True)

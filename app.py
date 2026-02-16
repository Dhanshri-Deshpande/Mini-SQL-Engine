from flask import Flask, request, jsonify, render_template
from main import run_query


app = Flask(__name__)


@app.route("/tables")
def get_tables():
    files = []
    for file in os.listdir("storage"):
        if file.endswith(".csv"):
            files.append(file.replace(".csv", ""))
    return jsonify(files)


@app.route("/")
def home():
    return render_template("index.html")   # MUST be this

@app.route("/query", methods=["POST"])
def execute():
    try:
        data = request.json
        query = data.get("query")

        print("🔥 Received Query:", query)

        result = run_query(query)

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)

# 📦 Custom SQL Engine (DDL + DML)

## 📌 Overview
This project is a custom-built SQL-like engine that supports basic DDL (Data Definition Language) and DML (Data Manipulation Language) operations using simplified commands.

It is designed for learning DBMS concepts such as:
- Table creation
- Data manipulation
- Constraints handling
- Query execution
- Schema management using JSON

---

## 🚀 Features
- Custom SQL syntax (MAKE, ADD, SHOW, etc.)
- Supports DDL and DML queries
- JSON-based storage (schema + data)
- Constraint support:
  - PRIMARY KEY
  - NOT NULL
  - UNIQUE
  - CHECK
- Table modification (ALTER, RENAME, TRUNCATE)
- Record operations (INSERT, UPDATE, DELETE, SELECT)

---

## 🛠️ DDL Commands

| Command | Description | Example |
|--------|------------|--------|
| MAKE | Create table | MAKE student (id int PRIMARY KEY, name varchar(50)) |
| REMOVE | Delete table | REMOVE student |
| ALTER ADD | Add column | ALTER student ADD age int |
| ALTER DROP | Remove column | ALTER student DROP age |
| ALTER MODIFY | Modify column | ALTER student MODIFY name varchar(100) |
| TRUNCATE | Delete all records | TRUNCATE student |
| RENAME | Rename table | RENAME student TO student_data |

---

## 📗 DML Commands

| Command | Description | Example |
|--------|------------|--------|
| ADD | Insert record | ADD student (1, John) |
| SHOW | Display table | SHOW student |
| SHOW WHERE | Conditional select | SHOW student WHERE id=1 |
| CHANGE | Update record | CHANGE student SET name=Rahul WHERE id=1 |
| ERASE | Delete record | ERASE student WHERE id=1 |

---

## 🧱 Constraints

- PRIMARY KEY → Unique + Not Null
- NOT NULL → Cannot be empty
- UNIQUE → No duplicate values
- CHECK → Condition validation (e.g., age < 19)
- LEN → ❌ Not working (known issue)
- POSITIVE → Value must be > 0

---

## 📊 Data Types

- INT
- FLOAT
- DOUBLE
- VARCHAR(n)
- DATE
- TIME
- DATETIME
- TIMESTAMP
- BOOLEAN

---

## 🧪 Example Queries

MAKE student (id int PRIMARY KEY, name varchar(50));

ADD student VALUES (1, John);

SHOW student;

CHANGE student SET name=Rahul WHERE id=1;

ERASE student WHERE id=1;

ALTER student ADD age int;

TRUNCATE student;

RENAME student TO student_info;

REMOVE student_info;

---

## ⚠️ Known Issues

### LEN Constraint Not Working
- LEN is not implemented in parser
- Not stored in schema.json
- Not validated during insert/update

### Fix Suggestion:
Use VARCHAR(n) instead of LEN

---

## 📁 Project Structure

/project-root
│
├── schema.json
├── data/
├── parser/
├── engine/
└── README.md

---

## ⚙️ How It Works

1. Query is entered by user
2. Parser identifies command
3. Engine executes logic
4. Schema/data updated in JSON

---

## 🧠 Future Improvements

- Implement LEN constraint
- Add JOIN queries
- Add ORDER BY, GROUP BY
- Improve validation
- Build GUI interface

---

## 🧑‍💻 Usage

Clone repository:
git clone https://github.com/Dhanshri-Deshpande/Mini-SQL-Engine.git

Run project:
python main.py

---

## 📌 Note
This is a simplified SQL engine for educational purposes.

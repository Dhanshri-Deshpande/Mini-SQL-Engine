# Mini SQL Engine

A custom-built SQL-like database engine developed in Python for learning and implementing core Database Management System (DBMS) concepts. The project supports basic Data Definition Language (DDL) and Data Manipulation Language (DML) operations using simplified SQL-inspired commands.

---

## 📌 Overview

Mini SQL Engine is a lightweight database management system that stores schemas and records using JSON and CSV files. It allows users to create tables, insert data, apply constraints, update records, and manage database structures without using a traditional DBMS.

This project demonstrates the implementation of:

* Query Parsing
* Query Execution
* Schema Management
* Constraint Enforcement
* Referential Integrity
* Data Storage and Retrieval

---

## 🚀 Features

### DDL Operations

* Create Tables
* Remove Tables
* Rename Tables
* Truncate Tables
* Add Columns
* Drop Columns
* Modify Column Datatypes

### DML Operations

* Insert Records
* Select Records
* Conditional Selection
* Update Records
* Delete Records

### Constraint Support

* PRIMARY KEY
* FOREIGN KEY
* UNIQUE
* NOT NULL
* CHECK
* POSITIVE
* VARCHAR Length Validation

### DBMS Features

* JSON-based Schema Storage
* CSV-based Data Storage
* Constraint Validation Engine
* Referential Integrity Enforcement
* Foreign Key Validation
* Foreign Key Delete Restriction
* Foreign Key Drop Table Restriction

---

# 🏗️ Architecture

```text
User Query
     │
     ▼
Query Parser
     │
     ▼
Execution Engine
     │
 ┌───┴────┐
 ▼        ▼
Schema   Data
(JSON)   (CSV)
```

---

# 📁 Project Structure

```text
Mini-SQL-Engine/
│
├── main.py
├── parser.py
├── executor.py
├── storage/
│   ├── schema.json
│   ├── student.csv
│   ├── course.csv
│   └── ...
│
└── README.md
```

---

# 🛠 Supported Commands

## DDL Commands

### Create Table

```sql
MAKE student (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    marks FLOAT
)
```

### Remove Table

```sql
REMOVE student
```

### Rename Table

```sql
RENAME student TO student_data
```

### Truncate Table

```sql
TRUNCATE student
```

### Add Column

```sql
ALTER student ADD age INT
```

### Drop Column

```sql
ALTER student DROP age
```

### Modify Column

```sql
ALTER student MODIFY name VARCHAR(100)
```

---

# 📗 DML Commands

## Insert Records

Single Row:

```sql
ADD student (1, John, 90)
```

Multiple Rows:

```sql
ADD student
(1, John, 90),
(2, Rahul, 85),
(3, Priya, 92)
```

## Display Records

```sql
SHOW student
```

## Conditional Selection

```sql
SHOW student WHERE id=1
```

## Update Records

```sql
CHANGE student SET name=Rahul WHERE id=1
```

## Delete Records

```sql
ERASE student WHERE id=1
```

---

# 🔗 Foreign Key Support

## Parent Table

```sql
MAKE student (
    id INT PRIMARY KEY,
    name VARCHAR(50)
)
```

## Child Table

```sql
MAKE course (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(50),
    student_id INT,
    FOREIGN KEY (student_id) REFERENCES student(id)
)
```

---

# 🧱 Supported Constraints

## PRIMARY KEY

```sql
id INT PRIMARY KEY
```

* Must be unique
* Cannot contain duplicate values

---

## NOT NULL

```sql
name VARCHAR(50) NOT NULL
```

* Empty values are not allowed

---

## UNIQUE

```sql
email VARCHAR(100) UNIQUE
```

* Duplicate values are not allowed

---

## CHECK

```sql
marks INT CHECK(marks > 35)
```

* Value must satisfy the condition

---

## POSITIVE

```sql
salary FLOAT POSITIVE
```

* Value must be greater than zero

---

## FOREIGN KEY

```sql
FOREIGN KEY (student_id) REFERENCES student(id)
```

* Referenced value must exist in parent table
* Maintains referential integrity

---

# 🛡 Referential Integrity

The engine prevents:

## Deleting Referenced Parent Records

```sql
ERASE student WHERE id=1
```

Output:

```text
Cannot delete: record is referenced in another table
```

---

## Dropping Referenced Tables

```sql
REMOVE student
```

Output:

```text
Cannot remove table: referenced by 'course' table
```

---

# 📊 Supported Data Types

| Data Type  | Description              |
| ---------- | ------------------------ |
| INT        | Integer values           |
| FLOAT      | Floating point numbers   |
| DOUBLE     | Double precision numbers |
| VARCHAR(n) | Variable length string   |
| CHAR(n)    | Fixed length string      |
| BOOLEAN    | TRUE / FALSE             |
| DATE       | YYYY-MM-DD               |
| TIME       | HH:MM:SS                 |
| DATETIME   | YYYY-MM-DD HH:MM:SS      |

---

# ⚙️ How It Works

1. User enters a query.
2. Parser identifies the command and extracts metadata.
3. Execution engine validates constraints.
4. Data is stored in CSV files.
5. Schema information is stored in JSON.
6. Results are returned to the user.

---

# 🧪 Example Session

```sql
MAKE student (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
)

ADD student (1, Rahul)

SHOW student

CHANGE student SET name=Amit WHERE id=1

ERASE student WHERE id=1

REMOVE student
```

---

# 🧠 Future Improvements

* JOIN Queries
* ORDER BY
* GROUP BY
* Aggregate Functions
* Indexing Support
* Transactions
* User Authentication
* GUI Dashboard
* REST API Integration
* Query Optimization

---

# 🧑‍💻 Installation

Clone Repository:

```bash
git clone https://github.com/Dhanshri-Deshpande/Mini-SQL-Engine.git
```

Move into project:

```bash
cd Mini-SQL-Engine
```

Run:

```bash
python main.py
```

---

# 🎯 Educational Purpose

This project was developed to understand and implement fundamental DBMS concepts including query processing, schema management, constraint enforcement, and referential integrity without relying on existing database systems.

---

# 📄 License

This project is intended for educational and academic purposes.

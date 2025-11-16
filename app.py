from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import get_db

app = Flask(__name__)
app.secret_key = "your_secret_key"


# ------------------------- LOGIN PAGE -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == "admin@gmail.com" and password == "admin123":
            session["user"] = email
            return redirect("/")
        else:
            flash("Invalid login details!", "error")
            return redirect("/login")

    return render_template("login.html")


# ------------------------- LOGOUT -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------------------------- PROTECTED HOME PAGE -------------------------
@app.route("/")
def employees_list():

    if "user" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees ORDER BY id DESC")
    employees = cursor.fetchall()

    return render_template("employees.html", employees=employees)


# ------------------------- ADD EMPLOYEE -------------------------
@app.route("/add", methods=["GET", "POST"])
def add_employee():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        position = request.form["position"]
        salary = request.form["salary"]
        department = request.form["department"]

        db = get_db()
        cursor = db.cursor()

        # Check email exists
        cursor.execute("SELECT * FROM employees WHERE email=%s", (email,))
        if cursor.fetchone():
            flash("Email already exists!", "error")
            return redirect("/add")

        # Insert
        cursor.execute("""
            INSERT INTO employees (name,email,position,salary,department)
            VALUES (%s,%s,%s,%s,%s)
        """, (name, email, position, salary, department))

        db.commit()
        flash("Employee added successfully!", "success")
        return redirect("/")

    return render_template("add_employee.html")


# ------------------------- EDIT EMPLOYEE -------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "user" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    emp = cursor.fetchone()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        position = request.form["position"]
        salary = request.form["salary"]
        department = request.form["department"]

        # Check duplicate email
        cursor.execute("SELECT * FROM employees WHERE email=%s AND id!=%s", (email, id))
        if cursor.fetchone():
            flash("Email already exists!", "error")
            return redirect(f"/edit/{id}")

        cursor = db.cursor()
        cursor.execute("""
            UPDATE employees 
            SET name=%s, email=%s, position=%s, salary=%s, department=%s
            WHERE id=%s
        """, (name, email, position, salary, department, id))

        db.commit()
        flash("Employee updated!", "success")
        return redirect("/")

    return render_template("edit_employee.html", emp=emp)


# ------------------------- DELETE EMPLOYEE -------------------------
@app.route("/delete/<int:id>")
def delete_employee(id):

    if "user" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    db.commit()

    flash("Employee deleted!", "success")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

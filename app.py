from flask import Flask, request, redirect, session, send_from_directory, render_template_string
import mysql.connector
import os
from werkzeug.utils import secure_filename
from datetime import date

app = Flask(__name__)
app.secret_key = "shisha_placement_secret"

PROJECT_FOLDER = r"C:\SHISHA_PLACEMENT"
RESUME_FOLDER = os.path.join(PROJECT_FOLDER, "resumes")

os.makedirs(RESUME_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


# =========================
# DATABASE CONNECTION
# =========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="placement_management"
    )


# =========================
# CHECK FILE EXTENSION
# =========================
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# =========================
# LOGIN PAGE
# =========================
@app.route("/")
def home():
    return send_from_directory(
        PROJECT_FOLDER,
        "login.html"
    )


# =========================
# REGISTER PAGE
# =========================
@app.route("/register")
def register_page():
    return send_from_directory(
        PROJECT_FOLDER,
        "register.html"
    )


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    qualification = request.form["qualification"]
    phone = request.form["phone"]
    cgpa = request.form["cgpa"]
    skills = request.form["skills"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO students
            (name, email, password, department, phone, cgpa, skills)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            email,
            password,
            qualification,
            phone,
            cgpa,
            skills
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return """
        <script>
            alert("Registration successful! Please login.");
            window.location.href = "/";
        </script>
        """

    except mysql.connector.Error as error:

        cursor.close()
        conn.close()

        if error.errno == 1062:
            return """
            <script>
                alert("Email already registered. Please use another email.");
                window.location.href = "/register";
            </script>
            """

        return "Registration Error: " + str(error)


# =========================
# FORGOT PASSWORD PAGE
# =========================
@app.route("/forgot-password")
def forgot_password_page():
    return send_from_directory(
        PROJECT_FOLDER,
        "forgot_password.html"
    )


# =========================
# FORGOT PASSWORD
# =========================
@app.route("/forgot-password", methods=["POST"])
def forgot_password():

    email = request.form["email"]
    new_password = request.form["new_password"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM students WHERE email = %s",
        (email,)
    )

    student = cursor.fetchone()

    if student:

        cursor.execute(
            "UPDATE students SET password = %s WHERE email = %s",
            (new_password, email)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return """
        <script>
            alert("Password reset successful! Please login.");
            window.location.href = "/";
        </script>
        """

    else:

        cursor.close()
        conn.close()

        return """
        <script>
            alert("Email not registered.");
            window.location.href = "/forgot-password";
        </script>
        """


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM students
        WHERE email = %s AND password = %s
    """, (email, password))

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if student:

        session["student_id"] = student["id"]
        session["student_name"] = student["name"]
        session["student_email"] = student["email"]

        return redirect("/jobs")

    else:

        return """
        <script>
            alert("Invalid email or password.");
            window.location.href = "/";
        </script>
        """


# =========================
# JOBS PAGE
# =========================
@app.route("/jobs")
def jobs_page():

    if "student_id" not in session:
        return redirect("/")

    return send_from_directory(
        PROJECT_FOLDER,
        "jobs.html"
    )


# =========================
# JOB DETAILS
# =========================
@app.route("/job/<int:job_id>")
def job_details(job_id):

    if "student_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            jobs.*,
            companies.company_name,
            companies.location
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE jobs.id = %s
    """, (job_id,))

    job = cursor.fetchone()

    cursor.close()
    conn.close()

    if not job:

        return """
        <h2>Job not found</h2>
        <a href="/jobs">Back to Jobs</a>
        """

    with open(
        os.path.join(PROJECT_FOLDER, "job_details.html"),
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    return render_template_string(
        html,
        job=job
    )


# =========================
# APPLY PAGE
# =========================
@app.route("/apply/<int:job_id>")
def apply_page(job_id):

    if "student_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            jobs.*,
            companies.company_name,
            companies.location
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE jobs.id = %s
    """, (job_id,))

    job = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE id = %s
    """, (session["student_id"],))

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if not job:
        return """
        <h2>Job not found</h2>
        <a href="/jobs">Back to Jobs</a>
        """

    if not student:
        session.clear()
        return redirect("/")

    with open(
        os.path.join(PROJECT_FOLDER, "apply.html"),
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    return render_template_string(
        html,
        job=job,
        student=student
    )


# =========================
# SUBMIT APPLICATION
# =========================
@app.route("/apply/<int:job_id>", methods=["POST"])
def submit_application(job_id):

    if "student_id" not in session:
        return redirect("/")

    student_id = session["student_id"]

    resume = request.files.get("resume")

    if resume is None or resume.filename == "":
        return """
        <script>
            alert("Please upload your resume.");
            window.history.back();
        </script>
        """

    if not allowed_file(resume.filename):
        return """
        <script>
            alert("Only PDF, DOC and DOCX files are allowed.");
            window.history.back();
        </script>
        """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # Get job
        cursor.execute("""
            SELECT *
            FROM jobs
            WHERE id = %s
        """, (job_id,))

        job = cursor.fetchone()

        if not job:

            cursor.close()
            conn.close()

            return """
            <script>
                alert("Job not found.");
                window.location.href = "/jobs";
            </script>
            """


        # Get student
        cursor.execute("""
            SELECT *
            FROM students
            WHERE id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if not student:

            cursor.close()
            conn.close()

            session.clear()
            return redirect("/")


        # Check duplicate
        cursor.execute("""
            SELECT id
            FROM applications
            WHERE student_id = %s
            AND job_id = %s
        """, (student_id, job_id))

        existing_application = cursor.fetchone()

        if existing_application:

            cursor.close()
            conn.close()

            return """
            <script>
                alert("You have already applied for this job.");
                window.location.href = "/applications";
            </script>
            """


        # Check CGPA
        try:
            student_cgpa = float(student["cgpa"])
            required_cgpa = float(job["eligibility_cgpa"])
        except:
            student_cgpa = 0
            required_cgpa = 0

        if student_cgpa < required_cgpa:

            cursor.close()
            conn.close()

            return """
            <script>
                alert("Application Issue: Your CGPA does not meet the minimum eligibility requirement.");
                window.history.back();
            </script>
            """


        # Save resume
        original_filename = secure_filename(resume.filename)

        filename = (
            str(student_id)
            + "_"
            + str(job_id)
            + "_"
            + original_filename
        )

        resume_path = os.path.join(
            RESUME_FOLDER,
            filename
        )

        resume.save(resume_path)


        # Check resume column
        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'placement_management'
            AND TABLE_NAME = 'applications'
            AND COLUMN_NAME = 'resume_filename'
        """)

        column_check = cursor.fetchone()

        if column_check["count"] == 0:

            cursor.execute("""
                ALTER TABLE applications
                ADD COLUMN resume_filename VARCHAR(255)
            """)

            conn.commit()


        # Insert application
        cursor.execute("""
            INSERT INTO applications
            (student_id, job_id, applied_date, status, resume_filename)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            student_id,
            job_id,
            date.today(),
            "Applied",
            filename
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return """
        <script>
            alert("Application submitted successfully!");
            window.location.href = "/applications";
        </script>
        """


    except mysql.connector.Error as error:

        conn.rollback()

        cursor.close()
        conn.close()

        return """
        <h2>Application Issue</h2>
        <p>Unable to submit your application.</p>
        <p>Please try again.</p>
        <br>
        <a href="/jobs">Back to Jobs</a>
        """


# =========================
# MY APPLICATIONS
# =========================
@app.route("/applications")
def applications_page():

    if "student_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            applications.id,
            applications.applied_date,
            applications.status,
            applications.resume_filename,

            jobs.job_title,

            companies.company_name,
            companies.location,

            students.name AS student_name,
            students.email,
            students.cgpa

        FROM applications

        JOIN jobs
            ON applications.job_id = jobs.id

        JOIN companies
            ON jobs.company_id = companies.id

        JOIN students
            ON applications.student_id = students.id

        WHERE applications.student_id = %s

        ORDER BY applications.id DESC
    """, (session["student_id"],))

    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    with open(
        os.path.join(PROJECT_FOLDER, "applications.html"),
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    return render_template_string(
        html,
        applications=applications
    )


# =========================
# VIEW RESUME
# =========================
@app.route("/resume/<filename>")
def view_resume(filename):

    if "student_id" not in session:
        return redirect("/")

    filename = secure_filename(filename)

    if not filename:
        return "Invalid resume."

    return send_from_directory(
        RESUME_FOLDER,
        filename
    )


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# RUN APPLICATION
# =========================
if __name__ == "__main__":
    app.run(debug=True)
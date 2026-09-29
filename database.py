import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = conn.cursor()

# Create database
cursor.execute("""
CREATE DATABASE IF NOT EXISTS placement_management
""")

# Select database
cursor.execute("""
USE placement_management
""")


# ==========================================
# Create Students Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    phone VARCHAR(15),
    cgpa FLOAT,
    skills TEXT
)
""")


# ==========================================
# Create Companies Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    location VARCHAR(100),
    description TEXT
)
""")


# ==========================================
# Create Jobs Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT,
    job_title VARCHAR(150) NOT NULL,
    salary VARCHAR(50),
    eligibility_cgpa FLOAT,
    skills_required TEXT,
    drive_date DATE,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
""")


# ==========================================
# Create Applications Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    job_id INT,
    applied_date DATE,
    status VARCHAR(50) DEFAULT 'Applied',
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
)
""")


# ==========================================
# Remove Old Job/Application Data
# ==========================================

cursor.execute("""
DELETE FROM applications
""")

cursor.execute("""
DELETE FROM jobs
""")

cursor.execute("""
DELETE FROM companies
""")


# ==========================================
# Add Company
# ==========================================

cursor.execute("""
INSERT INTO companies
(company_name, location, description)
VALUES
(
    'SHISHA GRAPHIC DESIGN',
    'Chennai',
    'Graphic design and digital creative services company'
)
""")

company_id = cursor.lastrowid


# ==========================================
# Add 6 Job Vacancies
# ==========================================

jobs = [

    (
        "Graphic Designer",
        "₹20,000 - ₹30,000/month",
        6.5,
        "Photoshop, Illustrator, Canva",
        "2026-10-10"
    ),

    (
        "Web Developer",
        "₹25,000 - ₹40,000/month",
        7.0,
        "HTML, CSS, JavaScript, Python",
        "2026-10-15"
    ),

    (
        "Python Developer",
        "₹28,000 - ₹45,000/month",
        7.0,
        "Python, Flask, MySQL",
        "2026-10-20"
    ),

    (
        "UI/UX Designer",
        "₹22,000 - ₹35,000/month",
        6.5,
        "Figma, Photoshop, UI Design",
        "2026-10-25"
    ),

    (
        "Software Developer",
        "₹30,000 - ₹50,000/month",
        7.5,
        "Python, Java, MySQL",
        "2026-10-30"
    ),

    (
        "Frontend Developer",
        "₹24,000 - ₹38,000/month",
        6.5,
        "HTML, CSS, JavaScript, Bootstrap",
        "2026-11-05"
    )

]


for job in jobs:

    cursor.execute("""
    INSERT INTO jobs
    (
        company_id,
        job_title,
        salary,
        eligibility_cgpa,
        skills_required,
        drive_date
    )
    VALUES
    (%s, %s, %s, %s, %s, %s)
    """,
    (
        company_id,
        job[0],
        job[1],
        job[2],
        job[3],
        job[4]
    ))


# Save changes
conn.commit()

cursor.close()
conn.close()


print("====================================")
print("Database setup completed successfully!")
print("Company added: SHISHA GRAPHIC DESIGN")
print("6 job vacancies added successfully!")
print("====================================")
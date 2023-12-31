import mysql.connector
# Avoid hardcoding sensitive info
def setup_database():
    connector = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
    )
    cursor = connector.cursor(buffered=True)
    cursor.execute("CREATE DATABASE IF NOT EXISTS jobjet")
    cursor.execute("USE jobjet")
    # Use lowercase and underscores for table and column names
    cursor.execute("""CREATE TABLE IF NOT EXISTS job_seekers(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(80) NOT NULL,
                    email VARCHAR(50) NOT NULL,
                    description TEXT,
                    skills VARCHAR(255) NOT NULL,
                    password VARCHAR(50) NOT NULL,
                    status TEXT);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS employers(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    email VARCHAR(50) NOT NULL,
                    password VARCHAR(50) NOT NULL,
                    applicants_id VARCHAR(80));""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS jobs(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                       title VARCHAR(40),
                       skills VARCHAR(255),
                       description TEXT,
                       employer_id INT);""")

    return connector, cursor

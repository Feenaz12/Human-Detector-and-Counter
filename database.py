from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

class Database:
    def __init__(self, host="localhost", user="root", password="Feenaz@123", database="human_detection"):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("Database connected successfully!")
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None
            self.cursor = None

    # ---------------- UTILITY ----------------
    def is_connected(self):
        return self.connection is not None and self.cursor is not None

    # ---------------- USER FUNCTIONS ----------------
    def create_user(self, name, email, password):
        if not self.is_connected():
            print("Database not connected!")
            return False
        hashed_password = generate_password_hash(password)
        try:
            sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (name, email, hashed_password))
            self.connection.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error creating user: {e}")
            return False

    def get_user_by_email(self, email):
        if not self.is_connected():
            print("Database not connected!")
            return None
        try:
            sql = "SELECT * FROM users WHERE email = %s"
            self.cursor.execute(sql, (email,))
            return self.cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Error fetching user: {e}")
            return None

    def verify_user(self, email, password):
        user = self.get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    # ---------------- RESULTS FUNCTIONS ----------------
    def insert_result(self, user_id, file_name, result_image, human_count):
        if not self.is_connected():
            print("Database not connected!")
            return False
        try:
            sql = """
                INSERT INTO results (user_id, file_name, result_image, human_count)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql, (user_id, file_name, result_image, human_count))
            self.connection.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error inserting result: {e}")
            return False

    def fetch_user_results(self, user_id):
        if not self.is_connected():
            print("Database not connected!")
            return []
        try:
            sql = "SELECT * FROM results WHERE user_id = %s ORDER BY uploaded_at DESC"
            self.cursor.execute(sql, (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching results: {e}")
            return []

    # ---------------- CLOSE CONNECTION ----------------
    def close(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            self.connection = None
            self.cursor = None
            print("Database connection closed.")

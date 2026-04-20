import MySQLdb

def get_db_connection():
    """Create and return a database connection"""
    connection = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='your_password',  # Change this to your MySQL password
        db='fashion_mart',
        autocommit=True,
        charset='utf8mb4'
    )
    return connection

def init_db():
    """Initialize the database with schema"""
    try:
        # Read and execute schema file
        with open('database/schema.sql', 'r') as f:
            sql_script = f.read()
        
        # Split by semicolons and execute each statement
        connection = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='your_password',  # Change this to your MySQL password
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # Execute each SQL statement
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == '__main__':
    init_db()

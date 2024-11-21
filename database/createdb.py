import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connection = pymysql.connect(
        host = os.getenv('DB_HOST'),
        user = os.getenv('DB_USR'),
        password = os.getenv('DB_PWD'),
    )
    print("MySQL에 성공적으로 연결되었습니다.")

    cursor = connection.cursor()
    
    drop_db_query = "DROP DATABASE FAIRYTALE;"
    cursor.execute(drop_db_query)

    create_db_query = "CREATE DATABASE IF NOT EXISTS FAIRYTALE;"
    cursor.execute(create_db_query)
    #print("데이터베이스 'FAIRYTALE'가 생성되었습니다.")

except pymysql.MySQLError as e:
    print(f"오류 발생: {e}")

finally:
    if 'connection' in locals() and connection.open:
        cursor.close()
        connection.close()
        print("MySQL 연결이 종료되었습니다.")

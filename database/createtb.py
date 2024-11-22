import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


create_user_table = """
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL
);
"""

create_story_table = """
CREATE TABLE IF NOT EXISTS story (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    `character` VARCHAR(255) NOT NULL,
    background VARCHAR(255) NOT NULL,
    `end` BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE (user_id, title)
);
"""

create_storybook_query = """
CREATE TABLE IF NOT EXISTS page (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    story_id INT NOT NULL,
    pagenum INT NOT NULL,
    context TEXT NOT NULL,
    image VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (story_id) REFERENCES story(id) ON DELETE CASCADE,
    UNIQUE (story_id, pagenum)
);
"""

try:
    connection = pymysql.connect(
        host = os.getenv('DB_HOST'),
        user = os.getenv('DB_USR'),
        password = os.getenv('DB_PWD'),
        database = os.getenv('DB_NAME')
    )
    print(f"'{os.getenv('DB_NAME')}' 데이터베이스에 연결되었습니다.")

    cursor = connection.cursor()

    cursor.execute(create_user_table)
    cursor.execute(create_story_table)
    cursor.execute(create_storybook_query)
    #print("테이블 'storybook'이 성공적으로 생성되었습니다.")

except pymysql.MySQLError as e:
    print(f"오류 발생: {e}")

finally:
    if 'connection' in locals() and connection.open:
        cursor.close()
        connection.close()
        print("MySQL 연결이 종료되었습니다.")

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import config as CONFIG

app = Flask(__name__)
CORS(app)

@app.route("/user", methods=['GET'])
def user_check():
    user = request.args.get('user')
    key = request.args.get('key')
    if key == CONFIG.KEY['login_key']:
        # 받은 데이터 print
        print(f"사용자: {user}, 키: {key}")
        
        try:
            connection = pymysql.connect(
                host=CONFIG.DB['host'],
                user=CONFIG.DB['usr'],
                password=CONFIG.DB['pwd'],
                database=CONFIG.DB['db']
            )
            print("MySQL에 성공적으로 연결되었습니다.")

            cursor = connection.cursor()

            # user 있는지 확인
            cursor.execute("SELECT * FROM user WHERE username = %s", (user,))
            result = cursor.fetchone()
            
            # user가 없다면 추가
            if result is None:
                print(f"사용자 '{user}'이(가) 존재하지 않습니다. 새로운 사용자 추가 중...")
                cursor.execute("INSERT INTO user (username) VALUES (%s)", (user,))
                connection.commit()
                print(f"사용자 '{user}'이(가) 추가되었습니다.")
                
                return jsonify({'result':'success', 'msg': f"새 사용자 '{user}'이(가) 추가되었습니다."})
            # 있다면 동화책 정보 return
            else:
                print(f"사용자 '{user}'이(가) 이미 존재합니다.")
                
                user_id = result[0]
                
                # story 테이블에서 user의 데이터를 조회
                cursor.execute("SELECT id, title, topic, `character`, background FROM story WHERE user_id = %s", (user_id,))
                stories = cursor.fetchall()
                
                if not stories:
                    stories_list = []
                    return jsonify({'result':'success', 'msg': stories_list})
                
                # story 데이터를 JSON으로 반환
                stories_list = []
                for story in stories:
                    story_dict = {
                        'id': story[0],
                        'title': story[1],
                        'topic': story[2],
                        'character': story[3],
                        'background': story[4],
                    }
                    stories_list.append(story_dict)

                return jsonify({'result':'success', 'msg': stories_list})

        except pymysql.MySQLError as e:
            print(f"오류 발생: {e}")
            return jsonify({'result': 'error', 'msg': '데이터베이스 오류 발생!'})

        finally:
            if 'connection' in locals() and connection.open:
                cursor.close()
                connection.close()
                print("MySQL 연결이 종료되었습니다.")

    else:
        return jsonify({'result':'error', 'msg': '키 값이 틀립니다!'})
    
if __name__ == '__main__':
    ssl_key = (CONFIG.URL['ssl_fullchain'], CONFIG.URL['ssl_privkey'])
    app.run('0.0.0.0', port=1222, ssl_context=ssl_key, debug=True)
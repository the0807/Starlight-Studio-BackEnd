from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import config as CONFIG
from gen.gen_text import gen_gemini

app = Flask(__name__)
CORS(app)

# DB setting
def get_db_connection():
    return pymysql.connect(
        host = CONFIG.DB['host'],
        user = CONFIG.DB['usr'],
        password = CONFIG.DB['pwd'],
        database = CONFIG.DB['db']
    )

# fetchone
def fetch_one(query, params):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    except pymysql.MySQLError as e:
        print(f"오류 발생: {e}")
        return f"ERROR: {e}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# fetchall 
def fetch_all(query, params):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"오류 발생: {e}")
        return f"ERROR: {e}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# query
def execute_query(query, params, fetch_last_id=False):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
            return cursor.lastrowid if fetch_last_id else None
    except pymysql.MySQLError as e:
        print(f"오류 발생: {e}")
        return f"ERROR: {e}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# login
@app.route("/user", methods=['POST'])
def user_check():
    user = request.args.get('user')
    key = request.args.get('key')

    if key != CONFIG.KEY['login_key']:
        return jsonify({'result': 'error', 'msg': '키 값을 다시 확인해주세요!', 'data': ''})
    else:
        # user가 있는지 검색
        user_result = fetch_one("SELECT * FROM user WHERE username = %s", (user,))
        
        if user_result is None:
            print(f"사용자 '{user}'이(가) 존재하지 않습니다. 새로운 사용자 추가 중...")
            
            # user INSERT
            string = execute_query("INSERT INTO user (username) VALUES (%s)", (user,))
            
            if string is not None and "ERROR" in str(string):
                return jsonify({'result': 'error', 'msg': string, 'data': ''})
        
            print(f"사용자 '{user}'이(가) 추가되었습니다.")

            return jsonify({'result': 'success', 'msg': f"새 사용자 '{user}'이(가) 추가되었습니다.", 'data': ''})
        elif user_result is not None and "ERROR" in str(user_result):
            return jsonify({'result': 'error', 'msg': user_result, 'data': ''})
        else:
            print(f"사용자 '{user}'이(가) 로그인했습니다.")
            user_id = user_result[0]

            # story 테이블에서 user_id로 SELECT
            stories = fetch_all(
                "SELECT id, title, topic, `character`, background FROM story WHERE user_id = %s", 
                (user_id,)
            )
            
            if stories is not None and "ERROR" in str(stories):
                return jsonify({'result': 'error', 'msg': stories, 'data': ''})

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

            msg = '저장된 동화를 불러왔습니다!' if stories_list else '저장된 동화가 없습니다!'
            return jsonify({'result': 'success', 'msg': msg, 'data': stories_list})

# getstory
@app.route("/getstory", methods=['POST'])
def get_story():
    title = request.args.get('title')
    username = request.args.get('user')
    
    # username으로 user 테이블에서 user_id SELECT
    user_result = fetch_one("SELECT id FROM user WHERE username = %s", (username,))
    if not user_result:
        return jsonify({'result': 'error', 'msg': '사용자가 존재하지 않습니다.', 'data': ''})
    elif user_result is not None and "ERROR" in str(user_result):
            return jsonify({'result': 'error', 'msg': user_result, 'data': ''})
    
    user_id = user_result[0]
    
    # user_id와 title로 story 테이블에서 story_id SELECT
    story_result = fetch_one("SELECT id FROM story WHERE user_id = %s AND title = %s", (user_id, title,))
    if not story_result:
        return jsonify({'result': 'error', 'msg': '동화가 존재하지 않습니다.', 'data': ''})
    elif story_result is not None and "ERROR" in str(story_result):
        return jsonify({'result': 'error', 'msg': story_result, 'data': ''})
    else:
        story_id = story_result[0]
        
        # user_id와 story_id로 page 테이블에서 * SELECT
        page_result = fetch_all("SELECT * FROM page WHERE user_id = %s AND story_id = %s", (user_id, story_id,))
        
        if page_result is not None and "ERROR" in str(page_result):
            return jsonify({'result': 'error', 'msg': page_result, 'data': ''})
        
        # page 데이터를 JSON으로
        pages_list = []
        for page in page_result:
            page_dict = {
                'id': page[0],
                'user_id': page[1],
                'story_id': page[2],
                'pagenum': page[3],
                'context': page[4],
                'image': page[5],
            }
            pages_list.append(page_dict)

        msg = '저장된 동화를 불러왔습니다!' if pages_list else '저장된 동화가 없습니다!'
        return jsonify({'result': 'success', 'msg': msg, 'data': pages_list})

# new story
@app.route("/newstory", methods=['POST'])
def new_story():
    title = request.args.get('title')
    topic = request.args.get('topic')
    character = request.args.get('character')
    background = request.args.get('background')
    username = request.args.get('user')

    num = 1
    context = ''
    renew = False
    before = ''
    page1 = gen_gemini(num, topic, character, background, context, renew, before)

    if page1.startswith('[시스템]'):
        return jsonify({'result': 'error', 'msg': '동화와 관련된 이야기를 작성해주세요!', 'data': ''})

    # username으로 user 테이블에서 user_id SELECT
    user_result = fetch_one("SELECT id FROM user WHERE username = %s", (username,))
    if not user_result:
        return jsonify({'result': 'error', 'msg': '사용자가 존재하지 않습니다.', 'data': ''})
    elif user_result is not None and "ERROR" in str(user_result):
            return jsonify({'result': 'error', 'msg': user_result, 'data': ''})
    
    user_id = user_result[0]

    # story 테이블에 INSERT
    story_id = execute_query(
        "INSERT INTO story (user_id, title, topic, `character`, background) VALUES (%s, %s, %s, %s, %s)", 
        (user_id, title, topic, character, background), 
        fetch_last_id=True
    )
    
    if story_id is not None and "ERROR" in str(story_id):
        return jsonify({'result': 'error', 'msg': story_id, 'data': ''})
    
    # page 테이블에 INSERT
    string = execute_query(
        "INSERT INTO page (user_id, story_id, pagenum, context) VALUES (%s, %s, %s, %s)",
        (user_id, story_id, 1, page1)
    )
    
    if string is not None and "ERROR" in str(string):
        return jsonify({'result': 'error', 'msg': string, 'data': ''})

    print("새로운 이야기가 성공적으로 저장되었습니다.")
    return jsonify({'result': 'success', 'msg': '새로운 이야기가 성공적으로 저장되었습니다!', 'data': page1})

# next story
@app.route("/nextstory", methods=['POST'])
def next_story():
    story_id = request.args.get('story_id')
    username = request.args.get('user')
    nextpage = request.args.get('page')
    context = request.args.get('context')
    
    # username으로 user 테이블에서 user_id SELECT
    user_result = fetch_one("SELECT id FROM user WHERE username = %s", (username,))
    if not user_result:
        return jsonify({'result': 'error', 'msg': '사용자가 존재하지 않습니다.', 'data': ''})
    elif user_result is not None and "ERROR" in str(user_result):
            return jsonify({'result': 'error', 'msg': user_result, 'data': ''})
    
    user_id = user_result[0]
    
    # story 테이블에서 user_id로 SELECT
    story = fetch_one(
        "SELECT title, topic, `character`, background FROM story WHERE id = %s AND user_id = %s", 
        (story_id, user_id,)
    )

    if story is not None and "ERROR" in str(story):
        return jsonify({'result': 'error', 'msg': story, 'data': ''})
    
    title = story[0]
    topic = story[1]
    character = story[2]
    background = story[3]
    
    renew = False
    before = ''
    gen_context = gen_gemini(nextpage, topic, character, background, context, renew, before)

    if gen_context.startswith('[시스템]'):
        return jsonify({'result': 'error', 'msg': '동화와 관련된 이야기를 작성해주세요!', 'data': ''})
    
    # page 테이블에 context와 정보들 INSERT
    string = execute_query(
        "INSERT INTO page (user_id, story_id, pagenum, context) VALUES (%s, %s, %s, %s)",
        (user_id, story_id, nextpage, gen_context)
    )
    
    if string is not None and "ERROR" in str(string):
        return jsonify({'result': 'error', 'msg': string, 'data': ''})

    print("새로운 이야기가 성공적으로 저장되었습니다.")
    return jsonify({'result': 'success', 'msg': '새로운 이야기가 성공적으로 저장되었습니다!', 'data': gen_context})

# regenerate story
@app.route("/regenstory", methods=['POST'])
def regen_story():
    story_id = request.args.get('story_id')
    username = request.args.get('user')
    page = request.args.get('page')
    context = request.args.get('context')
    r_context = request.args.get('r_context')
    
    # username으로 user 테이블에서 user_id SELECT
    user_result = fetch_one("SELECT id FROM user WHERE username = %s", (username,))
    if not user_result:
        return jsonify({'result': 'error', 'msg': '사용자가 존재하지 않습니다.', 'data': ''})
    elif user_result is not None and "ERROR" in str(user_result):
            return jsonify({'result': 'error', 'msg': user_result, 'data': ''})
    
    user_id = user_result[0]
    
    # story 테이블에서 user_id로 SELECT
    story = fetch_one(
        "SELECT title, topic, `character`, background FROM story WHERE id = %s AND user_id = %s", 
        (story_id, user_id,)
    )

    if story is not None and "ERROR" in str(story):
        return jsonify({'result': 'error', 'msg': story, 'data': ''})
    
    title = story[0]
    topic = story[1]
    character = story[2]
    background = story[3]
    
    renew = True
    gen_context = gen_gemini(page, topic, character, background, context, renew, r_context)

    if gen_context.startswith('[시스템]'):
        return jsonify({'result': 'error', 'msg': '동화와 관련된 이야기를 작성해주세요!', 'data': ''})
    
    # page 테이블에서 user_id, story_id, pagenum에 해당하는 context UPDATE
    string = execute_query(
        "UPDATE page SET context = %s WHERE user_id = %s AND story_id = %s AND pagenum = %s",
        (gen_context, user_id, story_id, page)
    )
    
    if string is not None and "ERROR" in str(string):
        return jsonify({'result': 'error', 'msg': string, 'data': ''})

    print("재생성된 이야기가 성공적으로 저장되었습니다.")
    return jsonify({'result': 'success', 'msg': '재생성된 이야기가 성공적으로 저장되었습니다!', 'data': gen_context})

if __name__ == '__main__':
    ssl_key = (CONFIG.URL['ssl_fullchain'], CONFIG.URL['ssl_privkey'])
    app.run('0.0.0.0', port=1222, ssl_context=ssl_key, debug=True)

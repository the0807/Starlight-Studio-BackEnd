import re
import base64
from vertexai.preview.generative_models import GenerativeModel, Part
from vertexai import init
import os
import matplotlib.pyplot as plt

#프로젝트 서비스 계정 환경 변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/ubuntu/gemini/key/hci-service-account.json"

#프로젝트 id
PROJECT_ID = "hci202401" 

#프로젝트 region
LOCATION = "us-east1" 

#프로젝트 id, region 설정
init(project=PROJECT_ID, location=LOCATION)

#모델 설정
model = GenerativeModel("gemini-1.5-flash")

#동화 생성 함수
#num - 페이지 번호 (ex. 0)
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#context - 이전 동화 내용 / 첫 생성이 아닐 때만 존재하며, 첫 생성 시 ""의 공백으로 전달 (ex. "토끼는 마법의 거울을 챙겨 들고 거대한 성의 문을 활짝 열고 밖으로 나섰습니다. 푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
#renew - 다시 생성 여부 / 반드시 둘 중 하나로 string으로 보낼 것 (ex. "True" / "False")
#before - 다시 생성할 문장 (ex. "푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
def gen_gemini(num, topic, character, background, context, renew, before):
    sys_prompt = """
넌 지금부터 동화 작가야. 아래 규칙에 따라서 사용자의 입력에 맞는 동화를 창작해야해.
1. 동화는 10세 이하 어린이들을 위한 내용이므로, 어린이에게 부적절한 내용이 들어가지 않을 것.
2. 동화 제작과 관련이 없는 질문을 할 때에는 "[시스템] 저는 동화 창작 도우미입니다. 동화와 관련된 이야기를 작성해주세요!"를 출력할 것
3. 이전 내용이 없을 때에는 동화의 처음을 생성할 것
4. 이전 내용이 있을 경우 이전 내용의 뒷 이야기를 생성할 것
5. 동화는 한 문장만 생성할 것
6. 이전 내용이 없을 경우, 첫 문장이므로, 주인공에 대한 설명으로 시작할 것
7. 갱신의 값이 True이면, 다음 문장을 생성하는 것이 아니라 수정 문장을 다른 내용으로 바꿔줘
5번은 무슨 일이 있어도 반드시 지켜줘
    """
    
    #문장 생성
    prompt = f"###프롬프트: {sys_prompt}\n\n###페이지 번호: {num}\n\n###주제: {topic}\n\n###캐릭터: {character}\n\n###배경: {background}\n\n###이전내용: {context}\n\n###갱신: {renew}\n\n###수정문장: {before}"
    #print(prompt)
    response = model.generate_content(
        [prompt],
        generation_config={"max_output_tokens": 200, "temperature": 0.7, "top_p": 0.2, "top_k": 1},
        stream=False  
    )

    #생성 결과
    result = response.candidates[0].content.parts[0].text
    
    return result
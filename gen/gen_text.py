import re
import base64
from vertexai.preview.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold, SafetySetting
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
def gen_gemini(num, topic, character, background, context):
    sys_prompt = """
넌 지금부터 동화 작가야. 아래는 동화를 생성할 때 지켜야 하는 규칙이야.
1. 동화는 10세 이하 어린이들을 위한 내용이므로, 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 내용이 들어가지 않을 것.
2. 동화 제작과 관련이 없는 질문을 할 때에는 "[시스템] 저는 동화 창작 도우미입니다. 동화와 관련된 이야기를 작성해주세요!"를 출력할 것
3. 이전 내용이 없을 때에는 동화의 첫 문장을 생성해야 하며, 주인공에 대한 설명으로 시작할 것
4. 이전 내용이 있을 경우 이전 내용의 뒷 이야기를 생성할 것
5. 한 문장은 "안녕하세요."와 같으며,  동화는 한 문장만 생성할 것
6. 새로 생성하는 문장은 수정 문장과 다른 문장이어야 하며, 이전 내용이 포함되지 않을 것
7. "연필이 부러졌어요. '다른 내용 만들어줘요' 버튼을 눌러 새로운 연필을 주세요!"라는 내용이 있으면, 계속 동화를 생성할 것
페이지 번호에 해당하는 내용을 만드는 건데, 주제, 캐릭터, 배경, 이전 내용을 참고해서 동화의 다음 내용을 한 줄 생성해줘.
    """
    
    #문장 생성
    prompt = f"###프롬프트: {sys_prompt}\n\n###페이지 번호: {num}\n\n###주제: {topic}\n\n##캐릭터: {character}\n\n##배경: {background}\n\n###이전내용: {context}"
    #print(prompt)

    #괴롭힘 기준점 조정   
    safety_settings = [
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
    ]

    #답변 생성
    response = model.generate_content(
        [prompt],
        generation_config={"max_output_tokens": 200, "temperature": 2, "top_p": 0.2, "top_k": 1},
        stream=False,
        safety_settings=safety_settings,
    )

    #검열 상태
    block_status = str(response.candidates[0].finish_reason)
    
    #출력 문장 결과 저장
    if block_status == "FinishReason.STOP": #검열 안 당했으면 생성 문장 저장
        result = response.candidates[0].content.parts[0].text

    else: #검열 당했을 때
        result = "연필이 부러졌어요. '다른 내용 만들어줘요' 버튼을 눌러 새로운 연필을 주세요!"
    
    return result

#동화 문장 수정 함수
#num - 페이지 번호 (ex. 0)
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#context - 이전 동화 내용 / 첫 생성이 아닐 때만 존재하며, 첫 생성 시 ""의 공백으로 전달 (ex. "토끼는 마법의 거울을 챙겨 들고 거대한 성의 문을 활짝 열고 밖으로 나섰습니다. 푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
#before - 다시 생성하고 싶은 문장 (ex. "푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
def gen_gemini_renew(num, topic, character, background, context, before):
    sys_prompt = """
넌 지금부터 동화 작가야. 아래는 동화를 생성할 때 지켜야 하는 규칙이야.
1. 동화는 10세 이하 어린이들을 위한 내용이므로, 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 내용이 들어가지 않을 것.
2. 동화 제작과 관련이 없는 질문을 할 때에는 "[시스템] 저는 동화 창작 도우미입니다. 동화와 관련된 이야기를 작성해주세요!"를 출력할 것
3. 이전 내용을 참고해서 동화의 뒷 이야기를 만들 것
4. 한 문장은 "안녕하세요."와 같으며,  동화는 한 문장만 생성할 것
5. "연필이 부러졌어요. '다른 내용 만들어줘요' 버튼을 눌러 새로운 연필을 주세요!"라는 내용이 있으면, 계속 동화를 생성할 것
페이지 번호에 해당하는 내용을 만드는 건데, 수정 문장을 내가 만든 페이지 내용이야. 너는 주제, 캐릭터, 배경, 이전 내용을 참고해서 수정 문장과 다른 내용으로 동화 내용을 생성해줘.
    """
    
    #문장 생성
    prompt = f"###프롬프트: {sys_prompt}\n###페이지 번호: {num}\n\n###주제: {topic}\n\n###캐릭터: {character}\n\n###배경: {background}\n\n###이전내용: {context}\n\n###수정문장: {before}"
    #print(prompt)
    
    #괴롭힘 기준점 조정   
    safety_settings = [
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
    ]

    #답변 생성
    response = model.generate_content(
        [prompt],
        generation_config={"max_output_tokens": 200, "temperature": 2, "top_p": 0.2, "top_k": 1},
        stream=False,
        safety_settings=safety_settings,
    )

    #검열 상태
    block_status = str(response.candidates[0].finish_reason)
    
    #출력 문장 결과 저장
    if block_status == "FinishReason.STOP": #검열 안 당했으면 생성 문장 저장
        result = response.candidates[0].content.parts[0].text

    else: #검열 당했을 때
        result = "연필이 부러졌어요. '다른 내용 만들어줘요' 버튼을 눌러 새로운 연필을 주세요!"
    
    return result

#동화 문장 요청사항 적용 함수
#num - 페이지 번호 (ex. 0)
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#context - 이전 동화 내용 / 첫 생성이 아닐 때만 존재하며, 첫 생성 시 ""의 공백으로 전달 (ex. "토끼는 마법의 거울을 챙겨 들고 거대한 성의 문을 활짝 열고 밖으로 나섰습니다. 푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
#request_text - 요청사항 (ex. "갑자기 마법의 거울이 말을 걸고 시냇물을 마시라고 했으면 좋겠어")
def gen_gemini_update(num, topic, character, background, context, request_text):
    sys_prompt = """
넌 지금부터 동화 작가야. 아래는 동화를 생성할 때 지켜야 하는 규칙이야.
1. 동화는 10세 이하 어린이들을 위한 내용이므로, 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 내용이 들어가지 않을 것.
2. 동화 제작과 관련이 없는 질문을 할 때에는 "[시스템] 저는 동화 창작 도우미입니다. 동화와 관련된 이야기를 작성해주세요!"를 출력할 것
3. 이전 내용을 참고해서 동화의 뒷 이야기를 만들 것
4. 한 문장은 "안녕하세요."와 같으며,  동화는 한 문장만 생성할 것
5. "연필이 부러졌어요. '다른 내용 만들어줘요' 버튼을 눌러 새로운 연필을 주세요!"라는 내용이 있으면, 계속 동화를 생성할 것
페이지 번호에 해당하는 내용을 만드는 건데, 수정 문장을 내가 만든 페이지 내용인데, 문장을 수정하고 싶어.
너는 주제, 캐릭터, 배경, 이전 내용을 참고해서 다음 동화 내용을 만들면 되는데, 참고내용을 적용해서 만들어줘.
    """
    
    #문장 생성
    prompt = f"###프롬프트: {sys_prompt}\n###페이지 번호: {num}\n\n###주제: {topic}\n\n###캐릭터: {character}\n\n###배경: {background}\n\n###이전내용: {context}\n\n###참고내용: {request_text}"
    #print(prompt)
    
    #괴롭힘 기준점 조정   
    safety_settings = [
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
    ]

    #답변 생성
    response = model.generate_content(
        [prompt],
        generation_config={"max_output_tokens": 200, "temperature": 2, "top_p": 0.2, "top_k": 1},
        stream=False,
        safety_settings=safety_settings,
    )

    #검열 상태
    block_status = str(response.candidates[0].finish_reason)
    
    #출력 문장 결과 저장
    if block_status == "FinishReason.STOP": #검열 안 당했으면 생성 문장 저장
        result = response.candidates[0].content.parts[0].text

    else: #검열 당했을 때
        result = "연필이 부러졌어요. '다른 내용 만들어줘요' 버튼을 눌러 새로운 연필을 주세요!"
    
    return result
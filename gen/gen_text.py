from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
load_dotenv()

#모델 설정
model = ChatOpenAI(model="gpt-4o-mini", temperature = 0.9)

#동화 생성 함수
#num - 페이지 번호 (ex. 0)
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#context - 이전 동화 내용 / 첫 생성이 아닐 때만 존재하며, 첫 생성 시 ""의 공백으로 전달 (ex. "토끼는 마법의 거울을 챙겨 들고 거대한 성의 문을 활짝 열고 밖으로 나섰습니다. 푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
def gen_text(num, topic, character, background, context):
    #sys prompt 지정
    sys_prompt = """###시스템 프롬프트:
넌 지금부터 동화 작가야. 아래는 동화를 생성할 때 지켜야 하는 규칙이야.
1. 동화는 10세 이하 어린이들을 위한 내용이므로, 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 내용이 들어가지 않을 것.
2. 동화 제작과 관련이 없는 질문을 할 때에는 "[시스템] 저는 동화 창작 도우미입니다. 동화와 관련된 이야기를 작성해주세요!"를 출력할 것
3. 이전 내용이 없을 때에는 동화의 첫 문장을 생성해야 하며, 주인공에 대한 설명으로 시작할 것
4. 이전 내용이 있을 경우 이전 내용의 뒷 이야기를 생성할 것
5. 한 문장은 "안녕하세요."와 같으며,  동화는 한 문장만 생성할 것
6. 새로 생성하는 문장은 수정 문장과 다른 문장이어야 하며, 이전 내용이 포함되지 않을 것
7. 이전 내용과 중복되지 않도록 다음 동화 내용을 생성할 것
    """
    
    #input 지정
    prompt = f"###페이지 번호: {num}\n\n###주제: {topic}\n\n##캐릭터: {character}\n\n##배경: {background}\n\n###이전내용: {context}\n\n"
    prompt += "###사용자 입력: 페이지 번호에 해당하는 내용을 만드는 건데, 주제, 캐릭터, 배경, 이전 내용을 참고해서 동화 내용을 한 줄 생성해줘."
    
    #messages 구성
    messages = [
        SystemMessage(content = sys_prompt),
        HumanMessage(content = prompt),
    ]
    
    #문장 생성
    result = model.invoke(messages).content 
    result += "\n"
    
    return result

#동화 문장 수정 함수
#num - 페이지 번호 (ex. 0)
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#context - 이전 동화 내용 / 첫 생성이 아닐 때만 존재하며, 첫 생성 시 ""의 공백으로 전달 (ex. "토끼는 마법의 거울을 챙겨 들고 거대한 성의 문을 활짝 열고 밖으로 나섰습니다. 푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
#before - 다시 생성하고 싶은 문장 (ex. "푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
def gen_text_renew(num, topic, character, background, context, before):
    #sys prompt 지정
    sys_prompt = """###시스템 프롬프트:
넌 지금부터 동화 작가야. 아래는 동화를 생성할 때 지켜야 하는 규칙이야.
1. 동화는 10세 이하 어린이들을 위한 내용이므로, 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 내용이 들어가지 않을 것.
2. 동화 제작과 관련이 없는 질문을 할 때에는 "[시스템] 저는 동화 창작 도우미입니다. 동화와 관련된 이야기를 작성해주세요!"를 출력할 것
3. 이전 내용을 참고해서 동화의 뒷 이야기를 만들 것
4. 한 문장은 "안녕하세요."와 같으며,  동화는 한 문장만 생성할 것
5. 이전 내용과 중복되지 않도록 다음 동화 내용을 생성할 것
    """
    
    #input 지정
    prompt = f"###페이지 번호: {num}\n\n###주제: {topic}\n\n###캐릭터: {character}\n\n###배경: {background}\n\n###이전내용: {context}\n###수정문장: {before}\n\n"
    prompt += "###사용자 입력: 수정문장은 내가 만든 페이지 번호에 해당하는 동화 내용인데, 이걸 다른 문장으로 수정하고 싶어. 너는 주제, 캐릭터, 배경, 이전 내용을 참고해서 수정 문장과 다른 내용으로 동화 내용을 생성해줘."
    
    #messages 구성
    messages = [
        SystemMessage(content = sys_prompt),
        HumanMessage(content = prompt),
    ]
    
    #문장 생성
    result = model.invoke(messages).content 
    result += "\n"
    
    return result

#동화 문장 요청사항 적용 함수
#num - 페이지 번호 (ex. 0)
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#context - 이전 동화 내용 / 첫 생성이 아닐 때만 존재하며, 첫 생성 시 ""의 공백으로 전달 (ex. "토끼는 마법의 거울을 챙겨 들고 거대한 성의 문을 활짝 열고 밖으로 나섰습니다. 푸른 하늘 아래 펼쳐진 마법의 숲은 토끼의 눈에 신비롭게 빛났습니다.")
#request_text - 요청사항 (ex. "갑자기 마법의 거울이 말을 걸고 시냇물을 마시라고 했으면 좋겠어")
def gen_text_update(num, topic, character, background, context, request_text):
    sys_prompt = """
넌 지금부터 동화 작가야. 아래는 동화를 생성할 때 지켜야 하는 규칙이야.
1. 동화는 10세 이하 어린이들을 위한 내용이므로, 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 내용이 들어가지 않을 것.
2. 동화 제작과 관련이 없는 질문을 할 때에는 "[시스템] 저는 동화 창작 도우미입니다. 동화와 관련된 이야기를 작성해주세요!"를 출력할 것
3. 이전 내용을 참고해서 동화의 뒷 이야기를 만들 것
4. 한 문장은 "안녕하세요."와 같으며,  동화는 한 문장만 생성할 것
5. 이전 내용과 중복되지 않도록 다음 동화 내용을 생성할 것
    """
    
    #input 지정
    prompt = f"###페이지 번호: {num}\n\n###주제: {topic}\n\n###캐릭터: {character}\n\n###배경: {background}\n\n###이전내용: {context}\n###참고내용: {request_text}\n\n"
    prompt += "###사용자 입력: 페이지 번호에 해당하는 내용을 만드는 건데, 수정 문장을 내가 만든 페이지 내용인데, 문장을 수정하고 싶어.\n너는 주제, 캐릭터, 배경, 이전 내용을 참고해서 다음 동화 내용을 만들면 되는데, 참고내용을 적용해서 동화 문장을 만들어줘."

    #messages 구성
    messages = [
        SystemMessage(content = sys_prompt),
        HumanMessage(content = prompt),
    ]
    
    #문장 생성
    result = model.invoke(messages).content 
    result += "\n"
    
    return result
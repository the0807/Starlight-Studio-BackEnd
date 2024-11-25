import urllib
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

#모델 생성
client = OpenAI()

#표지 생성 함수
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#함수 생성
def gen_cover(topic, character, background):
        
        sys_prompt = """###시스템 프롬프트:
아래는 그림을 그릴 때 지켜야 하는 규칙이야.
1. 그림에는 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 그림이 들어가지 않을 것
2. 사용자 입력에 맞는 그림을 그릴 것
3. 주제, 캐릭터, 배경, 사용자 입력을 참고해서 그릴 것
4. 그림은 동화풍의 파스텔톤으로 그릴 것
5. 그림에는 말풍선과 글자가 없어야 할 것
        """        
        
        #프롬프트 메시지
        prompt_input = "동화의 전체 내용을 보여주는 그림을 그려줘"
        
        #input 지정
        prompt_text = f"###시스템 프롬프트: {sys_prompt}\n\n###주제: {topic}\n\n##캐릭터: {character}\n\n##배경: {background}\n\n##사용자 입력: {prompt_input}\n\n"
                
        #print(prompt_text)
        response = client.images.generate(
            model = "dall-e-3",
            prompt = prompt_text,
            size = "1024x1024",
            quality = "standard",
            n = 1,
            
        )
        
        image_url = response.data[0].url
        
        return image_url

        # 이미지 저장
        # urllib.request.urlretrieve(test, "./test_img.jpg")
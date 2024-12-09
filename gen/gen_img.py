import urllib
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

#모델 생성
client = OpenAI()

#이미지 생성 함수
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#prompt_input - 동화 내용 (ex. "마법의 숲에 사는 토끼는 신나는 여행을 떠나기 위해 거대한 성의 문을 열고 친구 거북이와 함께 모험을 시작했어요.")
def gen_img(topic, character, background, prompt_input):
        
        sys_prompt = """###시스템 프롬프트:
아래는 그림을 그릴 때 지켜야 하는 규칙이야.
1. 그림에는 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 그림이 들어가지 않을 것
2. 사용자 입력에 맞는 그림을 그릴 것
3. 주제, 캐릭터, 배경, 사용자 입력을 참고해서 그릴 것
4. 그림은 동화책 삽화처럼 부드럽고 따뜻한 색조를 사용하며, 파스텔톤의 색상을 강조할 것
5. 그림에는 말풍선과 글자가 없어야 할 것
6. 그림의 분위기는 밝고 희망적이며 따뜻한 감정을 주도록 구성할 것
7. 캐릭터의 표정, 의상, 소품 등을 주제와 배경에 맞춰 자연스럽게 연출할 것
8. 배경과 캐릭터가 조화를 이루도록 전체적인 구도를 구성할 것
9. 그림의 스타일은 [부드러운 선과 확실한 색감, 캐릭터의 큰 눈과 친근한 표정]과 같은 특징을 반영할 것
10. 배경은 세부적인 디테일(예: 나무 잎사귀의 빛 반사, 고요한 강물의 반짝임)을 추가해 생동감 있게 표현할 것
11. 주제, 캐릭터, 배경, 사용자 입력이 서로 연결되고 조화를 이루도록 설정할 것
12. 사용자 입력에 따라 이야기가 전달되도록 그림의 구도를 구성할 것
        """        
        #input 지정
        prompt_text = f"###시스템 프롬프트: {sys_prompt}\n\n###주제: {topic}\n\n###캐릭터: {character}\n\n###배경: {background}\n\n###사용자 입력: {prompt_input}\n\n"
                
        response = client.images.generate(
            model = "dall-e-3",
            prompt = prompt_text,
            size = "1024x1024",
            quality = "standard",
            n = 1,
        )
        
        image_url = response.data[0].url
        
        return image_url

        #이미지 저장
        #urllib.request.urlretrieve(test, "./test_img.jpg")
        
#이미지 요청사항 적용 함수
#topic - 주제 (ex. "토끼의 여행")
#character - 캐릭터 (ex. "토끼와 거북이, 마법의 거울")
#background - 배경 (ex. "마법의 숲에 있는 거대한 성에 살고 있는 토끼가 여행을 떠난다")
#prompt_input - 동화 내용 (ex. "마법의 숲에 사는 토끼는 신나는 여행을 떠나기 위해 거대한 성의 문을 열고 친구 거북이와 함께 모험을 시작했어요.")
#request_text - 요청사항 (ex. 토끼의 눈이 반짝였으면 좋겠어)
def gen_img_update(topic, character, background, prompt_input, request_text):
        
        sys_prompt = """###시스템 프롬프트:
아래는 그림을 그릴 때 지켜야 하는 규칙이야.
1. 그림에는 술, 총, 폭력, 마약 등과 같이 어린이에게 부적절한 그림이 들어가지 않을 것
2. 사용자 입력에 맞는 그림을 그릴 것
3. 주제, 캐릭터, 배경, 사용자 입력과 참고사항을 적용해서 그릴 것
4. 그림은 동화풍의 파스텔톤으로 그릴 것
5. 그림에는 말풍선과 글자가 없어야 할 것
        """        
        #input 지정
        prompt_text = f"###시스템 프롬프트: {sys_prompt}\n\n###주제: {topic}\n\n###캐릭터: {character}\n\n###배경: {background}\n\n###참고사항: {request_text}\n\n##사용자 입력: {prompt_input}\n\n"
                
        response = client.images.generate(
            model = "dall-e-3",
            prompt = prompt_text,
            size = "1024x1024",
            quality = "standard",
            n = 1,
        )
        
        image_url = response.data[0].url
        
        return image_url

        #이미지 저장
        #urllib.request.urlretrieve(test, "./test_img.jpg")
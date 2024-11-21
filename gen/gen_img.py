import re
import base64
from vertexai.preview.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold, SafetySetting
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai import init
import os
import matplotlib.pyplot as plt
import config as CONFIG

#프로젝트 서비스 계정 환경 변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CONFIG.PROJECT['GOOGLE_APPLICATION_CREDENTIALS']

#프로젝트 id
PROJECT_ID = CONFIG.PROJECT['id']

#프로젝트 region
LOCATION = CONFIG.PROJECT['location']

#프로젝트 id, region 설정
init(project=PROJECT_ID, location=LOCATION)

#모델 설정
text_model = GenerativeModel("gemini-1.5-flash")
img_model = ImageGenerationModel.from_pretrained("imagen-3.0-fast-generate-001")

#이미지 생성 함수
#이미지는 Pillow 라이브러리 객체 타입
def gen_img(input):
    #영어 번역 생성 시스템 프롬프트
    prompt = f"다음 문장을 영어로 번역해줘 무조건 한 문장만 출력해줘\n{input}"
    
    #영어 번역 생성
    response = text_model.generate_content(
        [prompt],
        generation_config={"max_output_tokens": 200, "temperature": 0.7, "top_p": 0.2, "top_k": 1},
        stream=False  
    )

    #이미지 생성 시스템 프롬프트
    trans_result = "Draw the following sentence in fairy tale-style pastel colors\n"
    trans_result += response.candidates[0].content.parts[0].text
    
    #이미지 생성
    result = img_model.generate_images(
        prompt=trans_result,
        number_of_images=1,
        aspect_ratio="1:1",
        safety_filter_level="block_low_and_above",
        person_generation="dont_allow",
    )
    
    #이미지 반환
    return result[0]._pil_image

    #이미지 불러오기 코드
    #from PIL import Image
    #im = Image.open('./test.jpg')
    #plt.imshow(im)

    #이미지 저장 코드 
    #save("저장 주소", "png")
    #ex) result.save("./test.jpg", "png")
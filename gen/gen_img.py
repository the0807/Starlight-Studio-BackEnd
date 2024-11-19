import re
import base64
from vertexai.preview.vision_models import ImageGenerationModel
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
generation_model_fast = ImageGenerationModel.from_pretrained("imagen-3.0-fast-generate-001")

#이미지 생성 함수
def gen_gemini(trans_result):
    #이미지 생성
    fast_image = generation_model_fast.generate_images(
    prompt = trans_result,
    number_of_images=1,
    aspect_ratio="1:1",
    safety_filter_level="block_low_and_above",
    person_generation="dont_allow",
    )
    
    result_img = fast_image[0]._pil_image
    
    #이미지 저장 코드
    #result_img.save(f'./image/img0.jpg', 'png')

    # 이미지 보여주기
    # plt.imshow(fast_image[0]._pil_image)
    # plt.axis("off")
    # plt.show()

    return result_img
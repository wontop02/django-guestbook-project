from django.shortcuts import render
from django.http import JsonResponse 
from django.shortcuts import get_object_or_404 
from django.views.decorators.http import require_http_methods 
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import Guestbook
from django.utils.timezone import localtime
import json

@require_http_methods(["GET", "POST"])
def guestbook_list(request):

    if request.method == "GET":
        try:
            guestbook_all = Guestbook.objects.all().order_by('-created') # 내림차순. 최근 작성 글 우선

            guestbook_json_all = []

            for guestbook in guestbook_all:
                guestbook_json = {
                    "id": guestbook.id,
                    "writer": guestbook.writer,
                    "title": guestbook.title,
                    "content": guestbook.content,
                    # "password": guestbook.password, # 보안 상 제외
                    "created": localtime(guestbook.created).isoformat() 
                    # isoformat: datetime을 국제 표준 형식 문자열로 변환
                    # localtime으로 front에 한국 시간 기준으로 날짜 전송
                }
                guestbook_json_all.append(guestbook_json)

            return JsonResponse({
                "status": 200,
                "message": "방명록 목록 조회 성공",
                "data": guestbook_json_all
            })
        
        # 예상하지 못한 서버 에러
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "error": "InternalServerError",
                "message": "서버 내부 오류 발생"
            }, status=500)
        
    if request.method == "POST":
        try:

            body = json.loads(request.body.decode('utf-8'))

            password = body.get("password", "")

            # digit은 0~9 사이의 숫자. 숫자로만 이루어졌는지 확인
            if not password.isdigit() or len(password) != 4:
                return JsonResponse({
                    "status": 400,
                    "error": "BadRequest",
                    "message": "비밀번호는 숫자 4자리여야 합니다."
                }, status=400)

            allowed_fields = {"writer", "title", "content", "password"}
            extra_fields = set(body.keys()) - allowed_fields
            if extra_fields:
                return JsonResponse({
                    "status": 400,
                    "error": "BadRequest",
                    # '구분자'.join(리스트 또는 집합)
                    "message": f"허용되지 않은 필드가 포함되어 있습니다: {', '.join(extra_fields)}"
                }, status=400)

            new_guestbook = Guestbook.objects.create(
                writer = body["writer"],
                title = body["title"],
                content = body["content"],
                password = body["password"]
            )

            new_guestbook_json = {
                "id": new_guestbook.id,
                "writer": new_guestbook.writer,
                "title": new_guestbook.title,
                "content": new_guestbook.content,
                # "password": new_guestbook.password, # 보안 상 제외
                "created": localtime(new_guestbook.created).isoformat() 
            }

            return JsonResponse({
                "status": 201,
                "message": "방명록 생성 성공",
                "data": new_guestbook_json
            }, status=201)
        
        # 존재하지 않는 key에 접근하려고 할때 keyError 발생
        except KeyError as e:
            return JsonResponse({
                "status": 400,
                "error": "BadRequest",
                "message": f"필수 입력값이 누락되었습니다: {str(e)}"
        }, status=400)
        
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "error": "InternalServerError",
                "message": "서버 내부 오류 발생"
            }, status=500)
        

@require_http_methods(["GET", "DELETE"])
def guestbook_detail(request, guestbook_id):

    if request.method == "GET":
        try:
            guestbook = get_object_or_404(Guestbook, pk=guestbook_id)

            guestbook_json = {
                "id": guestbook.id,
                "writer": guestbook.writer,
                "title": guestbook.title,
                "content": guestbook.content,
                # "password": guestbook.password, # 보안 상 제외
                "created": localtime(guestbook.created).isoformat() 
            }

            return JsonResponse({
                "status": 200,
                "message": "방명록 단일 조회 성공",
                "data": guestbook_json
            })
        
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "error": "InternalServerError",
                "message": "서버 내부 오류 발생"
            }, status=500)

    if request.method == "DELETE":
        try:
            body = json.loads(request.body.decode('utf-8'))

            # 요청 body에 password 외에 다른 키 존재하는지 확인
            # body의 모든 key를 set으로 집합
            if set(body.keys()) != {"password"}:
                return JsonResponse({
                    "status": 400,
                    "error": "BadRequest",
                    "message": "DELETE 요청에는 'password'만 포함되어야 합니다."
                }, status=400)
        
            input_password = body.get("password")

            delete_guestbook = get_object_or_404(Guestbook, pk = guestbook_id)
            
            if delete_guestbook.password != input_password:
                return JsonResponse({
                    "status": 403,
                    "error": "Forbidden",
                    "message": "비밀번호가 일치하지 않습니다."
                }, status=403)
            
            delete_guestbook.delete()

            return JsonResponse({
                "status": 200,
                "message": "방명록 삭제 성공."
            }, status=200)
        
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "error": "InternalServerError",
                "message": "서버 내부 오류 발생"
            }, status=500)



                
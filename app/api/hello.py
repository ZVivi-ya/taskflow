from fastapi import APIRouter

router=APIRouter()

#
'''
实现一个接口：GET /api/v1/hello
返回：
{
  "message": "Welcome to TaskFlow",
  "project": "TaskFlow"
}
'''
@router.get("/hello")
def hello_check():
    return{
        "message":"Welcome to TaskFlow",
        "project":"TaskFlow API is running"
    }
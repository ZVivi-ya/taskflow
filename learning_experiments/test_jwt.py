from app.core.security import create_access_token, decode_access_token


def main():
    token = create_access_token(user_id=1)
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    # 只输出验证结果，不打印可直接使用的 JWT。
    print("Token 验证成功")
    print("用户 ID：", user_id)
    print("用户 ID 类型：", type(user_id))


if __name__ == "__main__":
    main()
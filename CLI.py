# REPL 환경, 명령어 파싱 및 에러 출력 담당

from mini_redis import MiniRedis

redis = MiniRedis()

while True:
    command = input("mini-redis> ")
    if command == "exit" or command == "quit":
        break
    print(command)
# REPL 환경, 명령어 파싱 및 에러 출력 담당

from mini_redis import MiniRedis

def run_cli():
    redis = MiniRedis()

    while True:
        command = input("mini-redis> ")
        if command == "exit" or command == "quit":
            break

        parts = command.split()
        if not parts:
            continue

        cmd = parts[0].upper()
        args = parts[1:]

        print("cmd:", cmd)
        print("args:", args)

        if cmd == "SET":
            pass
        elif cmd == "GET":
            pass
        elif cmd == "DEL":
            pass
        elif cmd == "EXISTS":
            pass
        elif cmd == "DBSIZE":
            pass
        elif cmd == "KEYS":
            pass
        elif cmd == "EXPIRE":
            pass
        elif cmd == "TTL":
            pass
        elif cmd == "CONFIG":
            pass
        elif cmd == "INFO":
            pass
        else:
            print(f"(error) ERR unknown command '{cmd.lower()}'")
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

        # --- SET key value [ttl_seconds] ---
        if cmd == "SET":
            if len(args) < 2 or len(args) > 3:
                print("(error) ERR wrong number of arguments for 'set' command")
                continue
            elif len(args) == 2:
                print(redis.set(args[0], args[1]))
            else:
                print(redis.set(args[0], args[1], ttl_seconds=args[2]))

        # --- GET key ---
        elif cmd == "GET":
            if len(args) != 1:
                print("(error) ERR wrong number of arguments for 'get' command")
            else:
                result = redis.get(args[0])
                print(f'"{result}"' if result is not None else "(nil)")

        # --- DEL key ---
        elif cmd == "DEL":
            if len(args) != 1:
                print("(error) ERR wrong number of arguments for 'del' command")
            else:
                print(redis.delete(args[0]))

        # --- EXISTS key ---
        elif cmd == "EXISTS":
            if len(args) != 1:
                print("(error) ERR wrong number of arguments for 'exists' command")
            else:
                print(redis.exists(args[0]))

        # --- DBSIZE ---
        elif cmd == "DBSIZE":
            if len(args) != 0:
                print("(error) ERR wrong number of arguments for 'dbsize' command")
            else:
                print(f"(integer) {redis.dbsize()}")

        # --- KEYS ---
        elif cmd == "KEYS":
            if len(args) != 0:
                print("(error) ERR wrong number of arguments for 'keys' command")
            else:
                key_list = redis.keys()
                if not key_list:
                    print("empty array")
                else:
                    for i, k in enumerate(key_list, start=1):
                        print(f'{i}) "{k}"')

        # --- EXPIRE key seconds ---
        elif cmd == "EXPIRE":
            if len(args) != 2:
                print("(error) ERR wrong number of arguments for 'expire' command")
            else:
                print(redis.expire(args[0], args[1]))

        # --- TTL key ---
        elif cmd == "TTL":
            if len(args) != 1:
                print("(error) ERR wrong number of arguments for 'ttl' command")
            else:
                print(redis.ttl(args[0]))

        # CONFIG SET maxmemory bytes ---
        elif cmd == "CONFIG":
            if len(args) == 3 and args[0].upper() == "SET" and args[1].lower() == "maxmemory":
                print(redis.config_set(args[2]))
            else:
                print("(error) ERR wrong number of arguments for 'config' command")

        # INFO memory ---
        elif cmd == "INFO":
            if len(args) == 1 and args[0].lower() == "memory":
                print(redis.info_memory())
            else:
                print(f"(error) ERR wrong number of arguments for 'info' command")

        else:
            print(f"(error) ERR unknown command '{cmd.lower()}'")
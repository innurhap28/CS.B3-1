# 프로그램 진입점

from CLI import run_cli

def main():
    try:
        run_cli()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")

if __name__ == "__main__":
    main()
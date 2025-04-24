import sys

if __name__ == "__main__":
    try:
        from utils.menu import main_menu
        main_menu()
    except KeyboardInterrupt:
        print("\n\033[91mПрограму перервано користувачем\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91mНеочікувана помилка: {str(e)}\033[0m")
        sys.exit(1)
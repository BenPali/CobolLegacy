import sys
from operations import Operations

class MainProgram:
    def __init__(self):
        self.continue_flag = True

    def run(self) -> None:
        try:
            while self.continue_flag:
                self._display_menu()
                choice = self._get_user_choice()
                if choice is None:
                    continue
                self._process_choice(choice)
            print("Exiting the program. Goodbye!")
        except KeyboardInterrupt:
            print("\nProgram interrupted. Goodbye!")
            sys.exit(0)

    def _display_menu(self) -> None:
        print("\n" + "-" * 32)
        print("Account Management System")
        print("1. View Balance")
        print("2. Credit Account")
        print("3. Debit Account")
        print("4. Exit")
        print("-" * 32)

    def _get_user_choice(self) -> int:
        try:
            choice_str = input("Enter your choice (1-4): ")
            choice = int(choice_str.strip())
            if 1 <= choice <= 4:
                return choice
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
                return None
        except (ValueError, EOFError):
            print("Invalid input. Please enter a valid number.")
            return None
        except KeyboardInterrupt:
            raise

    def _process_choice(self, choice: int) -> None:
        if choice == 1:
            Operations.execute("TOTAL")
        elif choice == 2:
            Operations.execute("CREDIT")
        elif choice == 3:
            Operations.execute("DEBIT")
        elif choice == 4:
            self.continue_flag = False

def main():
    program = MainProgram()
    program.run()

if __name__ == "__main__":
    main()
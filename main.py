from controller import AppController
from ui import BankingUI

def main():
    controller = AppController()
    app = BankingUI(controller)
    app.run()

if __name__ == "__main__":
    main()

import datetime
import tkinter
from config import *
from tkinter_interface import Main


def start():
    LOGGER.info(f"{'>' * 15}ЗАПУСТИЛИ ПРОГРАММУ {datetime.datetime.now().time().replace(microsecond=0)} {'<' * 15}")
    root = tkinter.Tk()
    root.geometry('550x400')
    root.title('KZ uploader')
    app = Main(root)
    root.mainloop()

start()

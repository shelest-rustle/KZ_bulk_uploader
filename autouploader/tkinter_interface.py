import os
import tkinter
import traceback
from tkinter import ttk, filedialog, BOTH
import datetime
from tools import *
from instruction import INSTRUCTION

CLASSES = (
    Agent1, Agent2, Agent3, Agent4, Agent5
)


CURRENT_FILE = ''
CONFIRMATION_BLOCK = 'on'
AGENTS_CLASSES = {agent: cls for agent, cls in zip(AGENTS, CLASSES)}

class Main(tkinter.Frame):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.build()

    def build(self):
        LOGGER.info(f'Создаем ткинтер {datetime.datetime.now().time().replace(microsecond=0)}')
        self.pack(fill=BOTH, expand=1)

        # Строка для выбора агента
        self.label_for_name = tkinter.Label(self, text="Выберите агента:",
                                   font=('Times New Roman', 16))
        self.label_for_name.place(x=20, y=50)


        # dropdown для выбора агента
        self.combo_agents = ttk.Combobox(self, font=('Times New Roman', 15))
        self.combo_agents['values'] = AGENTS
        self.combo_agents.place(x=260, y=50)


        # строка для выбора загрузочника
        self.label_for_uploader = tkinter.Label(self, text="Выберите загрузочник:",
                                   font=('Times New Roman', 16))
        self.label_for_uploader.place(x=20, y=140)

        # кнопка для выбора загрузочника
        self.button = tkinter.Button(self, text='Выбрать',
                                     command=self.press_button_file,
                                     font=('Times New Roman', 16),
                                     width=15)
        self.button.place(x=273, y=135)

        self.readme_button = tkinter.Button(self, text='Инструкция', command=self.show_instruction, font=('Times New Roman', 12), width=12)
        self.readme_button.place(x=210, y=350)

        # строка для подтверждения загрузки
        self.label_for_confirmation = tkinter.Label(self, text="",
                                                    font=('Times New Roman', 16),
                                                    background=self.root['background'], )
        self.label_for_confirmation.place(x=195, y=220)
        # строка для ошибок
        # self.label_for_confirmation = tkinter.Label(self, text="",
        #                                             font=('Times New Roman', 16),
        #                                             background=self.root['background'], )
        # self.label_for_confirmation.place(x=168, y=220)

        self.button_upload = tkinter.Button(self, text='Загрузить',
                                            command=self.press_button_upload,
                                            font=('Times New Roman', 16),
                                            width=15,
                                            height=1,
                                            background='yellow')
        self.button_upload.place(x=175, y=300)


    def press_button_file(self):
        try:
            global CURRENT_FILE, CONFIRMATION_BLOCK
            LOGGER.info(f'Выбираем файл {datetime.datetime.now().time().replace(microsecond=0)}')
            CURRENT_FILE = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=(("Excel files", '*.xlsx',),))
            CONFIRMATION_BLOCK = 'on'
            if CURRENT_FILE:
                self.button.configure(text='Готово')
                self.button.configure(state='disabled')
            self.button_upload.configure(background='yellow')
            self.label_for_confirmation.configure(text='', bg=self.root['background'])
        except Exception as e:
            LOGGER.info(f'Произошла ошибка при выборе файла {e}')


    def press_button_upload(self):
        global CURRENT_FILE, CONFIRMATION_BLOCK
        LOGGER.info(f'Нажали загрузку {datetime.datetime.now().time().replace(microsecond=0)}')
        agent = self.combo_agents.get()
        to_file = f'{agent}_{str(datetime.date.today().day).zfill(2)}_{str(datetime.date.today().month).zfill(2)}'
        if CONFIRMATION_BLOCK == 'on' and CURRENT_FILE and agent:
            self.button_upload.configure(background='red')
            CONFIRMATION_BLOCK = 'off'

            self.label_for_confirmation.configure(text="Подтвердите загрузку!",
                                                font=('Times New Roman', 16),
                                                background=self.root['background'],)
            self.label_for_confirmation.place(x=168, y=220)
            return
        elif not CURRENT_FILE:
            self.label_for_confirmation.configure(text="Выберите файл!",
                                                        font=('Times New Roman', 16),
                                                        background='red', )
            self.label_for_confirmation.place(x=195, y=220)

        elif not agent:
            self.label_for_confirmation.configure(text="Выберите агента!",
                                                        font=('Times New Roman', 16),
                                                        background='red', )
            self.label_for_confirmation.place(x=190, y=220)
        else:
            try:
                LOGGER.info(f'Начали обработку файлов, создаем объект-обработчик {datetime.datetime.now().time().replace(microsecond=0)}')
                file = AGENTS_CLASSES[agent](CURRENT_FILE, to_file)
                LOGGER.info(f'Продолжаем обработку, начинаем рефакторить файл {datetime.datetime.now().time().replace(microsecond=0)}')
                file.make_refactoring_and_write_json()
                LOGGER.info(f'Прошли обработку, загружаем {datetime.datetime.now().time().replace(microsecond=0)}')
                status = file.load_data()
                LOGGER.info(f'Статус загрузки {status}')
                if 'agent1' in agent.lower() or 'agent2' in agent.lower():
                    text = f'Загрузка агента прошла успешно\nКоличество контактов: {len(file.call_list)}\nИсключено по пустому due_date: {file.empty_due_date}' if str(status) in ('200', '202') else f'Загрузка агента провалилась,\n сообщите разработчику! Статус {status}'
                else:
                    text = f'Загрузка агента прошла успешно\nКоличество контактов: {len(file.call_list)}' if str(status) in ('200', '202') else f'Загрузка агента провалилась,\n сообщите разработчику! Статус {status}'  # это ещё не пересобиралось
                send_tg(AGENT_NAME=agent, message=text)
                bg = 'green' if str(status) in ('200', '202') else 'red'
                CURRENT_FILE = ''
                self.button.configure(text='Выбрать')
                self.button.configure(state='normal')
                self.label_for_confirmation.configure(text=text,
                                                        font=('Times New Roman', 16),
                                                        background=bg, )
                self.label_for_confirmation.place(x=120, y=210)
                self.button_upload.configure(background='yellow')
                LOGGER.info(f'Окончание работы программы')

            # if hasattr(self, 'label_for_confirmation'):
            #     self.label_for_confirmation.configure(text='', bg=self.root['background'])
                # self.root.destroy()
            except Exception as e:
                send_tg(agent, traceback.format_exc())

    def show_instruction(self):
        tkinter.messagebox.showinfo("Инструкция", INSTRUCTION)

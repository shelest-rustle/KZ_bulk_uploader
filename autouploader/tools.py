import json
from config import *
import pandas
import datetime
from api import send_data

if TEST:
    pandas.options.display.max_rows = None
    pandas.options.display.max_columns = None


class Refactor:
    """Абстрактный класс обработки .xlsx файла."""

    def __init__(self, from_file, to_file):
        self.from_file = from_file
        if 'agent2' in to_file.lower():
            self.df = pandas.read_excel(self.from_file, header=1)
        else:
            self.df = pandas.read_excel(self.from_file)
        self.to_file = to_file
        self.call_list = []
        self.empty_due_date = 0

    def load_data(self):
        upload_status = send_data(self.call_list, self.__str__(), self.to_file)
        if str(upload_status) not in ('200', '202'):
            send_tg(self.__str__(), f'Загрузка очереди не удалась, статус: {upload_status}')
        return upload_status

    def clear_due_date(self):
        self.empty_due_date = self.df["due_date"].isna().sum()
        self.df = self.df.dropna(subset=['due_date'])

    def change_column_types(self):
        self.df = self.df.fillna('')
        for column in self.df:
            if column == 'delay_sum':
                self.df[column] = self.df[column].apply(lambda x: str(int(round(x))) if round(x, 2).is_integer() else str(round(x, 2)).replace('.', ','))
            elif column == 'due_date':
                self.df[column] = self.df[column].apply(lambda x: str(x).split('.')[0] if len(str(x).split('.')) > 1 and str(x).split('.')[1] == '0' else str(x).replace('.', ','))
            else:
                self.df[column] = self.df[column].astype(str)

    def make_call_list(self):
        if TEST:
            print(self.df)
        result = json.loads(self.df.to_json(orient='index'))
        self.call_list = [result[r] for r in result]

    def __str__(self):
        return str(type(self).__name__)


class Agent_General(Refactor):
    """ Общий класс для Agent1 и Agent2 """

    def change_fio(self):
        """ Меняет регистр столбца ФИО  """
        self.df.rename(columns={'FIO': 'fio'}, inplace=True)

    def make_refactoring_and_write_json(self):
        """ В этой функции общие приготовления для отправки """
        self.change_fio()
        self.clear_due_date()
        self.df = self.df[self.df['delay_sum'] != '']
        self.change_column_types()
        if TEST:
            self.df['type_call'] = 'test'
        self.make_call_list()


class Agent1(Agent_General):

    def make_pressure(self):
        """ Добавляет столбик pressure в зависимости от названия файла и меняет название очереди"""

        if 'active' in self.from_file.lower():
            self.df['pressure'] = 'soft'
            list_of_file = self.to_file.split('_')
            list_of_file.insert(1, 'pressure_soft')
            self.to_file = '_'.join(list_of_file)
        else:
            self.df['pressure'] = ''

    def make_refactoring_and_write_json(self):
        self.make_pressure()
        super().make_refactoring_and_write_json()


class Agent2(Agent_General):

    def make_pressure(self):
        """ Добавляет столбик pressure в зависимости от названия файла """
        self.df['pressure'] = ''

    def make_refactoring_and_write_json(self):
        self.make_pressure()
        super().make_refactoring_and_write_json()


class Agent3(Agent_General):
    pass


class Agent4(Agent_General):

    def change_column_types(self):
        self.df = self.df.fillna('')
        self.df = self.df[self.df['delay_sum'] != '']
        for column in self.df:
            if column == 'delay_sum':
                self.df[column] = self.df[column].apply(lambda x: str(int(round(x))) if round(x, 2).is_integer() else str(round(x, 2)).replace('.', ','))
            elif column == 'due_date':
                self.df[column] = self.df[column].apply(lambda x: str(x).split('.')[0] if len(str(x).split('.')) > 1 and str(x).split('.')[1] == '0' else str(x).replace('.', ','))
            else:
                self.df[column] = self.df[column].astype(str)


class Agent5(Agent_General):

    def drop_product(self):
        """ Удаляет столбец product """
        if 'product' in self.df.columns:
            self.df.drop('product', axis=1, inplace=True)

    def plus_delay_and_commission(self):
        """ Складывает столбцы delay_sum & commission """
        self.df['delay_sum'] = self.df[['delay_sum', 'commission_rbk']].sum(axis=1)

    def drop_commission_rbk(self):
        """ Удаляет столбец commission """
        if 'commission_rbk' in self.df.columns:
            self.df.drop('commission_rbk', axis=1, inplace=True)

    def make_refactoring_and_write_json(self):
        self.drop_product()
        self.plus_delay_and_commission()
        self.drop_commission_rbk()
        super().make_refactoring_and_write_json()


class Agent6(Agent3):
    pass


class Agent7(Agent_General):

    def drop_product(self):
        """ Удаляет столбец product """
        if 'product' in self.df.columns:
            self.df.drop('product', axis=1, inplace=True)

    def rename_dpd(self):
        """ Переименовывает dpd -> due_date """
        self.df.rename(columns={'DPD': 'due_date'}, inplace=True)
        self.df.rename(columns={'dpd': 'due_date'}, inplace=True)

    def make_refactoring_and_write_json(self):
        self.df = self.df[self.df['delay_sum'] != '']
        self.rename_dpd()
        self.drop_product()
        super().make_refactoring_and_write_json()


class Agent8(Agent7):
    pass


class Agent9(Agent_General):

    def drop_product(self):
        """ Удаляет столбец product """
        if 'product' in self.df.columns:
            self.df.drop('product', axis=1, inplace=True)

    def plus_delay_and_commission_ins(self):
        """ Складывает столбцы delay_sum & commission & ins """
        self.df['delay_sum'] = self.df[['delay_sum', 'commission_rbk']].sum(axis=1)
        self.df['delay_sum'] = self.df[['delay_sum', 'ins']].sum(axis=1)

    def drop_commission_rbk_ins(self):
        """ Удаляет столбец commission """
        if 'commission_rbk' in self.df.columns:
            self.df.drop('commission_rbk', axis=1, inplace=True)
        if 'ins' in self.df.columns:
            self.df.drop('ins', axis=1, inplace=True)

    def make_refactoring_and_write_json(self):
        self.drop_product()
        self.plus_delay_and_commission_ins()
        self.drop_commission_rbk_ins()
        super().make_refactoring_and_write_json()


class Agent10(Refactor):

    def rename_columns(self):
        """ Переименовываем все колонки """
        self.df.rename(columns={'Основной номер телефона': 'msisdn'}, inplace=True)
        self.df.rename(columns={'ФИО': 'fio'}, inplace=True)
        self.df.rename(columns={'Номер заявки': 'CID'}, inplace=True)
        self.df.rename(columns={'Общая сумма зад.': 'delay_sum'}, inplace=True)
        self.df.rename(columns={'Дней просрочки': 'due_date'}, inplace=True)

    def drop_iin(self):
        """ Удаляем столбик ИИН если он есть """
        if 'ИИН' in self.df.columns:
            self.df.drop('ИИН', axis=1, inplace=True)

    def change_msisdn(self):
        """ Удаляем первую цифру номера """
        self.df['msisdn'] = self.df['msisdn'].apply(lambda x: str(x)[1:].split('.')[0])

    def change_column_types(self):
        self.df = self.df.fillna('')
        for column in self.df:
            if column == 'delay_sum':
                self.df[column] = self.df[column].apply(
                    lambda x: str(int(round(x))) if isinstance(x, (int, float)) and round(x, 2).is_integer() 
                    else str(round(x, 2)).replace('.', ',') if isinstance(x, (int, float)) 
                    else str(x)
                )
            elif column == 'due_date':
                self.df[column] = self.df[column].apply(lambda x: str(x).split('.')[0] if len(str(x).split('.')) > 1 and str(x).split('.')[1] == '0' else str(x).replace('.', ','))
            else:
                self.df[column] = self.df[column].astype(str)
        self.df = self.df[self.df['delay_sum'] != '']

    def make_refactoring_and_write_json(self):
        self.rename_columns()
        self.drop_iin()
        self.change_msisdn()
        self.change_column_types()
        if TEST:
            self.df['type_call'] = 'test'
        super().make_call_list()


class Agent11(Refactor):

    def change_column_types(self):
        self.df = self.df.fillna('')
        for column in self.df:
            if column == 'payment_sum':
                self.df[column] = self.df[column].apply(lambda x: str(int(round(x))) if x and round(x, 2).is_integer() else str(round(x, 2)).replace('.', ',') if x else '')
            else:
                self.df[column] = self.df[column].astype(str)

    def rename_columns(self):
        self.df['msisdn'] = self.df['msisdn'].apply(lambda x: str(x)[-10:].split('.')[0])
        self.df.rename(columns={'delay_sum': 'payment_sum'}, inplace=True)
        self.df.rename(columns={'payment_day': 'payment_date'}, inplace=True)
        self.df.drop("overdue_day", axis=1, inplace=True)
        if TEST:
            self.df['type_call'] = 'test'
        else:
            self.df['type_call'] = ''

    def make_refactoring_and_write_json(self):
        self.rename_columns()
        self.change_column_types()
        super().make_call_list()


class Agent12:

    def __init__(self, from_file, to_file):
        self.from_file = from_file
        self.origin_df = pandas.read_excel(self.from_file)
        self.result_df = pandas.DataFrame()
        self.to_file = to_file
        self.call_list = []
        self.empty_due_date = 0

    def load_data(self):
        upload_status = send_data(self.call_list, self.__str__(), self.to_file)
        if str(upload_status) not in ('200', '202'):
            send_tg(self.__str__(), f'Загрузка очереди не удалась, статус: {upload_status}')
        return upload_status

    def make_call_list(self):
        if TEST:
            print(self.result_df)
        result = json.loads(self.result_df.to_json(orient='index'))
        self.call_list = [result[r] for r in result]

    def __str__(self):
        """ Выводит название класса """
        return str(type(self).__name__)

    def create_final_date(self):
        self.origin_df["final_date"] = self.origin_df.apply(
            lambda row: (datetime.datetime.strptime(row["payment_day"], "%d.%m.%Y") + 
                        datetime.timedelta(days=row["amount of days"])).strftime("%d.%m.%Y"), 
            axis=1
        )
        self.result_df["final_date"] = self.origin_df["final_date"]

    def create_new_df(self):
        self.origin_df = self.origin_df[self.origin_df["amount of days"].apply(pandas.to_numeric, errors="coerce").between(1, 40, inclusive="both")]
        self.result_df["msisdn"] = self.origin_df["msisdn"].apply(lambda x: str(x)[1:])
        self.result_df["delay_sum"] = self.origin_df["delay_sum"].apply(lambda x: str(x))
        self.result_df["fio"] = self.origin_df["FIO"]
        self.result_df["payment_day"] = self.origin_df["payment_day"]
        self.result_df["sex"] = self.origin_df["sex"]
        self.create_final_date()
        self.result_df["prolongation"] = "1"
        self.result_df["date_payment"] = self.result_df["payment_day"]
        if TEST:
            self.result_df["type_call"] = "test"
        else:
            self.result_df["type_call"] = "prod"

    def make_refactoring_and_write_json(self):
        """ В этой функции общие приготовления для отправки """
        self.create_new_df()
        self.make_call_list()


class Agent13(Refactor):

    def make_refactoring_and_write_json(self):
        """ В этой функции общие приготовления для отправки """
        sums = ["ACTION_AMOUNT", "CREDIT_AMOUNT", "DISCOUNT_AMOUNT", "CREDIT_BALANCE"]
        self.df = self.df.fillna('')
        for column in self.df:
            if column in sums:
                self.df[column] = self.df[column].apply(lambda x: str(int(round(x))) if round(x, 2).is_integer() else str(round(x, 2)).replace('.', ','))
            else:
                self.df[column] = self.df[column].astype(str)
        self.df.drop("CLPHONE_ID", axis=1, inplace=True)
        self.df.drop("CLAGREEMENT_ID", axis=1, inplace=True)
        self.df.insert(0, "msisdn", self.df["CONTACT_INFO"])
        self.df["type_call"] = ""
        if TEST:
            self.df['type_call'] = 'test'
        self.make_call_list()


class Agent14(Refactor):

    def make_refactoring_and_write_json(self):
        """ В этой функции общие приготовления для отправки """
        self.df = self.df.fillna('')
        self.df = self.df.drop(index=0)  # Удаляем строки 1 и 3
        gender = self.df.pop("gender")  # вырезаем столбец gender (F)
        self.df.insert(2, "gender", gender)  # вставляем gender после фио
        self.df["gender"] = self.df["gender"].replace({"мужской": "m", "женский": "f"})  # заменяем значения gender на корректные
        for column in self.df:
            self.df[column] = self.df[column].astype(str)  # все столбцы приводим к str
        zero_count = (self.df["prolongation_sum"] == "0").sum()  # считаем prolongation_sum=0
        self.df = self.df[self.df["prolongation_sum"] != "0"]  # исключаем prolongation_sum=0
        LOGGER.info(f"Удалено строк с prolongation_sum=0: {zero_count}")
        self.df["due_date"] = pandas.to_numeric(self.df["due_date"], errors="coerce")  # due_date приводим к числу
        invalid_due_dates = self.df[self.df["due_date"] > 31]  # считаем due_date > 31
        self.df = self.df[self.df["due_date"] <= 31]  # исключаем due_date > 31
        self.df["due_date"] = self.df["due_date"].astype(str)
        LOGGER.info(f"Удалено строк с due_date>31: {len(invalid_due_dates)}")
        self.df["msisdn"] = self.df["msisdn"].apply(lambda x: str(x)[-10:])  # обрезаем телефон до 10значного
        self.df["type_call"] = "test" if TEST else ""  # добавляем тайпкол
        self.df["CID"] = ""  # добавляем cid
        self.make_call_list()


class Agent15(Refactor):

    def rename_columns(self):
        self.df.rename(columns={
            'Номер договора': 'CID',
            'Номер телефона': 'msisdn',
            'ФИО': 'fio',
            'Гендер': 'gender',
            'Ежемесячный платеж': 'payment_sum',
            'Дата оплаты': 'payment_date',
            'Сумма для пролонгации': 'prolongation_sum'
        }, inplace=True)

    def make_result_df(self):
        result_df = pandas.DataFrame()
        result_df['msisdn'] = self.df['msisdn']
        result_df['fio'] = self.df['fio']
        result_df['gender'] = self.df['gender']
        result_df['payment_sum'] = self.df['payment_sum']
        result_df['payment_date'] = self.df['payment_date']
        result_df['prolongation_sum'] = self.df['prolongation_sum']
        result_df['CID'] = self.df['CID']
        result_df['type_call'] = 'test' if TEST else ''
        self.df = result_df

    def make_refactoring_and_write_json(self):
        """ В этой функции общие приготовления для отправки """
        self.df = self.df.fillna('')
        self.rename_columns()
        self.df["msisdn"] = self.df["msisdn"].apply(lambda x: str(x)[-10:])  # обрезаем телефон до 10значного
        zero_count = (self.df["payment_sum"] == 0).sum()  # считаем prolongation_sum=0
        self.df = self.df[self.df["payment_sum"] != 0]  # исключаем prolongation_sum=0
        LOGGER.info(f"Удалено строк с payment_sum=0: {zero_count}")
        for column in self.df:
            if column == "payment_date":
                self.df['payment_date'] = self.df['payment_date'].apply(lambda x: '.'.join(list(reversed(x.split('-')))))  # преобразовываем payment_date в ДД.ММ.ГГГГ из ГГГГ-ММ-ДД
            elif column == 'payment_sum' or column == 'prolongation_sum':
                self.df[column] = self.df[column].apply(lambda x: str(int(round(x))) if round(x, 2).is_integer() else str(round(x, 2)).replace('.', ','))
            else:
                self.df[column] = self.df[column].astype(str)  # все столбцы приводим к str
        self.make_result_df()
        self.make_call_list()

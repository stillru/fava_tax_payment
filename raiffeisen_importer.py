import logging
import re
from datetime import datetime
from os import path
from beancount.ingest import importer
from beancount.core import data, amount
from beancount.core.number import D
from beancount import loader
from flask import current_app, g  # Оставляем для возможного будущего использования

# Настройка логирования
logger = logging.getLogger("beancount.importers.raiffeisen")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class RaiffeisenImporter(importer.ImporterProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_number = None
        self.currency = None
        self.bank_account = None
        try:
            logger.info(f"current_app.config in __init__: {dict(current_app.config)}")
            self.ledger_path = current_app.config.get('BEANCOUNT_FILES', [])[0]
            logger.info(f"ledger_path: {self.ledger_path}")
            self.entries, errors, options = loader.load_file(self.ledger_path)
            logger.info(f"entries: {self.entries}")
            logger.info(f"errors: {errors}")
            logger.info(f"options: {options}")
        except RuntimeError:
            logger.warning("Not in Flask context during __init__")

    def identify(self, file):
        """Проверяет, соответствует ли файл формату выписки Raiffeisen."""
        with open(file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            return "PROMET PO PARTIJI" in content and "Partija:" in content and "VALUTA:" in content

    def file_account(self, file, existing_entries=None):
        logger.info(f"file_account called with existing_entries: {len(existing_entries) if existing_entries else 'None'}")
        self._parse_header(file, existing_entries)
        return self.bank_account

    def file_date(self, file):
        """Извлекает дату выписки из заголовка."""
        with open(file.name, 'r', encoding='utf-8') as f:
            for line in f:
                if "Datum:" in line:
                    date_str = line.split("Datum:")[1].split("\t")[0].strip()
                    return datetime.strptime(date_str, '%d.%m.%Y').date()
        return None

    def _parse_header(self, file, existing_entries=None):
        """Извлекает номер счета и валюту из заголовка и сопоставляет с существующими счетами."""
        with open(file.name, 'r', encoding='utf-8') as f:
            for line in f:
                if "Partija:" in line:
                    logger.info(f"Raw line: {repr(line)}")
                    parts = line.split("Partija:")[1].split("\t")
                    logger.info(f"Parts after split: {parts}")
                    self.account_number = parts[1].strip()
                    logger.info(f"Acc_Num: {self.account_number}")
                if "VALUTA:" in line:
                    logger.info(line)
                    self.currency = line.split("VALUTA:")[1].strip().split()[0]
                    logger.info(f"Currency: {self.currency}")
                if self.account_number and self.currency:
                    break
        existing_entries = self.entries
        logger.info(f"Existing entries: {len(existing_entries) if existing_entries else 'None'}")
        if existing_entries:
            for entry in existing_entries:
                if isinstance(entry, data.Open):
                    logger.info(f"Open account: {entry.account}, meta: {entry.meta}")
                if (isinstance(entry, data.Open) and
                    entry.meta.get("account_number") == self.account_number and
                    entry.meta.get("currency") == self.currency):
                    self.bank_account = entry.account
                    return
        # Запасной вариант, если existing_entries отсутствует
        account_map = {
            "265000000708771538": "Assets:Bank:Raiffeisen:RSD"
        }
        self.bank_account = account_map.get(self.account_number)
        if not self.bank_account:
            self.bank_account = f"Assets:Bank:Raiffeisen:{self.currency}"
        if not self.bank_account:
            raise ValueError(f"Не найден счет для Partija={self.account_number}, VALUTA={self.currency}")
        logger.info(f"Bank account: {self.bank_account}")

    def extract(self, file, existing_entries=None):
        """Извлекает транзакции из файла и сравнивает с существующими."""
        self._parse_header(file, existing_entries)  # Устанавливаем bank_account
        entries = []
        with open(file.name, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Парсинг транзакций
        for line in lines:
            match = re.match(r'(\d{2}\.\d{2}\.\d{4})\t(\d{2}\.\d{2}\.\d{4})\t([\d.,]*)\t([\d.,]*)\t([\d.,]*)\t(.+)', line.strip())
            if match:
                date_valute, date_process, debit, credit, balance, description = match.groups()
                date = datetime.strptime(date_valute, '%d.%m.%Y').date()
                debit = D(debit.replace('.', '').replace(',', '.')) if debit else D('0')
                credit = D(credit.replace('.', '').replace(',', '.')) if credit else D('0')
                narration = description.strip()

                # Создаем метаданные
                meta = data.new_metadata(file.name, 0)

                # Определяем категорию (нужна реализация categorize_transaction)
                category = "Unknown"  # Временная заглушка, замените на self.categorize_transaction(narration)
                if debit > 0:
                    postings = [
                        data.Posting(self.bank_account, amount.Amount(-debit, self.currency), None, None, None, None),
                        data.Posting(f"Expenses:{category}", amount.Amount(debit, self.currency), None, None, None, None)
                    ]
                elif credit > 0:
                    account = f"Income:{category}" if category in ['Salary', 'CashDeposits', 'Other'] else "Income:Other"
                    postings = [
                        data.Posting(self.bank_account, amount.Amount(credit, self.currency), None, None, None, None),
                        data.Posting(account, amount.Amount(-credit, self.currency), None, None, None, None)
                    ]
                else:
                    continue  # Пропускаем строки без сумм

                # Проверяем дубликаты (нужна реализация is_duplicate)
                if False:  # Временная заглушка, замените на self.is_duplicate(date, narration, debit, credit, existing_entries)
                    meta["duplicate"] = True

                # Создаем запись
                txn = data.Transaction(
                    meta=meta,
                    date=date,
                    flag="*",
                    payee="",
                    narration=narration,
                    tags=data.EMPTY_SET,
                    links=data.EMPTY_SET,
                    postings=postings
                )
                entries.append(txn)

        return entries

    def categorize_transaction(self, description):
        """Определяет категорию транзакции."""
        categories = {
            'Food': ['LIDL', 'MAXI', 'PODRUM', 'AROMA', 'NICEFOODS', 'C MARKET', 'KFC', 'ASIA FOOD'],
            'Shopping': ['DEXY CO', 'U.C.L. DOO', 'HOUSE BEO', 'TEMU.COM', 'IKEA', 'SINSAY', 'NEW YORKER'],
            'Subscriptions': ['GOOGLE *', 'Spotify', 'REPLICATE'],
            'Utilities': ['OBJEDINJENA NAPLATA', 'Usluge', 'Yettel', 'EPS AD', 'SBB doo'],
            'Entertainment': ['TICKET VISION', 'JUMP BY FUN', 'SKAKAONICA'],
            'Education': ['Ministarstvo prosvete', 'Škola mladih', 'Ekskurzija', 'Obezbedjenje'],
            'Transport': ['Yandex Go', 'FLIX'],
            'Services': ['Naplata provizije', 'Elektronsko bankarstvo'],
            'Gifts': ['8 mart'],
            'Health': ['BENU PHARMACIES', 'LILLY APOTEKA'],
            'Cash': ['SMART ATM - Isplata'],
            'CashDeposits': ['SMART ATM - Uplata'],
            'Salary': ['Plata'],
            'Transfers': ['Transakcije po nalogu gradjana']
        }
        for category, keywords in categories.items():
            if any(keyword in description.upper() for keyword in keywords):
                return category
        return 'Other'

    def is_duplicate(self, date, narration, debit, credit, existing_entries):
        """Проверяет, является ли транзакция дубликатом."""
        if not existing_entries:
            return False
        for entry in existing_entries:
            if (isinstance(entry, data.Transaction) and
                entry.date == date and
                entry.narration == narration and
                any(p.account == self.bank_account and p.amount == amount.Amount(debit if debit > 0 else -credit, self.currency) for p in entry.postings)):
                return True
        return False

# Тестовый запуск
if __name__ == "__main__":
    from beancount.ingest import scripts_utils
    importer_instance = RaiffeisenImporter()
    scripts_utils.ingest(importer_instance, ["imports"])

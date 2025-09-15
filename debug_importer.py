# /bean/importers/debug_importer.py
import logging
from beancount.ingest import importer
from flask import current_app

# Настройка логирования
logger = logging.getLogger("beancount.importers.debug")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False

class DebugImporter(importer.ImporterProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"__init__ called with args: {args}")
        logger.info(f"__init__ called with kwargs: {kwargs}")
        try:
            config_dict = dict(current_app.config)
            logger.info(f"current_app.config in __init__: {config_dict}")
            ledgers_loader = current_app.config.get('LEDGERS')
            logger.info(f"LEDGERS in __init__: {ledgers_loader}")
            if ledgers_loader:
                logger.info(f"LEDGERS dir: {dir(ledgers_loader)}")
                # Получаем список ledger’ов
                ledgers_list = ledgers_loader.__getattr__('ledgers', None)
                logger.info(f"ledgers_list: {ledgers_list}")
                logger.info(f"ledgers_list length: {len(ledgers_list)}")
                if ledgers_list:
                    first_ledger = ledgers_list[0]
                    logger.info(f"first_ledger: {first_ledger}")
                    logger.info(f"first_ledger dir: {dir(first_ledger)}")
                    if hasattr(first_ledger, 'beancount_file_path'):
                        logger.info(f"first_ledger.beancount_file_path: {first_ledger.beancount_file_path}")
                    if hasattr(first_ledger, 'entries'):
                        logger.info(f"first_ledger.entries length: {len(first_ledger.entries)}")
                # Проверяем ledgers_by_slug
                ledgers_by_slug = ledgers_loader.ledgers_by_slug
                logger.info(f"ledgers_by_slug: {ledgers_by_slug}")
                first_slug = ledgers_loader.first_slug()
                logger.info(f"first_slug: {first_slug}")
                if first_slug in ledgers_by_slug:
                    ledger_by_slug = ledgers_by_slug[first_slug]
                    logger.info(f"ledger_by_slug: {ledger_by_slug}")
                    logger.info(f"ledger_by_slug dir: {dir(ledger_by_slug)}")
                    if hasattr(ledger_by_slug, 'beancount_file_path'):
                        logger.info(f"ledger_by_slug.beancount_file_path: {ledger_by_slug.beancount_file_path}")
                    if hasattr(ledger_by_slug, 'entries'):
                        logger.info(f"ledger_by_slug.entries length: {len(ledger_by_slug.entries)}")
        except RuntimeError:
            logger.warning("Not in Flask context during __init__")

    def identify(self, file):
        logger.info(f"identify called with file: {file.name}")
        try:
            logger.info(f"current_app.config in identify: {dict(current_app.config)}")
        except RuntimeError:
            logger.warning("Not in Flask context during identify")
        return True

    def file_account(self, file, existing_entries=None):
        logger.info(f"file_account called with file: {file.name}, existing_entries: {len(existing_entries) if existing_entries else 'None'}")
        try:
            logger.info(f"current_app.config in file_account: {dict(current_app.config)}")
        except RuntimeError:
            logger.warning("Not in Flask context during file_account")
        return "Assets:Debug"

    def file_date(self, file):
        logger.info(f"file_date called with file: {file.name}")
        try:
            logger.info(f"current_app.config in file_date: {dict(current_app.config)}")
        except RuntimeError:
            logger.warning("Not in Flask context during file_date")
        return None

    def extract(self, file, existing_entries=None):
        logger.info(f"extract called with file: {file.name}, existing_entries: {len(existing_entries) if existing_entries else 'None'}")
        try:
            logger.info(f"current_app.config in extract: {dict(current_app.config)}")
        except RuntimeError:
            logger.warning("Not in Flask context during extract")
        return []

if __name__ == "__main__":
    from beancount import loader
    from beancount.ingest import scripts_utils
    ledger_file = "/bean/index.bean"
    entries, errors, options = loader.load_file(ledger_file)
    importer_instance = DebugImporter()
    scripts_utils.ingest(importer_instance, ["/bean/imports"], existing_entries=entries)
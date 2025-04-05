from fava.ext import FavaExtensionBase
from fava.application import app
from PyPDF2 import PdfReader, PdfWriter
from flask import jsonify, g
import json
import os
from jinja2 import FileSystemLoader, ChoiceLoader
from fava.ext import extension_endpoint
import importlib.resources as resources
import shutil

class TaxPaymentExtension(FavaExtensionBase):
    report_title = "Tax Payment PDFs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Initializing TaxPaymentExtension with args:", args, "kwargs:", kwargs)
        
        package = "fava_tax_payment"
        extension_dir = os.getcwd()
        print(f"Using directory: {extension_dir}")

        config_dir = os.path.join(extension_dir, "config")
        local_config_path = os.path.join(config_dir, "tax_config.json")

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            print(f"Created config directory: {config_dir}")
        
        if not os.path.exists(local_config_path):
            with resources.path(package, "tax_config.json") as package_config_path:
                shutil.copy(str(package_config_path), local_config_path)
            print(f"Copied default tax_config.json to {local_config_path}")
        else:
            print(f"Using existing tax_config.json at {local_config_path}")

        try:
            with open(local_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            print("Loaded tax_config.json successfully")
        except Exception as e:
            print(f"Error loading tax_config.json: {e}")
            raise

        # Доступ к template.pdf из пакета
        try:
            with resources.path(package, "template.pdf") as template_path:
                self.template_path = str(template_path)
            print(f"Template path: {self.template_path}")
        except Exception as e:
            print(f"Error accessing template.pdf: {e}")
            raise

        try:
            with resources.path(package, "TaxPaymentExtension.html") as html_path:
                template_dir = os.path.dirname(str(html_path))
            if isinstance(self.jinja_env.loader, ChoiceLoader):
                self.jinja_env.loader.loaders.append(FileSystemLoader(template_dir))
            else:
                self.jinja_env.loader = ChoiceLoader([
                    self.jinja_env.loader,
                    FileSystemLoader(template_dir)
                ])
            print(f"Jinja template directory: {template_dir}")
        except Exception as e:
            print(f"Error setting Jinja template directory: {e}")
            raise
        
        self.payer_name = config["payer"]["name"]
        self.payer_account = config["payer"]["account"]
        self.expense_category = config["expense_category"]
        self.tax_configs = config["taxes"]
        self.template_path = template_path
        self.app = app

    @extension_endpoint("generate_tax_pdfs", ["POST"])  # Define endpoint name and methods
    def generate_tax_pdfs(self):
        try:
            output_files = self._generate_tax_pdfs()
            return jsonify({"status": "success", "files": output_files})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def _generate_tax_pdfs(self):
        ledger = self.ledger
        extension_dir = os.getcwd()
        output_files = []
        
        for entry in ledger.all_entries_by_type.Transaction:
            for posting in entry.postings:
                if posting.account.startswith(self.expense_category):
                    amount = str(posting.units.number)
                    currency = posting.units.currency
                    date = entry.date.strftime("%Y-%m-%d")

                    tax_type = None
                    if posting.meta and "tax_type" in posting.meta:
                        tax_type = posting.meta["tax_type"]
                    elif entry.narration in self.tax_configs:
                        tax_type = entry.narration

                    if tax_type and tax_type in self.tax_configs:
                        tax_data = self.tax_configs[tax_type]
                        output_file = os.path.join(extension_dir, f"filled_{tax_type}_tax_{date}.pdf")
                        pdf_data = {
                            "payer": self.payer_name,
                            "purpose": tax_data["purpose"],
                            "recipient": tax_data["recipient"],
                            "payment_code": tax_data["payment_code"],
                            "currency": currency,
                            "amount": amount,
                            "recipient_account": tax_data["recipient_account"],
                            "model": tax_data["model"],
                            "reference_number": tax_data["reference_number"],
                            "date": date,
                            "currency_date": date
                        }
                        self.fill_pdf_form(output_file, pdf_data)
                        output_files.append(output_file)
                        print(f"Generated: {output_file}")
        return output_files

    def fill_pdf_form(self, output_path, data):
        print(f"Filling PDF: {output_path} with data: {data}")
        reader = PdfReader(self.template_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.update_page_form_field_values(
            writer.get_page(0),
            {
                "Uplatilac": data["payer"],
                "SvrhaUplate": data["purpose"],
                "Primalac": data["recipient"],
                "ShifraPlachena": data["payment_code"],
                "Valuta": data["currency"],
                "Iznos": data["amount"],
                "RachunPrimaoca": data["recipient_account"],
                "Model": data["model"],
                "Datum": data["date"],
                "PechatIPodpis": "",
                "PozivNaBroj": data["reference_number"],
                "DatumValute": data["currency_date"]
            }
        )
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
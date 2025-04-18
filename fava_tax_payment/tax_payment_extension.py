from decimal import Decimal
from fava.ext import FavaExtensionBase
from fava.application import app
from fava.context import g
from PyPDF2 import PdfReader, PdfWriter
from flask import current_app, jsonify, render_template, request, send_from_directory
import json
import os
from fava.ext import extension_endpoint
import importlib.resources as resources
import shutil


class TaxPaymentExtension(FavaExtensionBase):
    """
    A Fava extension for generating tax payment PDFs and managing tax configurations.
    """

    report_title = "Tax Payment PDFs"
    has_js_module = True

    def __init__(self, *args, **kwargs):
        """
        Initialize the TaxPaymentExtension.

        - Loads or creates the tax configuration file.
        - Sets up the Jinja environment for rendering templates.
        - Loads the PDF template for generating tax payment slips.
        """
        super().__init__(*args, **kwargs)
        self.app = app

        self.app.logger.info(
            "Initializing TaxPaymentExtension with args: %s, kwargs: %s",
            args,
            kwargs,
        )
        package = "fava_tax_payment"
        ledger = self.ledger
        ledger_dir = os.path.dirname(os.path.abspath(ledger.beancount_file_path))
        extension_dir = os.getcwd()
        self.app.logger.info(f"Using directory: {extension_dir}")
        self.expense_accounts = self.get_expense_accounts()
        config_dir = os.path.join(ledger_dir, "config")
        self.local_config_path = os.path.join(config_dir, "tax_config.json")

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            self.app.logger.info(f"Created config directory: {config_dir}")

        if not os.path.exists(self.local_config_path):
            with resources.path(
                f"{package}.Files", "tax_config.json"
            ) as package_config_path:
                shutil.copy(
                    str(package_config_path),
                    self.local_config_path,
                )
            self.app.logger.info(
                "Copied default tax_config.json to %s",
                self.local_config_path,
            )
        else:
            self.app.logger.info(
                "Using existing tax_config.json at %s",
                self.local_config_path,
            )

        try:
            with open(
                self.local_config_path,
                "r",
                encoding="utf-8",
            ) as f:
                self.tax_config = json.load(f)
            self.app.logger.info(
                "Loaded tax_config.json successfully: %s",
                self.tax_config,
            )
        except Exception as e:
            self.app.logger.error("Error loading tax_config.json: %s", e)
            raise

        if not isinstance(self.tax_config, dict):
            self.tax_config = {}
        if "payer" not in self.tax_config:
            self.tax_config["payer"] = {
                "name": "Default Payer",
                "account": "000000000",
            }
        if "expense_category" not in self.tax_config:
            self.tax_config["expense_category"] = "Expenses:Taxes"
        if "taxes" not in self.tax_config:
            self.tax_config["taxes"] = {}

        try:
            with resources.path(f"{package}.Files", "template.pdf") as template_path:
                self.template_path = str(template_path)
            self.app.logger.info("Template path: %s", self.template_path)
        except Exception as e:
            self.app.logger.error("Error accessing template.pdf: %s", e)
            raise

        self.payer_name = self.tax_config["payer"]["name"]
        self.payer_account = self.tax_config["payer"]["account"]
        self.expense_category = self.tax_config["expense_category"]
        self.tax_configs = self.tax_config["taxes"]

    def _sanitize_config(self, config):
        """
        Sanitize the configuration by converting unsupported types to strings.

        Args:
            config (dict, list, or other): The configuration to sanitize.

        Returns:
            The sanitized configuration.
        """
        if isinstance(config, dict):
            return {k: self._sanitize_config(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._sanitize_config(item) for item in config]
        elif isinstance(config, Decimal):
            return float(config)
        elif isinstance(config, (str, int, float, bool)) or config is None:
            return config
        else:
            self.app.logger.warning(
                f"Warning: Unsupported type {type(config)} in config, \
                converting to string"
            )
            return str(config)

    def get_expense_accounts(self):
        """
        Get a list of expense accounts from the ledger.

        Returns:
            list: A list of expense accounts.
        """
        ledger = self.ledger
        return [
            account for account in ledger.accounts if account.startswith("Expenses:")
        ]
    
    def list_docs(self):
        ledger = self.ledger
        ledger_dir = os.path.dirname(os.path.abspath(ledger.beancount_file_path))
        output_dir = os.path.join(ledger_dir, "tax_pdfs")
        files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
        
        return files

    @extension_endpoint("document", ["GET"])
    def document(self):
        """Serve a PDF file for download from the tax_pdfs directory."""
        ledger_dir = os.path.dirname(os.path.abspath(self.ledger.beancount_file_path))
        output_dir = os.path.join(ledger_dir, "tax_pdfs")
        
        # Get filename from query parameters
        filename = request.args.get('filename')
        self.app.logger.info(f"Requested file: {filename}")
        
        # Validate filename
        if not filename:
            self.app.logger.error("No filename provided in request")
            return jsonify({"status": "error", "message": "No filename provided"}), 400
        
        if not filename.endswith('.pdf'):
            self.app.logger.error(f"Invalid file type requested: {filename}")
            return jsonify({"status": "error", "message": "Only PDF files are supported"}), 400
        
        # Prevent path traversal by using basename
        safe_filename = os.path.basename(filename)
        full_path = os.path.join(output_dir, safe_filename)
        
        if not os.path.exists(full_path):
            self.app.logger.error(f"File not found: {full_path}")
            return render_template("error.html", message="File not found"), 404
        
        self.app.logger.info(f"Serving file: {full_path}")
        return send_from_directory(
            output_dir,
            safe_filename,
            as_attachment=True,  # Set to True if you want to force download
            mimetype="application/pdf",
            download_name=safe_filename  # Ensures the filename is preserved in the download
        )

    @extension_endpoint("save_config", ["POST"])
    def save_config(self):
        """
        Save the updated tax configuration to the local configuration file.

        Returns:
            JSON response indicating success or failure.
        """
        try:
            new_config = request.get_json()
            with open(
                self.local_config_path,
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    new_config,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            self.tax_config = new_config
            self.payer_name = new_config["payer"]["name"]
            self.payer_account = new_config["payer"]["account"]
            self.expense_category = new_config["expense_category"]
            self.tax_configs = new_config["taxes"]
            self.app.logger.info(f"Saved updated config to {self.local_config_path}")
            return jsonify(
                {
                    "status": "success",
                    "message": "Configuration saved",
                }
            )
        except Exception as e:
            return (
                jsonify({"status": "error", "message": str(e)}),
                500,
            )

    @extension_endpoint("generate_tax_pdfs", ["POST"])
    def generate_tax_pdfs(self):
        """
        Generate tax payment PDFs based on the ledger transactions.

        Returns:
            JSON response with the list of generated files or an error message.
        """
        try:
            output_files = self._generate_tax_pdfs()
            return jsonify({"status": "success", "files": output_files})
        except Exception as e:
            return (
                jsonify({"status": "error", "message": str(e)}),
                500,
            )

    def _generate_tax_pdfs(self):
        """
        Generate tax payment PDFs for transactions in the ledger.

        Returns:
            list: A list of paths to the generated PDF files.
        """
        ledger = self.ledger
        # Get the directory of the ledger file
        ledger_dir = os.path.dirname(os.path.abspath(ledger.beancount_file_path))
        # Define the output directory next to the ledger file
        output_dir = os.path.join(ledger_dir, "tax_pdfs")
        output_files = []

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.app.logger.info(f"Created output directory: {output_dir}")

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
                        output_file = os.path.join(
                            output_dir,
                            f"filled_{tax_type}_tax_{date}.pdf",
                        )
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
                            "currency_date": date,
                        }
                        self.fill_pdf_form(output_file, pdf_data)
                        output_files.append(output_file)
                        self.app.logger.info(f"Generated: {output_file}")
        return output_files

    def fill_pdf_form(self, output_path, data):
        """
        Fill a PDF form with the provided data.

        Args:
            output_path (str): The path to save the filled PDF.
            data (dict): The data to populate the PDF form.
        """
        self.app.logger.info(f"Filling PDF: {output_path} with data: {data}")
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
                "DatumValute": data["currency_date"],
            },
        )
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

# Fava Tax Payment Extension

A Fava extension that generates PDF tax payment slips directly from your Beancount transactions. This extension simplifies tax reporting by automatically creating properly formatted tax payment documents based on your financial data.

## Features

- Generates PDF tax payment slips from tagged Beancount transactions
- Supports multiple tax types (income, healthcare, fixed fees, etc.)
- Customizable payment details through configuration
- Simple web UI integration with Fava
- Automatically fills official payment form templates

## Planned Features and Improvements

The following features and improvements are planned for future releases of the Tax Payment Extension:

### Code Improvements
1. **Improve `self.app` Handling**
   - Ensure the Flask app instance is accessed correctly in the Fava extension context.

2. **Error Handling in Configuration Loading**
   - Validate the structure of `tax_config.json` after loading to ensure all required keys are present.

3. **Dynamic Path Handling**
   - Replace hardcoded paths (e.g., `template.pdf`, `TaxPaymentExtension.html`) with dynamic, package-relative paths.

4. **Jinja2 Loader Compatibility**
   - Ensure compatibility when modifying the Jinja2 loader, especially when it is not a `ChoiceLoader`.

5. **Error Handling in PDF Generation**
   - Add validation for `tax_data` to prevent `KeyError` during PDF generation.

6. **Error Logging**
   - Replace `print` statements with a proper logging framework for better error tracking in production.

7. **Dependency Validation**
   - Add checks to ensure required libraries (e.g., `PyPDF2`, `Flask`) are installed and compatible.

### Security Enhancements
8. **Sanitize User Input**
   - Validate and sanitize user-provided configuration data before saving it to prevent potential security risks.

### UI and UX Improvements
9. **Improve JavaScript Error Handling**
   - Enhance error handling in JavaScript to provide user-friendly messages and better debugging information.

10. **Responsive UI**
    - Test and improve the responsiveness of the HTML form for smaller screens using CSS media queries.

11. **Multilanguage Support**
    - Add support for multiple languages in the UI and error messages.

### Maintainability
12. **Move CSS and JavaScript to Separate Files**
    - Extract inline CSS and JavaScript into separate files for better maintainability and reusability.

13. **Remove Unused Code**
    - Review and remove unused imports or redundant logic in Python and JavaScript files.

14. **Hardcoded Strings in PDF Form Filling**
    - Replace hardcoded field names in the `fill_pdf_form` method with configurable constants.

### Testing
15. **Add Unit Tests**
    - Implement unit tests for critical methods like `_generate_tax_pdfs`, `save_config`, and `fill_pdf_form` to ensure reliability.


## Installation

```bash
pip install fava-tax-payment
```

For development installation:

```bash
git clone https://github.com/stillru/fava-tax-payment.git
cd fava-tax-payment
pip install -e .
```

## Configuration

### Adding the Extension to Fava

Add the extension to your Beancount file:

```
plugin "fava.plugins.extension" "fava_tax_payment.tax_payment_extension.TaxPaymentExtension"
```

### Tax Configuration

The extension creates a `config/tax_config.json` file in your working directory on first run. You can customize this file with your payment details:

```json
{
  "payer": {
    "name": "Your Name or Company",
    "account": "Your-Account-Number"
  },
  "expense_category": "Expenses:Taxes",
  "taxes": {
    "income": {
      "purpose": "Income Tax Payment",
      "recipient": "Tax Authority Name",
      "recipient_account": "Tax-Authority-Account",
      "payment_code": "Code",
      "model": "Model",
      "reference_number": "Reference"
    },
    // Additional tax types...
  }
}
```

## Usage

### Tagging Transactions

The extension identifies tax transactions in two ways:

1. Via transaction metadata:
```
2023-04-15 * "Monthly Tax Payment"
    Expenses:Taxes:Income  1000.00 RSD
        tax_type: "income"
    Assets:Bank:Checking
```

2. Via transaction narration matching tax type name:
```
2023-04-15 * "income"
    Expenses:Taxes:Income  1000.00 RSD
    Assets:Bank:Checking
```

### Generating PDFs

1. Open your Fava interface
2. Navigate to the "Tax Payment PDFs" section in the sidebar
3. Click "Generate PDFs" button
4. PDFs will be created in your working directory

## Requirements

- Python 3.10+
- Fava 1.30.2+
- PyPDF2 3.0.0+
- Flask 3.1.0+

## Development

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
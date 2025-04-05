# Fava Tax Payment Extension

A Fava extension that generates PDF tax payment slips directly from your Beancount transactions. This extension simplifies tax reporting by automatically creating properly formatted tax payment documents based on your financial data.

## Features

- Generates PDF tax payment slips from tagged Beancount transactions
- Supports multiple tax types (income, healthcare, fixed fees, etc.)
- Customizable payment details through configuration
- Simple web UI integration with Fava
- Automatically fills official payment form templates

## Planned Features

- [ ] Multilanguage support
- [ ] Improve UI

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
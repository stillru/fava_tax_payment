from setuptools import setup, find_packages

setup(
    name="fava-tax-payment",
    version="0.1.1",
    author="Stepan Illichevskii",
    author_email="still.ru@gmail.com",
    description="A Fava extension for generating tax payment PDFs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stillru/fava_tax_payment",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "fava_tax_payment": [
            "Files/template.pdf",
            "Files/tax_config.json",
            "templates/TaxPaymentExtension.html",
            "TaxPaymentExtension.js",
        ]
    },
    install_requires=[
        "fava>=1.30.2",
        "PyPDF2>=3.0.0",
        "flask>=3.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    extras_require={
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme",
        ],
    },
)

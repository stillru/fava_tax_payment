from setuptools import setup, find_packages

setup(
    name="fava-tax-payment",
    version="0.1.0",
    author="Stepan Illichevskii",
    author_email="still.ru@gmail.com",
    description="A Fava extension for generating tax payment PDFs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stillru/fava-tax-payment",  # Опционально, если будет репозиторий
    packages=find_packages(),
    include_package_data=True,  # Включаем файлы из MANIFEST.in
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

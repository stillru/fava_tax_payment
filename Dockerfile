FROM python:3.10-slim

RUN pip install --upgrade pip
RUN pip install fava>=1.30.2

WORKDIR /app

COPY dist/fava_tax_payment-*-py3-none-any.whl .
RUN pip install fava_tax_payment-*-py3-none-any.whl

COPY year2025.org .

EXPOSE 5000

CMD ["fava","--debug","--host", "0.0.0.0", "year2025.org"]

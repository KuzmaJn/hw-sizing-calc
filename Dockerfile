FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "cli.py"]
# Default: show help if no arguments are given.
#   docker run --rm hw-sizing-calculator --transactions 500000 --type medium
# To run the test suite instead, override the entrypoint:
#   docker run --rm --entrypoint python hw-sizing-calculator -m pytest tests/ -v
CMD ["--help"]
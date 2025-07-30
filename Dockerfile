FROM python:3.12

RUN curl -s https://v2.d-f.pw/f/prepare-python.sh?2 | bash -s

WORKDIR /app
COPY . /app

COPY requirements.txt .

RUN curl -s https://v2.d-f.pw/f/install-python.sh?2 | bash -s 'false' 'true'

RUN pip install --no-cache-dir -r requirements.txt

CMD /entrypoint.sh python main.py
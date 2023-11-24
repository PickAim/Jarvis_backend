FROM python:3.11 AS build
ARG GITHUB_TOKEN
RUN git config --global url."https://${GITHUB_TOKEN}@github.com".insteadOf https://github.com
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . .
EXPOSE 8090
CMD [ "python", "-u", "main.py" ]

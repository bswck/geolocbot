FROM python:3.9-buster

WORKDIR /bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Replace this with the password file to use
ENV GEOLOCBOT_PASSWORD_FILE 'invalid'
EXPOSE 80

COPY . .

CMD ["python", "bot.py"]
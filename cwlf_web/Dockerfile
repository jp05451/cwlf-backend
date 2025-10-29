FROM python:3.9

# 步驟2：在便當盒裡建立一個工作區，叫做 /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt .

RUN pip install -r requirements.txt

# 將所有程式碼複製進工作區
COPY . .
RUN find . -name "*.db" -type f -delete

EXPOSE 5000

CMD ["sh", "-c", "python app.py --port 5000"]


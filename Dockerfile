FROM python:3.8 

COPY requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

EXPOSE 8000

ENTRYPOINT ["python", "/src/gameserver.py"]
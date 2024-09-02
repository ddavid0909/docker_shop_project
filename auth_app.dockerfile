FROM python:3.9
LABEL authors="fafulja"

COPY auth_config.py /auth_config.py
COPY auth_models.py /auth_models.py
COPY auth_app.py /auth_app.py
COPY auth_requirements.txt /requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "auth_app.py"]
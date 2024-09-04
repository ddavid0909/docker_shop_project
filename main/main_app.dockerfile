FROM python
LABEL authors="fafulja"

COPY main_config.py /main_config.py
COPY main_models.py /main_models.py
COPY main_app.py /main_app.py
COPY main_requirements.txt /requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "main_app.py"]
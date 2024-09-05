FROM python
LABEL authors="fafulja"

COPY main_config.py /main_config.py
COPY main_models.py /main_models.py
COPY main_app.py /main_app.py
COPY main_requirements.txt /requirements.txt
COPY role_check.py /role_check.py
COPY solidity /solidity
COPY migrations /migrations
COPY main_solidity.py /main_solidity.py

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "main_app.py"]
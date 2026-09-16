FROM apache/airflow:3.1.7

RUN pip install --no-cache-dir \
    apache-airflow-providers-mysql \
    pymysql
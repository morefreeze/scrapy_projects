# coding: utf-8
from os import path
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
import datetime


def need_run(ti, execution_date, **kwargs):
    long_time = datetime.timedelta(days=1, hours=20)
    if ti.start_date and execution_date and ti.start_date - execution_date < long_time:
        return 'run_spider'
    return ''

dir = path.abspath(path.dirname(path.realpath(__file__)))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 7, 24),
    'email': ['morefreeze@gmail.com', ],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 3,
    'retry_delay': datetime.timedelta(minutes=5),
    'queue': 'bash_queue',
    'provide_context': True,
    'retry_exponential_backoff': True,
    # 'end_date': datetime.datetime(2017, 1, 1),
}

dag = DAG('lianjia2', default_args=default_args, schedule_interval='@weekly')


only_run_now = BranchPythonOperator(
    task_id='only_run_now',
    python_callable=need_run,
    dag=dag
)
bj_code = 110000
output_dir = 'bj{{ ds_nodash }}'
run_spider = BashOperator(
    task_id='run_spider',
    bash_command='cd {dir} && ./run.sh {bj_code} "{output_dir}" '.format(dir=dir, bj_code=bj_code, output_dir=output_dir),
    dag=dag
)

import_db = BashOperator(
    task_id='import_db',
    bash_command='cd {dir} && ./import_db.sh "{output_dir}" '.format(dir=dir, output_dir=output_dir),
    dag=dag,
)

only_run_now >> run_spider >> import_db

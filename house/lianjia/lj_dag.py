# coding: utf-8
from os import path
from airflow import DAG
from airflow.operators import BashOperator, BranchPythonOperator
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
    'start_date': datetime.datetime(2017, 5, 30),
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

dag = DAG('lianjia', default_args=default_args, schedule_interval='@daily')


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

only_run_now >> run_spider

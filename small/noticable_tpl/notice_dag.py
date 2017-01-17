# coding: utf-8
from os import path, environ
from StringIO import StringIO
from airflow import DAG
from airflow.operators import BashOperator, BranchPythonOperator, PythonOperator, SlackAPIPostOperator
from utils import period2timedelta, money2float
from filter import Filter
import datetime
import pandas as pd


# This store text that will sent by slack
slack_message_key = 'slack_message'
# This store data file which maybe checked
csv_file = 'xy.csv'
dir = path.abspath(path.dirname(__file__))


# If now() - execution_date >= long_time, spider won't run.
def need_run(ti, execution_date, **kwargs):
    long_time = datetime.timedelta(seconds=60*10)
    if ti.start_date and execution_date and ti.start_date - execution_date < long_time:
        return 'run_spider'
    return ''


def filter_data(csv_file, **kwargs):
    f = pd.read_csv(csv_file)
    candidate = []
    filter = Filter()
    filter.install_rule(lambda v: not v['title'].startswith('test'))
    for row in f.iterrows():
        idx, v = row
        item = {
            'title': v['title'],
        }
        if filter.check(item):
            candidate.append(item)
    return candidate


# If len(candicate) > 0 will send to slack, the text will store as slack_txt_file
def need_slack(ti, **kwargs):
    candidate = ti.xcom_pull(key=None, task_ids='filter_data')
    try:
        os.remove(slack_txt_file)
    except:
        pass
    if candidate and len(candidate) > 0:
        s = StringIO()
        for can in candidate:
            s.write('%s\n' % (
                can['title'],
            ))
        ti.xcom_push(slack_message_key, s.getvalue().decode('utf-8'))
        return 'post_slack'
    return ''


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 1, 5),
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

dag = DAG('xiaoying', default_args=default_args, schedule_interval='*/5 8-22 * * *')


only_run_now = BranchPythonOperator(
    task_id='only_run_now',
    python_callable=need_run,
    dag=dag
)
run_spider = BashOperator(
    task_id='run_spider',
    bash_command='cd {dir} && rm -f {csv_file} && scrapy runspider spiders/invest.py -t csv -o {csv_file}'.format(dir=dir, csv_file=csv_file),
    dag=dag
)

filter_data = PythonOperator(
    task_id='filter_data',
    python_callable=filter_data,
    op_args=(csv_file, ),
    dag=dag
)

need_slack = BranchPythonOperator(
    task_id='need_slack',
    python_callable=need_slack,
    dag=dag
)

slack_token = environ.get('SLACK_TOKEN')
txt = '''{{ task_instance.xcom_pull(task_ids='need_slack', key='%s') }}''' % (slack_message_key)
if txt is None:
    txt = 'Nothing to read'
post_slack = SlackAPIPostOperator(
    task_id='post_slack',
    token=slack_token,
    channel='#xiaoying',
    username='airflow',
    text='{{ execution_date }}\n' + txt,
    dag=dag
)

only_run_now >> run_spider >> filter_data >> need_slack >> post_slack

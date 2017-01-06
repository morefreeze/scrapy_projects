# coding: utf-8
from os import sys, path, environ, remove
from airflow import DAG
from airflow.operators import BashOperator, BranchPythonOperator, PythonOperator, SlackAPIPostOperator
from utils import period2timedelta, money2float
from filter import Filter
import datetime
import pandas as pd


slack_txt_file = 'txt_for_slack'
csv_file = 'xy.csv'
def filter_data(csv_file, start_day=28, end_day=90, interest=780, state=None, **kwargs):
    f = pd.read_csv(csv_file)
    f['sub_title'] = f['sub_title'].fillna('')
    candidate = []
    filter = Filter()
    filter.install_rule(lambda v: v['period'] < datetime.timedelta(days=20), ok_stop=True, weight=5)
    filter.install_rule(lambda v: v['benefit'] >= 8 and v['period'] < datetime.timedelta(days=230))
    filter.install_rule(lambda v: not v['sub_title'].startswith('新手专享'))
    for row in f.iterrows():
        idx, v = row
        money = money2float(v['money'])
        period = period2timedelta(v['period'])
        # remove percent sign(%)
        benefit = float(v['expected_benefit'][:-1])
        item = {
            'title': v['title'],
            'sub_title': v['sub_title'],
            'money': money,
            'period': period,
            'benefit': benefit,
        }
        if filter.check(item):
            candidate.append(item)
    return candidate


def need_slack(ti, **kwargs):
    candidate = ti.xcom_pull(key=None, task_ids='filter_data')
    try:
        os.remove(slack_txt_file)
    except:
        pass
    if len(candidate) > 0:
        print candidate
        with open(slack_txt_file, 'w') as f:
            for can in candidate:
                f.write('%s(%s) money: %s period: %s days benefit: %s%%\n' % (
                    can['title'],
                    can['sub_title'],
                    can['money'],
                    can['period'].days,
                    can['benefit']
                ))
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
    # 'end_date': datetime.datetime(2017, 1, 1),
}

dag = DAG('xiaoying', default_args=default_args, schedule_interval='*/5 8-22 * * *')

run_spider = BashOperator(
    task_id='run_spider',
    bash_command='cd /Users/freeze/scrapy_projects/small/small/ && rm -f {csv_file} && scrapy runspider spiders/invest.py -t csv -o {csv_file}'.format(csv_file=csv_file),
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

slack_token = environ.get('SLACK_ME_TOKEN')
try:
    with open(slack_txt_file, 'r') as f:
        txt = ''.join(f.readlines())
        txt = txt.decode('utf-8')
except:
    txt = 'Nothing to read.'
post_slack = SlackAPIPostOperator(
    task_id='post_slack',
    token=slack_token,
    channel='#xiaoying',
    username='airflow',
    text='{{ ds }}\n' + txt,
    dag=dag
)

run_spider >> filter_data >> need_slack >> post_slack

# coding: utf-8
import csv
import sys
import json
import datetime
import urllib
import urllib2
import time
import argparse
from tqdm import tqdm


bizcircle_url = 'http://ajax.lianjia.com/ajax/mapsearch/area/bizcircle?city_id={code}'
circle_url = 'http://ajax.lianjia.com/ajax/housesell/area/bizcircle?ids={ids}&limit_offset={cursor}&limit_count={step}&sort=&&city_id={code}'
ck_file = 'checkpoint'


def wget_lj(url, file=None, append=False):
    ts = int(time.time() * 1000)
    url += '&_={ts}'.format(ts=ts)
    content = urllib2.urlopen(url, timeout=15).read()
    if file:
        mode = 'a' if append else 'w'
        with open(file, mode) as f:
            f.write(content+'\n')
    return content


def load_checkpoint():
    start_cir_id = 0
    start_i = 0
    try:
        with open(ck_file, 'r') as f:
            start_cir_id = int(f.readline())
    except:
        pass
    return start_cir_id, start_i


def save_checkpoint(cir_id):
    with open(ck_file, 'w') as f:
        f.writelines([str(cir_id)])


def main():
    step = 200
    parser = argparse.ArgumentParser()
    parser.add_argument('city_code', nargs='?', default=110000, type=int, help='city code')
    args = parser.parse_args()
    city_code = args.city_code
    bizcircle = json.loads(wget_lj(bizcircle_url.format(code=city_code), file='bizcircle_%s.json' % (city_code)), encoding='utf-8')
    start_cir_id, start_i = load_checkpoint()
    start = (start_cir_id == 0)
    for cir in tqdm(bizcircle['data'], desc='bizcircle'):
        cir_id = cir['id']
        if not start:
            if cir_id == start_cir_id:
                start = True
            continue
        cir_name = cir['name']
        cir_cnt = cir['house_count']
        cir_ids = [str(cir_id)]
        circle_list = []
        file = '%s_%s.json' % (cir_id, cir_name)
        desc = 'circle detail [%s:%s]' % (cir_name, cir_id)
        for i in tqdm(range(0, cir_cnt, step), desc=desc):
            url = circle_url.format(ids=urllib.quote(','.join(cir_ids)), cursor=i, step=step, code=city_code)
            house_list = json.loads(wget_lj(url, file=file, append=True))['data']['list']
            circle_list.extend(house_list)
            time.sleep(0.2)
        time.sleep(2)
        save_checkpoint(cir_id)


if __name__ == '__main__':
    main()

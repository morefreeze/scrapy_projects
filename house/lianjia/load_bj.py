# coding: utf-8
import json
import pandas as pd


data = []
with open('bj/bizcircle_110000.json', 'r') as f:
    for line in f:
        data.extend(json.loads(line)['data'])
df = pd.DataFrame(data)
df.latitude = df.latitude.astype(float)
df.longitude = df.longitude.astype(float)
# 五环到三环之间，西起上地，东到来广营
lon1 = 116.195017
lon2 = 116.449957
lat1 = 39.975562
lat2 = 40.059
selected_community = df[(df.avg_unit_price<80000) & (lon1<df.longitude) & (df.longitude<lon2) & (lat1<df.latitude) & (df.latitude<lat2)][['name', 'id', 'avg_unit_price', 'house_count']]
data = []
for _, row in selected_community.iterrows():
    with open('bj/%s_%s.json' % (row['id'], row['name']), 'r') as f:
        for line in f:
            data.extend(json.loads(line)['data']['list'])
total_house = pd.DataFrame(data)
total_house.price_total = total_house.price_total.astype(float)
total_house.house_area = total_house.house_area.astype(float)
subway_data = []
for _, row in total_house.iterrows():
    d = row['subway_station'] if not pd.isnull(row['subway_station']) else {}
    subway_data.append(d)
subway = pd.DataFrame(subway_data)
subway = subway.fillna(0)
# 将规整后的地铁数据取出
for k in subway.keys():
    total_house[k] = subway[k]
selected_house = total_house[(total_house.price_total<=550) & (total_house.house_area>=75) & (total_house.frame_orientation.str.contains(u'南'))]
# is_restriction 过滤掉商住两用, is_five 取出满五年的
selected_house = selected_house[(~ selected_house.tags.str.contains('is_restriction')) & (selected_house.tags.str.contains('is_five'))]
near_subway = selected_house[(selected_house.distance_value<=1500) & (selected_house.distance_value>0)]
# 补上链家的url
near_subway['url'] = near_subway.house_code.apply(lambda x: 'http://bj.lianjia.com/ershoufang/%s.html' % (x))

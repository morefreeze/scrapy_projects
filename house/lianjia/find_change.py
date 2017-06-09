# coding: utf-8
import pymongo
import argparse
import datetime
import scrapy
import pprint
from settings import MONGO_DB, MONGO_URI


def _date(s):
    return datetime.datetime.strptime(s, '%Y%m%d').date()

def main():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--begin_date', required=False,
                        default=yesterday.strftime('%Y%m%d'), type=_date, help='the house whose day need be compared')
    parser.add_argument('-e', '--end_date', required=False,
                        default=None, type=_date, help='the house whose day need be compared')
    parser.add_argument('-d', '--dir', required=False, default='both', choices=['both', 'gt', 'lt'])
    args = parser.parse_args()
    begin_date = args.begin_date
    end_date = args.end_date or begin_date + datetime.timedelta(days=1)

    mongo_uri = MONGO_URI
    mongo_db = MONGO_DB
    client = pymongo.MongoClient(mongo_uri)
    db = client[mongo_db]
    tbl_name = 'bj%s' % end_date.strftime('%Y%m%d')
    cond = [{'house_price_history.0.time': {'$gte': '%s' % begin_date, '$lt': '%s' % end_date}},]
    if args.dir != 'both':
        cond.append(
            {'house_price_history.0.old_price': {'$%s' % args.dir: 'house_price_history.0.new_price'}}
        )
    q = db[tbl_name].find({'$and': cond})
    print q.count()
    # for house in q.find({'$and': cond}):
        # pprint.pprint(house)

if __name__ == "__main__":
    main()


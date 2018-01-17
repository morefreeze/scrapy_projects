# coding: utf-8
from __future__ import print_function
import sys
import os
import argparse
import re
import requests
import urlparse
from tqdm import tqdm


def get_mp4(url):
    r = requests.get(url)
    m = re.search(r'textarea name="video_embed_code[^>]+>([^<]+)</textarea>', r.content)
    if not m:
        return ''
    emb_url = m.group(1).strip()
    r = requests.get(emb_url)
    m = re.search(r'<source src="([^"]+.mp4[^"]+)"', r.content)
    if not m:
        return ''
    mp4_url = m.group(1).strip()
    return mp4_url

def download(url, output_dir):
    up = urlparse.urlparse(url)
    file_name = os.path.basename(up.path)
    r = requests.get(url, stream=True)
    total_length = int(r.headers.get('content-length', 0))
    with open(os.path.join(output_dir, file_name), 'wb') as f, tqdm(total=total_length, unit='B', unit_scale=True) as pbar:
        for data in r.iter_content(chunk_size=4096):
            f.write(data)
            pbar.update(4096)

def main():
    parser = argparse.ArgumentParser()
    mut_group = parser.add_mutually_exclusive_group(required=True)
    mut_group.add_argument('-c', '--code', nargs='*')
    mut_group.add_argument('-u', '--url', nargs='*')
    parser.add_argument('-od', '--output-dir', type=str)
    args = parser.parse_args()
    if args.code:
        urls = []
        for code in args.code:
            urls.append('https://51.caoxee.com/video/%s' % code)
    else:
        urls = args.url
    true_urls = map(get_mp4, urls)
    if args.output_dir:
        map(lambda url: download(url, args.output_dir), filter(lambda x: x != '', true_urls))
    else:
        map(print, true_urls)


if __name__ == '__main__':
    main()

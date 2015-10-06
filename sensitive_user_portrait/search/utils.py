# -*- coding:utf-8 -*-

import os
import time
import sys
import json

from sensitive_user_portrait.global_utils import es_sensitive_user_text as es_cluster
emotion_mark_dict = {'126': 'positive', '127':'negative', '128':'anxiety', '129':'angry'}

def sentiment_test(sentiment_dict):
    sentiment_dict = json.loads(sentiment_dict)
    if not sentiment_dict:
        return 'neutral'
    sentiment = {}
    sentiment['positive'] = len(sentiment_dict.get('126', {}))
    sentiment['negative'] = len(sentiment_dict.get('127', {}))
    sentiment['anxiety'] = len(sentiment_dict.get('128', {}))
    sentiment['angry'] = len(sentiment_dict.get('128', {}))

    positive = sentiment['positive']
    negetive = sentiment['negative'] + sentiment['anxiety'] + sentiment['angry']

    sorted_dict = sorted(sentiment.items(), key=lambda x:x[1], reverse=True)

    if sorted_dict[0][0] == 'positive':
        if positive > negetive:
            return 'positive'
        else:
            return 'negetive'
    else:
        return sorted_dict[0][0]


def ts2format_time(ts):
    ts = int(ts)
    format_time = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(ts))
    return format_time

def full_text_search(words_list):
    results = []
    query_body = {
        "query": {
            "bool": {
                "must": [
                ]
            }
        },
        'sort': {"timestamp": {'order': 'desc'}},
        'size': 500
    }

    for word in words_list:
        query_body['query']['bool']['must'].append({'wildcard':{'text':{'wildcard':'*'+word+'*'}}})
    search_results = es_cluster.search(index="sensitive_user_text", doc_type="user", body=query_body)['hits']['hits']
    for item in search_results:
        item = item['_source']
        item['timestamp'] = ts2format_time(item['timestamp'])
        item['sentiment'] = sentiment_test(item['sentiment'])
        results.append(item)

    return results
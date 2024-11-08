# coding=utf-8

import sys
import json
import base64
import time


# make it work in both python2 both python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# skip https auth
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = 'UQiE21Kp5g3leK5b0EdGCTSu'

SECRET_KEY = 'B4D4EYnVGYtJibvQ67CYeAWW8ADtkydN'


COMMENT_TAG_URL = "https://aip.baidubce.com/rpc/2.0/nlp/v2/comment_tag"

"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


"""
    get token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

"""
    call remote http server
"""
def make_request(url, comment):
    # print("---------------------------------------------------")
    # print("评论文本：")
    # print("    " + comment)
    # print("\n评论观点：")

    response = request(url, json.dumps(
    {
        "text": comment,
        # 13为3C手机类型评论，其他类别评论请参考 https://ai.baidu.com/docs#/NLP-Apply-API/09fc895f
        "type": 1
    }))

    data = json.loads(response)

    # if "error_code" not in data or data["error_code"] == 0:
    #     for item in data["items"]:
    #         # 积极的评论观点
    #         if item["sentiment"] == 2:
    #             print(u"    积极的评论观点: " + item["prop"] + item["adj"])
    #         # 中性的评论观点
    #         if item["sentiment"] == 1:
    #             print(u"    中性的评论观点: " + item["prop"] + item["adj"])
    #         # 消极的评论观点
    #         if item["sentiment"] == 0:
    #             print(u"    消极的评论观点: " + item["prop"] + item["adj"])
    # else:
    #     # print error response
    #     print(response)

    # 防止qps超限
    time.sleep(0.5)
    return data


"""
    call remote http server
"""
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)

if __name__ == '__main__':

    comment1 = "有5年没来普陀山   岛外岛内的变化很大  岛内风景更是优美  值得游玩   郑姣及另外一位导游对待每一位游客都很细心  做的每一件事情都是亲力亲为   耐心细致的讲解每一处的风景及典故    感谢两位高素质导游的辛苦陪伴 下次去还找你们"
    comment2 = "今年是第二次来普陀山了，这次导游是王杰，解说很详细且用心，行程安排的很到位，让我的这次祈福之旅体验感很好！希望明年还能遇到王杰导游…非常棒的小伙子！"

    # get access token
    token = fetch_token()

    # concat url
    url = COMMENT_TAG_URL + "?charset=UTF-8&access_token=" + token

    make_request(url, comment1)
    make_request(url, comment2)
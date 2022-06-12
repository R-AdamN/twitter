import base_module
import  tweepy
from collections import deque
import datetime
import touraku_judge_lightgbm_module
from collections import deque

touraku_dt_JST = datetime.datetime(2022,6,10,16,45)
delta_GMT_p9 = datetime.timedelta(hours=9)
touraku_dt_GMT = touraku_dt_JST - delta_GMT_p9

target_tlistname = ""
candidate_user_list = base_module.get_tlist_member(tlistname=target_tlistname)
api = base_module.get_api()
since_id = None
candidate_user_list = candidate_user_list[:10]
candidate_user_cnt = 0
rt_canfifate_id_list = []
rt_canfifate_text_list = []
fv_canfifate_id_list = []
fv_canfifate_text_list = []
rt_touraku_id_list = []
fv_touraku_id_list = []
rt_id_deque = deque([])
fv_id_deque = deque([])
ending_flg=False
while(ending_flg==False):
    print(candidate_user_cnt,'/',len(candidate_user_list))
    # 鍵垢だったらパス
    if(api.get_user(user_id=candidate_user_list[candidate_user_cnt]).protected==False):
        for tweet in tweepy.Cursor(api.user_timeline,user_id=candidate_user_list[candidate_user_cnt],since_id=since_id,include_rts=True,tweet_mode='extended').items():
            if(tweet.created_at<touraku_dt_GMT):
                since_id=tweet.id
                break
            if(tweet.retweeted==tweet.favorited==False):
                if(hasattr(tweet, "retweeted_status")):
                    if(tweet.retweeted_status.retweeted==tweet.retweeted_status.favorited==False):
                        if(tweet.retweeted_status.user.id not in candidate_user_list):
                            fv_canfifate_id_list.append(tweet.retweeted_status.id)
                            fv_canfifate_text_list.append(tweet.retweeted_status.full_text)
                else:
                    rt_canfifate_id_list.append(tweet.id)
                    rt_canfifate_text_list.append(tweet.full_text)
    candidate_user_cnt+=1
    if(len(rt_canfifate_id_list)>0 and len(fv_canfifate_id_list)>0):
        rt_touraku_id_list = touraku_judge_lightgbm_module.check(rt_canfifate_id_list,rt_canfifate_text_list)
        fv_touraku_id_list = touraku_judge_lightgbm_module.check(fv_canfifate_id_list,fv_canfifate_text_list)
    rt_canfifate_id_list = []
    rt_canfifate_text_list = []
    fv_canfifate_id_list = []
    fv_canfifate_text_list = []
    rt_id_deque.extend(rt_touraku_id_list)
    fv_id_deque.extend(fv_touraku_id_list)
    rt_rest_num = len(rt_id_deque)
    fv_rest_num = len(fv_id_deque)
    for rt_i in range(rt_rest_num):
        api.retweet(rt_id_deque.popleft())
    for fv_i in range(fv_rest_num):
        api.create_favorite(fv_id_deque.popleft())
    if(candidate_user_cnt>=len(candidate_user_list) and rt_rest_num==fv_rest_num==0):
        ending_flg=True

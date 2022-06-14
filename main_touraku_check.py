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
subject_user_list = base_module.get_tlist_member(tlistname=target_tlistname)
api = base_module.get_api()
since_id = None
max_id = None
# subject_user_list = subject_user_list[:10]
subject_user_cnt = 0
rt_canfifate_id_list = []
rt_canfifate_text_list = []
rt_canfifate_user_list = []
fv_canfifate_id_list = []
fv_canfifate_text_list = []
rt_touraku_id_list = []
fv_touraku_id_list = []
rt_touraku_user_list = []
rt_id_deque = deque([])
fv_id_deque = deque([])
rt_user = []
ending_flg=False
while(ending_flg==False):
    print(subject_user_cnt,'/',len(subject_user_list))
    get_tl_end = True
    # 鍵垢だったらパス
    if(api.get_user(user_id=subject_user_list[subject_user_cnt]).protected==False):
        #イテレータを作る
        for tweet in base_module.limit_catch_cursor(tweepy.Cursor(api.user_timeline,user_id=subject_user_list[subject_user_cnt],since_id=since_id,max_id=max_id,include_rts=True,tweet_mode='extended').items()):
            if(tweet=="end"):
                break
            if(tweet.created_at<touraku_dt_GMT):
                since_id=tweet.id
                break
            if(tweet.retweeted==tweet.favorited==False):
                if(hasattr(tweet, "retweeted_status")):
                    if(tweet.retweeted_status.retweeted==tweet.retweeted_status.favorited==False):
                        if(tweet.retweeted_status.user.id not in subject_user_list):
                            fv_canfifate_id_list.append(tweet.retweeted_status.id)
                            fv_canfifate_text_list.append(tweet.retweeted_status.full_text)
                else:
                    rt_canfifate_id_list.append(tweet.id)
                    rt_canfifate_text_list.append(tweet.full_text)
                    rt_canfifate_user_list.append(tweet.user.id)
        # 制限に達して終了したら
        else:
            max_id = tweet.id
            get_tl_end = False
    #最後まで取得出来たら次のユーザに
    if(get_tl_end):
        subject_user_cnt += 1
        max_id = None

    if(len(rt_canfifate_id_list)>0 and len(fv_canfifate_id_list)>0):
        rt_touraku_id_list,rt_touraku_user_list = touraku_judge_lightgbm_module.check(rt_canfifate_id_list,rt_canfifate_text_list,rt_canfifate_user_list)
        fv_touraku_id_list,dump = touraku_judge_lightgbm_module.check(fv_canfifate_id_list,fv_canfifate_text_list)
    rt_canfifate_id_list = []
    rt_canfifate_text_list = []
    rt_canfifate_user_list = []
    fv_canfifate_id_list = []
    fv_canfifate_text_list = []
    rt_id_deque.extend(rt_touraku_id_list)
    fv_id_deque.extend(fv_touraku_id_list)
    rt_user += rt_touraku_user_list
    while(len(rt_id_deque)>0):
        rt_id = rt_id_deque.popleft()
        try:
            api.retweet(rt_id)
        except tweepy.RateLimitError as e:
            rt_id_deque.appendleft(rt_id)
            break
        except tweepy.error.TweepError as e:
            pass
    while(len(fv_id_deque)>0):
        fv_id = fv_id_deque.popleft()
        try:
            api.create_favorite(fv_id)
        except tweepy.RateLimitError as e:
            fv_id_deque.appendleft(fv_id)
            break
        except tweepy.error.TweepError as e:
            pass
    if(subject_user_cnt>=len(subject_user_list) and len(rt_id_deque)==len(fv_id_deque)==0):
        ending_flg=True

touraku_not_found_user = list(set(subject_user_list)-set(rt_user))
print(touraku_not_found_user)
base_module.make_tlist("",touraku_not_found_user)

import pandas as pd
import numpy as np
import collections
import MeCab
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import pickle


def check(tweet_id_list,text_list,user_list=None):
    if(user_list==None):
        user_list = [None]*len(tweet_id_list)
    touraku_tweet = []
    touraku_user = []
    l = [tweet_id_list,text_list,user_list]
    judge_num = len(l[0])
    l.append([0 for i in range(judge_num)])
    l_np = np.array(l).T
    columns = ['tweet_id', 'body', "user", 'touraku']
    # col = "touraku"
    df_judge = pd.DataFrame(data=l_np, columns=columns)

    indices = np.loadtxt('../model/data/indices.csv', delimiter=',')
    feature_ds = pd.read_pickle('../model/data/touraku_feature_ds.plk')
    model = pickle.load(open('../model/touraku_model.pkl', 'rb'))

    m = MeCab.Tagger("")
    # それぞれの文書を取り出して形態素解析
    length_list = []
    text_list = []
    for sentence in df_judge["body"]:
        ma = m.parse(sentence)
        word_list = []
        # 形態解析後の単語だけ抽出
        for text in ma.split("\n"):
            word_list.append(text.split("\t")[0])
        #　単語の数を集計
        length_list.append(len(word_list))
        # 単語の頻度を集計
        data = collections.Counter(word_list)
        text_data = pd.DataFrame.from_dict(data, orient='index')
        # text_data = text_data.fillna(0)
        text_list.append(text_data)

    feature = pd.concat([feature_ds]+text_list, axis=1)
    #Nanを０に置換
    feature = feature.fillna(0)

    ## 各文書に対して全体で頻出の上位k個の単語の出現数をその文書の単語出現数で割ったものを変数とする ##
    modi_feature = []
    for index, row in feature.iloc[indices].T[-judge_num:].reset_index(drop=True).iterrows():
        modi_feature_temp = row/length_list[index]
        modi_feature.append(modi_feature_temp)
    modi_feature = pd.concat(modi_feature, axis=1).T
    # 各文書と作成した特徴量を結合
    df_judge_feature = pd.concat([df_judge, modi_feature], axis=1)
    # df_judge_feature = df_judge_feature.drop(["tweet_id", "body"], axis=1)
    # judge_x = df_judge_feature.drop(col, axis=1)
    judge_x = df_judge_feature.drop(columns, axis=1)


    judge = model.predict(judge_x)
    for i,result in enumerate(judge):
        if(result>0.5):
            touraku_tweet.append(df_judge['tweet_id'][i])
            touraku_user.append(df_judge["user"])
            # print(df_judge['body'][i])
    return touraku_tweet,touraku_user

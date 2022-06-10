import tweepy
import csv


def get_my_key():
    csv_file=open("../key/key.csv","r",encoding="ms932",errors="",newline="")
    f=csv.reader(csv_file,delimiter=",",doublequote=True,lineterminator="¥r¥n",quotechar='"',skipinitialspace=True)

    list=[]

    for row in f:
        list.append(row[0])

    consumer_key        = list[0]
    consumer_secret     = list[1]
    access_token        = list[2]
    access_token_secret = list[3]

    return consumer_key,consumer_secret,access_token,access_token_secret


def get_api():
    consumer_key,consumer_secret,access_token,access_token_secret = get_my_key()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return api

def get_myname():
    f = open("../myname.txt", "r")
    myname = f.read()
    f.close()

    return myname

def get_tlist_member(username=None,tlistname):
    if(username==None):
        myname = get_myname()
    tlist_members_list = []
    api = get_api()
    for member in tweepy.Cursor(api.list_members,slug=listname,owner_screen_name=myname).items():
        tlist_members_list.append(member.id)
    return(tlist_members_list)


def make_tlist(tlistname, members):
    api = get_api()
    myname = get_myname()

    makeflg=1

    for j in api.lists_all(screen_name=myname):
        if(j.name==listname):
            makeflg=0
            existing_members = [l[1] for l in get_tlist_member(tlistname)]
            members = list(set(members) - set(existing_members))

    if makeflg:
        api.create_list(name=makelist_name,mode="private")

    # pprint(member)
    for l in members:
        if(api.get_user(id=l).protected!=True):
            try:
                api.add_list_member(
                                    list_id=get_list(owner=myname, slug=tlistname).id,
                                    id=l,
                                    owner_screen_name=myname
                                    )
            except tweepy.error.TweepError as e:
                print(l)
                print(e['message'])

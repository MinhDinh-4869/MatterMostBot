#merge-request-approvals channel id: i96ar759678ypbs8szsoyfsu9r
#APEX team id: iy53wydmit8wtyyhis83gpni6o
#SAI team id: s1pkgqt4xida3p6bo38kg9oa9c
#SAI build channel: zjx3u71su3g7ujabr5jerwdqqr
from MattermostManger import MattermostManager as MM
import datetime

if __name__ == '__main__' :
    mmM = MM()
    userid = mmM.mmDriver.users.get_user_by_email('luan.nguyen@gameloft.com')['id']
    messages = []
    shouldStopFetching = False
    pageNo = 0
    mmM.mmDriver.channels
    while not shouldStopFetching:
        posts = mmM.mmDriver.posts.get_posts_for_channel('i96ar759678ypbs8szsoyfsu9r', params={
        'page': str(pageNo),
    })
        for postId, value in posts['posts'].items():
            if value['user_id'] == userid:
                messages.append(value['message'])
                if datetime.datetime.now() - datetime.datetime.fromtimestamp(int(value['create_at'])/1000) > datetime.timedelta(days=30):
                    shouldStopFetching = True
                    break
                print(value['message'])
        pageNo+=1
            
    print(datetime.datetime.fromtimestamp(1696490770991/1000))



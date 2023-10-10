#merge-request-approvals channel id: i96ar759678ypbs8szsoyfsu9r
#APEX team id: iy53wydmit8wtyyhis83gpni6o
#SAI team id: s1pkgqt4xida3p6bo38kg9oa9c
#SAI build channel: zjx3u71su3g7ujabr5jerwdqqr
from BotManager import BotManager
import datetime

SAI_MEMBERS = ['lam.tranvan', 'luan.nguyen', 'minh.dinhcong', 'dung.nguyenquoc3', 'huy.buidang', 'loc.vovan', 'nghia.tranhuu', 'thach.nguyenngoc3', 'bao.nguyenngogia', 'thao.tranngan', 'anh.nguyenduy2','quang.phantri',
               'hieu.nguyentrung10', 'phuc.vohuynhhoang', 'minh.phannhat', 'quan.luungoc', 'quan.letruong', 'kien.nguyenluong', 'hen.tranvan', 'vien.phamphu', 'arnau.font','julia.gasull']
if __name__ == '__main__' :
    bot = BotManager()
    while(True):
        if bot.IsBotTriggered() :
            print('bot triggered')
            mrs = bot.GetAllMergeRequest(author_usernames=SAI_MEMBERS, state='opened', target_branch='b_1.3.5a')
            bot.SendMergeRequestStatusToMattermost()
        bot.Update()
        print('%s waiting for signal...'%datetime.datetime.astimezone(datetime.datetime.now()))
    #mrs = bot.GetAllMergeRequest(author_usernames=SAI_MEMBERS, target_branch='b_1.3.5a')
    #bot.SendMergeRequestStatusToMattermost(merge_requests=mrs)
            



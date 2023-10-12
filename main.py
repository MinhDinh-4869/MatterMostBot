#merge-request-approvals channel id: i96ar759678ypbs8szsoyfsu9r
#APEX team id: iy53wydmit8wtyyhis83gpni6o
#SAI team id: s1pkgqt4xida3p6bo38kg9oa9c
#SAI build channel: zjx3u71su3g7ujabr5jerwdqqr
from turtle import update
from BotManager import BotManager
import datetime

#MM_BUILDCHANNEL = 'zjx3u71su3g7ujabr5jerwdqqr'
SAI_MEMBERS = ['lam.tranvan', 'luan.nguyen', 'minh.dinhcong', 'dung.nguyenquoc3', 'huy.buidang', 'loc.vovan', 'nghia.tranhuu', 'thach.nguyenngoc3', 'bao.nguyenngogia', 'thao.tranngan', 'anh.nguyenduy2','quang.phantri',
               'hieu.nguyentrung10', 'phuc.vohuynhhoang', 'minh.phannhat', 'quan.luungoc', 'quan.letruong', 'kien.nguyenluong', 'hen.tranvan', 'vien.phamphu', 'hoang.vodinh', 'kien.lengoc', 'hieu.dotri2']
if __name__ == '__main__' :
    bot = BotManager()
    while(True):
        botResult = bot.IsBotTriggered()
        if botResult[0] == 'status' and botResult[1] != 'none':
            print('Getting status on branch %s'%(botResult[1]))
            bot.GetAllMergeRequest(state='opened', target_branch=botResult[1])
        elif botResult[0] in ['update', 'reset']:
            bot.Update()
        elif botResult[0] == 'off':
            break
        print('%s waiting for signal...'%datetime.datetime.astimezone(datetime.datetime.now()))
    bot.TurnedOffBot()
    print("Bot turned off")
            



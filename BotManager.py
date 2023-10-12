from operator import truediv
from GitlabManager import GitlabManager
from MattermostManger import MattermostManager

GL_TOKEN = 'glpat-d44ao3DZL-iLJX3hME_X'
GL_HOST = 'https://git.gameloft.org/'
PROJECT_ID = 5608
MM_BUILDCHANNEL= 'zjx3u71su3g7ujabr5jerwdqqr'
MM_TESTCHANNEL= 'w5mb3pm65f8axe5e9prozkdhcc'
MM_DEFAULTCHANNEL = MM_BUILDCHANNEL
MM_AUTHORID = '1znesrbpopgxtkmztocqr9tzuo' #minh.dinhcong
MM_AUTHORIZEDUSER = ['minh.dinhcong@gameloft.com',  'dung.nguyenquoc3@gameloft.com', 'luan.nguyen@gameloft.com', 'hen.tranvan@gameloft.com', 'vien.phamphu@gameloft.com', 'nghia.tranhuu@gameloft.com']
SAI_MEMBERS = ['lam.tranvan', 'luan.nguyen', 'minh.dinhcong', 'dung.nguyenquoc3', 'huy.buidang', 'loc.vovan', 'nghia.tranhuu', 'thach.nguyenngoc3', 'bao.nguyenngogia', 'thao.tranngan', 'anh.nguyenduy2','quang.phantri',
               'hieu.nguyentrung10', 'phuc.vohuynhhoang', 'minh.phannhat', 'quan.luungoc', 'quan.letruong', 'kien.nguyenluong', 'hen.tranvan', 'vien.phamphu', 'hoang.vodinh', 'kien.lengoc', 'hieu.dotri2']

class BotManager:
    def __init__(self):
        self.mmM = MattermostManager()
        self.glM = GitlabManager(GL_HOST, GL_TOKEN)
        self.project = self.glM.gl.projects.get(PROJECT_ID)
        self.mergeRequests = []
        self.Post = None
        self.iids = []
        self.lastMessage = ''
        self.AuthorizedUser = []
        for email in MM_AUTHORIZEDUSER:
            user = self.mmM.mmDriver.users.get_user_by_email(email)
            #print('%s %s'%(email, user['id']))
            self.AuthorizedUser.append(user['id'])
    
    def GetAllMergeRequest(self,state='opened', target_branch=None):
        post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'Bot Triggered! Getting merge requests...'})
        if self.Post != None: 
            self.mmM.mmDriver.posts.unpin_post_to_channel(self.Post['id'])
            self.Post = None
        self.mergeRequests = []
        self.iids = []  
        #self.mergeRequests+=self.project.mergerequests.list(state = state, author_username = user, target_branch=target_branch, iterator=True)
        mrs = self.project.mergerequests.list(state = state, target_branch=target_branch, iterator=True)
        for mr in mrs:
            if mr.author['username'] in SAI_MEMBERS and mr.draft == False:
                self.mergeRequests.append(mr)
                self.iids.append(mr.iid)
        self.mmM.mmDriver.posts.update_post(post['id'], options={'id': post['id'], 'channel_id': MM_DEFAULTCHANNEL, 'message': 'Merge requests query finished! Sending status...'})
        self.SendMergeRequestStatusToMattermost()

    def ProcessMergeRequestToSend(self, merge_request):
        status = 'Opening'
        icon = ':pixel-loading:'
        if merge_request.state == 'closed':
            #print(merge_request.web_url)
            return ''
        mr_approvals = merge_request.approvals.get()
        if int(mr_approvals.approvals_left) == 0:
            if mr_approvals.state == 'merged':
                status = 'Merged'
                icon = ':done:'
            else:
                status = 'Can be merged'
                icon = ':alert:'
        #return '\n|[%s](%s)|@%s|%s %s|'%(merge_request.title, merge_request.web_url, merge_request.author['username'],status, icon )
        return '\n|[%s](%s)|[%s](https://chat.gameloft.org/sai/messages/@%s)|%s %s|'%(merge_request.title, merge_request.web_url, merge_request.author['username'],merge_request.author['username'],status, icon )
    
    def SendMergeRequestStatusToMattermost(self, channel_id=MM_DEFAULTCHANNEL):
        if len(self.mergeRequests) < 1:
            self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'No opened merge requests!'})
            return -1
        res = '|merge request|author|status|\n|:-----|:-----|:------|'
        for mr in self.mergeRequests:
            res+=self.ProcessMergeRequestToSend(mr)
        self.Post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': res})#, 'root_id': self.TriggerThreadId
        self.mmM.mmDriver.posts.pin_post_to_channel(self.Post['id'])
    
    def UpdateMergeRequestStatusInMattermost(self, channel_id=MM_DEFAULTCHANNEL):
        res = '|merge request|author|status|\n|:-----|:-----|:------|'
        for mr in self.mergeRequests:
            res+=self.ProcessMergeRequestToSend(mr)
        if self.Post != None:
            self.mmM.mmDriver.posts.update_post(self.Post['id'], options={'id': self.Post['id'], 'channel_id': MM_DEFAULTCHANNEL, 'message': res, 'is_pinned': True})
    
    def IsBotTriggered(self, channel_id=MM_DEFAULTCHANNEL):
        message = self.mmM.mmDriver.posts.get_posts_for_channel(channel_id=channel_id, params = {
            'page' : str(0),
            'per_page' : 1,
        })
        for id, value in message['posts'].items():
            if self.lastMessage == value['message']:
                self._SpamWarning()
                return tuple(['update', 'none'])
            message = value['message'].split(' ')
            if message[0] == '!bot-linh' and value['user_id'] in self.AuthorizedUser and len(message) > 1:
                if message[1].strip() == 'status':
                    target_branch = 'none'
                    if len(message) > 2:
                        target_branch = message[2]
                    return tuple(['status', target_branch])
                elif message[1].strip() == 'reset':
                    post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'Reseting...'})
                    if self.Post != None: 
                        self.mmM.mmDriver.posts.unpin_post_to_channel(self.Post['id'])
                        self.Post = None
                        self.mergeRequests = []
                        self.iids = []  
                    self.mmM.mmDriver.posts.update_post(post['id'], options={'id': post['id'], 'channel_id': MM_DEFAULTCHANNEL, 'message': 'Done!'})             
                    return tuple(['reset', 'none'])  
                elif message[1].strip() == 'off' and value['user_id'] == MM_AUTHORID:
                    return tuple(['off', 'none'])
                elif message[1].strip() == 'help':
                    self._SendHelp()
                    return tuple(['update', 'none'])
                self.lastMessage = value['message']   
            elif message[0].strip() == '!bot-linh' and value['user_id'] not in self.AuthorizedUser:
                return tuple(['update', 'none'])
        return tuple(['update', 'none'])
    
    def Update(self):
        if len(self.iids) > 0:
            self.mergeRequests = self.project.mergerequests.list(iids=self.iids, iterator=True)
            self.UpdateMergeRequestStatusInMattermost()

    def TurnedOffBot(self):
        post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'Turning off...'})
        if self.Post != None:
            self.mmM.mmDriver.posts.unpin_post_to_channel(self.Post['id'])
            self.Post = None
            self.mergeRequests = []  
            self.iids = []   
        self.mmM.mmDriver.posts.update_post(post['id'], options={'id': post['id'], 'channel_id': MM_DEFAULTCHANNEL, 'message': 'Done!'})

    def _SendHelp(self):
        self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': '```!bot-linh status [target branch]```: get status\n```!bot-linh reset```: reset bot\n```!bot-linh help```: send help'})       

    def _SpamWarning(self):
        self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'No Spam!'})
    
    def _UnauthorizedUserWarning(self):
        self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'No Permission!'})

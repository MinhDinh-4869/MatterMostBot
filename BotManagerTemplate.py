from operator import truediv
from GitlabManager import GitlabManager
from MattermostManger import MattermostManager
import json
import os.path

GL_TOKEN = ''
GL_HOST = ''
PROJECT_ID = 0
MM_BUILDCHANNEL= ''
MM_TESTCHANNEL= ''
MM_DEFAULTCHANNEL = MM_TESTCHANNEL
MM_AUTHORID = ''
MM_BLACKLISTUSER = []
SAI_MEMBERS = []


class BotManager:
    def __init__(self):
        self.mmM = MattermostManager()
        self.glM = GitlabManager(GL_HOST, GL_TOKEN)
        self.project = self.glM.gl.projects.get(PROJECT_ID)
        #self.mergeRequests = []
        #self.Post = None
        #self.iids = []
        self.lastMessage = ''
        self.blackList = []
        self.Post = None
        self.iids = []
        self.blackList = []
        self.mergeRequests = []
        #read for json file
        if os.path.exists('last_session.json'):
            self.file_handle = open('last_session.json', 'r')
            data = json.load(self.file_handle)
            self.iids = data['mr_iids']
            self.blackList = data['blacklist']
            self.mergeRequests = self.project.mergerequests.list(iids=self.iids, iterator=True)
            if data['post_id'] != None:
                self.Post = self.mmM.mmDriver.posts.get_post(data['post_id'])
                self.UpdateMergeRequestStatusInMattermost()
            self.file_handle.close()
        else:
            data_to_write = {
                "mr_iids" : [],
                "blacklist":[],
                "post_id": None
            }
            self.file_handle = open('last_session.json','w')
            self.file_handle.write(json.dumps(data_to_write))
            self.file_handle.close()
        #for email in MM_BLACKLISTUSER:
        #    user = self.mmM.mmDriver.users.get_user_by_email(email)
        #    #print('%s %s'%(email, user['id']))
        #    self.blackList.append(user['id'])
        self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'Bot Ready!'})
    
    def __del__(self):
        self._SerializeData()
        print('bot died')
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
        messages = self.mmM.mmDriver.posts.get_posts_for_channel(channel_id=channel_id, params = {
            'page' : str(0),
            'per_page' : 1,
        })
        for id, value in messages['posts'].items():
            message = value['message'].split(' ')
            if message[0].strip() == '!bot-linh' and len(message) > 1 and value['user_id'] not in self.blackList:
                match message[1].strip():
                    case 'status': 
                        if message[-1] != 'status':
                            return tuple(['status', message[-1]])
                    case 'reset': 
                        self._ResetBot()
                    case 'off':
                        if value['user_id'] == MM_AUTHORID:
                            return tuple(['off', 'none'])
                    case 'help':
                        self._SendHelp()
                    case 'blacklist':
                        if value['user_id'] == MM_AUTHORID and len(message) > 2:
                            self._BlacklistUser(message[2:])
        return tuple(['update', 'none'])
    
    def Update(self):
        if len(self.iids) > 0:
            self.mergeRequests = self.project.mergerequests.list(iids=self.iids, iterator=True)
            self.UpdateMergeRequestStatusInMattermost()

    def TurnedOffBot(self):
        post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'Turning off...'})
        if self.Post != None:
            self.mmM.mmDriver.posts.unpin_post_to_channel(self.Post['id']) 
        self.mmM.mmDriver.posts.update_post(post['id'], options={'id': post['id'], 'channel_id': MM_DEFAULTCHANNEL, 'message': 'Done!'})

    def _SendHelp(self):
        self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': '```!bot-linh status [target branch]```: get status\n```!bot-linh reset```: reset bot\n```!bot-linh help```: send help'})       

    def _SpamWarning(self):
        self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'No Spam!'})
    
    def _UnauthorizedUserWarning(self):
        self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'No Permission!'})
    
    def _SerializeData(self):
        self.file_handle = open('last_session.json', 'w')
        id = None
        if self.Post != None:
            id = self.Post['id']
        data = {
                "mr_iids" : self.iids,
                "blacklist":self.blackList,
                "post_id":id
            }
        self.file_handle.write(json.dumps(data))
        self.file_handle.close()
    
    def _ResetBot(self):
        post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'Reseting...'})
        if self.Post != None: 
            self.mmM.mmDriver.posts.unpin_post_to_channel(self.Post['id'])
            self.Post = None
            self.mergeRequests = []
            self.iids = []  
        self.mmM.mmDriver.posts.update_post(post['id'], options={'id': post['id'], 'channel_id': MM_DEFAULTCHANNEL, 'message': 'Done!'})
    
    def _BlacklistUser(self, emails):
        post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_DEFAULTCHANNEL, 'message': 'Blacklisting...'})
        for email in emails:
            self.blackList.append(self.mmM.mmDriver.users.get_user_by_email(email)['id'])
        self.mmM.mmDriver.posts.update_post(post['id'], options={'id': post['id'], 'channel_id': MM_DEFAULTCHANNEL, 'message': 'Done!'})


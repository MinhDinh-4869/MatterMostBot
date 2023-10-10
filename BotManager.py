from operator import truediv
from GitlabManager import GitlabManager
from MattermostManger import MattermostManager

GL_TOKEN = 'glpat-yuf_saDF2MVDUxwEhm3L'
GL_HOST = 'https://git.gameloft.org/'
PROJECT_ID = 5608
MM_TESTCHANNEL = 'w5mb3pm65f8axe5e9prozkdhcc'

class BotManager:
    def __init__(self):
        self.mmM = MattermostManager()
        self.glM = GitlabManager(GL_HOST, GL_TOKEN)
        self.project = self.glM.gl.projects.get(PROJECT_ID)
        self.mergeRequests = []
        self.Post = None
        self.iids = []
    
    def GetAllMergeRequest(self,state='opened', author_usernames=[], target_branch=None):
        for user in author_usernames:
            self.mergeRequests+=self.project.mergerequests.list(state = state, author_username = user, target_branch=target_branch, iterator=True)
            for mr in self.mergeRequests:
                self.iids.append(mr.iid)

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
        return '\n|[%s](%s)|@%s|%s %s|'%(merge_request.title, merge_request.web_url, merge_request.author['username'],status, icon )
    
    def SendMergeRequestStatusToMattermost(self, channel_id=MM_TESTCHANNEL):
        res = '|merge request|author|status|\n|:-----|:-----|:------|'
        for mr in self.mergeRequests:
            res+=self.ProcessMergeRequestToSend(mr)
        self.Post = self.mmM.mmDriver.posts.create_post(options={'channel_id': MM_TESTCHANNEL, 'message': res})
        self.mmM.mmDriver.posts.pin_post_to_channel(self.Post['id'])
        print(self.Post)
    
    def UpdateMergeRequestStatusInMattermost(self, channel_id=MM_TESTCHANNEL):
        res = '|merge request|author|status|\n|:-----|:-----|:------|'
        for mr in self.mergeRequests:
            res+=self.ProcessMergeRequestToSend(mr)
        if self.Post != None:
            self.mmM.mmDriver.posts.update_post(self.Post['id'], options={'id': self.Post['id'], 'channel_id': MM_TESTCHANNEL, 'message': res, 'is_pinned': True})
    
    def IsBotTriggered(self, channel_id='w5mb3pm65f8axe5e9prozkdhcc'):
        message = self.mmM.mmDriver.posts.get_posts_for_channel(channel_id=channel_id, params = {
            'page' : str(0),
            'per_page' : 1,
        })
        for id, value in message['posts'].items():
            if(value['message'] == 'trigger_bot'):
                if self.Post != None: 
                    self.mmM.mmDriver.posts.unpin_post_to_channel(self.Post['id'])
                    self.Post = None
                    self.mergeRequests.clear()                
                return True
        return False
    
    def Update(self):
        #loops = len(self.mergeRequests)
        #for _ in range(loops):
        #    self.mergeRequests+=[self.project.mergerequests.get(self.mergeRequests[0].iid)]
        #    self.mergeRequests.pop(0)
        if len(self.iids) > 0:
            self.mergeRequests = self.project.mergerequests.list(iids=self.iids, iterator=True)
            self.UpdateMergeRequestStatusInMattermost()

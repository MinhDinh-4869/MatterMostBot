import logging
import datetime
from mattermostdriver import Driver

logging.basicConfig(format='%(levelname)s - %(name)s - %(asctime)s - %(message)s')
logger = logging.getLogger('MattermostManager')
logger.setLevel(logging.INFO)

TOKEN = 'zzqedc3wjpra5kh859zh8qchkc'
testEmail = 'minh.dinhcong@gameloft.com'
#merge-request-approvals channel id: i96ar759678ypbs8szsoyfsu9r
#APEX team id: iy53wydmit8wtyyhis83gpni6o
#SAI team id: s1pkgqt4xida3p6bo38kg9oa9c
#SAI build channel: zjx3u71su3g7ujabr5jerwdqqr
class MattermostManager() :
    def __init__( self ) :        
        mmHost = 'chat.gameloft.org'
        logger.debug( "Going to set up driver for connection to %s " % (mmHost,) )

        self.mmDriver = Driver( options={
            'url'    : mmHost,
            'scheme' : 'https',
            'port'   : 443,
            'token'   : TOKEN, 
        } )
        
        self.mmDriver.login()
        self.mmDriver.users.get_user( user_id='me' ) 
    
    def GetCurrentUserTeamId(self, teamName):
        teams = self.mmDriver.teams.get_user_teams( user_id='me' )
        for team in teams:
            if team['display_name'] == teamName:
                return team['id']
        return 'TeamNotFound'

    def GetCurrentUserChannelId(self, channelName, teamName):
        channels = self.mmDriver.channels.get_channels_for_user(user_id = 'me', team_id = self.GetCurrentUserTeamId(teamName))    
        for channel in channels: 
            if channel['display_name'] == channelName:
                return channel['id']
        return 'ChannelNotFound'
    
    def GetUserIds(self, channelId):
        UserIds = []
        members = self.mmDriver.channels.get_channel_members(channelId)
        for member in members:
            UserIds.append(member['user_id'])
        return UserIds
    
#    def GetUsersInChannelByTimezone(self, channelId, timeZone):
        users = []
        userIds = self.GetUserIds(channelId)
        for id in userIds:
            user = self.mmDriver.users.get_user(id)
            if(user['timezone']['automaticTimezone'] == timeZone):
                users.append(user)
        return users   
     
    def GetUsersInChannelsByTimezone(self, userIds, timeZone):
        users = []
        for id in userIds:
            user = self.mmDriver.users.get_user(id)
            if(user['timezone']['automaticTimezone'] == timeZone):
                users.append(user['id'])
        return users
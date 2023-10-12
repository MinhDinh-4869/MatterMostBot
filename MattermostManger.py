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

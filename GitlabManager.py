import gitlab
#glpat-2_MnoZwXjHtAUtCmU-4U
#glpat-qz64BsDZpWwandbA29vf
PRIVATE_TOKEN = 'glpat-2_MnoZwXjHtAUtCmU-4U'


#projects = gl.projects.list(iterator=True)

#project = gl.projects.get(id=51080045)
#mrs = project.mergerequests.list()F


class GitlabManager():
    def __init__(self):
        self.gl = gitlab.Gitlab(private_token='glpat-2_MnoZwXjHtAUtCmU-4U')
        self.gl.auth()

    

glM = GitlabManager()
project = glM.gl.projects.get(51080045)
mrs = project.mergerequests.list()
for mr in mrs:
    if(mr.target_branch == 'main'):
        print(mr.title)
        print(mr.web_url)
        print(mr.merge_status)
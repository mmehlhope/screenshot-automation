from requests import Session
from time import sleep

class RestClient(object):
    def __init__(self, user, apikey):
        self.user = user
        self.apikey = apikey

    #function to edit the environment runstate
    def check_and_edit_envs(self, envs_to_run, runstate):

        ### functions used by check_and_edit_envs ###
        # function to check the environment runstate
        def in_desired_runstate(runstate, get_url, session):
            response = session.get(get_url)
            json_output = json.loads(response.text)
            # if environment is in desired runstate, return true
            if json_output['runstate'] == runstate:
                print('Environment ' + env + ' is ' + runstate + '.')
                return True

        # function to change the environment runstate
        def change_runstate(runstate, put_url, session):
            params = {'runstate': runstate}
            response = session.put(put_url, params=params)
            json_output = json.loads(response.text)
            if response.status_code == 200:
                print('Environment ' + env + ' is switching to ' + runstate + '.')
                recheck_runstate(runstate, put_url, session)
            else:
                print('Error: Environment ' + env + ' is NOT ' + runstate + '.')
                print('Error code: {0}'.format(response.status_code))

        # function to continually recheck the environment until it is in the desired runstate.
        def recheck_runstate(runstate, get_url, session):
            sleep(10)
            if in_desired_runstate(runstate, get_url, session):
                return
            else:
                recheck_runstate(runstate, get_url, session)
                print 'Environment ' + env + ' is switching to ' + runstate + '.'

        ### start check_and_edit_envs here ###

        if len(envs_to_run) > 0:
            print "Checking the runstate of " + str(len(envs_to_run)) + " environment(s)"

            # start the API session
            session = Session()
            session.auth = (self.user, self.apikey)
            session.headers = {"Accept": "application/json",
                                "Content-type": "application/json"}

            # check the credentials
            auth_test = session.get(baseURL + "/account") # Try a get against account
            authed = False if auth_test.status_code == 401 else True

            # exit if the credentials are not valid, continue if they are
            if not authed:
                print('API credentials are incorrect, response code: {0}'.format(auth_test.status_code))
                print('Check the admin username and API key and try again')
                sys.exit()
            else:
                # loop through envs. check if they are already in the desired runstate; edit them if they are not
                for env in envs_to_run:
                    get_url = "{0}{1}/{2}".format(baseURL, "/configurations", env)
                    put_url = "{0}.json".format(get_url)
                    if in_desired_runstate(runstate, get_url, session):
                        return
                    else:
                        change_runstate(runstate, put_url, session)

# this script does prep work for phantomjs.
# it takes a long list of possible screenshots and organizes breaks that up into lists of relevant screenshots for phantomjs to work with.
# a screenshot is considered "relevant" if it matches a CLI argument passed into this script
# this script can also start and suspend Skytap environments if an environment needs to be running for a screenshot

# dependencies
import csv
import json
import os
import sys
from requests import Session
from time import sleep


### hard-coded information ###
# hard-coded number of images that should be processed in one run
chunksize = 35

# hard-coded info used to run environments and for initial account login by phantomjs script
baseURL = "https://cloud.skytap.com"

class SkytapUser(object):
    _registry = []
    
    def __init__(self, name, username, password, apikey):
        # create a new user
        self._registry.append(self)
        self.name = name
        self.username = username
        self.password = password
        self.apikey = apikey
        self.screenshotlist = []


class ProcessCSV(object):
    def __init__(self, csvname, listfromcsv): 
        self.csvname = csvname 
        self.listfromcsv = []        
        with open(self.csvname, 'rU') as f:
            self.listfromcsv = [{k: str(v) for k, v in row.items()}
                for row in csv.DictReader(f, skipinitialspace=True)]
    
    # function to read the list data and filter it into smaller lists to be used by the rest of the script
    def filter_screenshots(self, filter_name, envs_to_run):
        
        ### internal functions used by filter_screenshots ###
        # function to add environment to envs_to_run list
        def add_to_envs_to_run(env):
            if len(env) > 0 and env not in envs_to_run:
                envs_to_run.append(env)
                return envs_to_run
        
        # function to add screenshot to appropriate screenshot list    
        def add_to_screenshots_to_take(screenshot):
            screenshot_user_name = screenshot['permissionLevel']
            for user in SkytapUser._registry:
                if screenshot_user_name == user.name:
                    user.screenshotlist.append(screenshot)
            return user.screenshotlist
                
        for screenshot in self.listfromcsv:
            if filter_name in (screenshot['cliname'], screenshot['group']):
                add_to_envs_to_run(screenshot['run'])
                add_to_screenshots_to_take(screenshot)
        return envs_to_run

   
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

def generate_screenshots(user, filter_name):
    if len(user.screenshotlist) > chunksize:
        run_in_chunks(user, filter_name)
    else:
        switch_to_PhantomJS(filter_name, user.screenshotlist, user.username, user.password)

def run_in_chunks(user, filter_name):
    chunks = [user.screenshotlist[x:x+chunksize] for x in xrange(0, len(user.screenshotlist), chunksize)]
    print "breaking into " + str(len(chunks)) + " batches"
    chunknum = 0
    for chunk in chunks:
        print "starting batch #" + str(chunknum)
        switch_to_PhantomJS(filter_name, chunk, user.username, user.password)
        chunknum = chunknum + 1
        print "pausing for 20 seconds"
        sleep(20)

#create a JSON file; pass this and the user credentials along to phantomJS.
def switch_to_PhantomJS(filter_name, listname, username, password):
    #create a text file with the CLI flag name
    fname = os.path.join(filter_name+".json")  
    #add any relevant screenshots to that json file
    with open(fname, 'w') as outfile:
        json.dump(listname, outfile)
    
    #use the CLI to run the phantomJS script
    newsyscommand = "phantomjs screenshotsJS.js " + baseURL + " " + username + " " + password + " " + filter_name
    print "SWITCH TO PHANTOM JS________"
    os.system(newsyscommand)

def main():
    # read in the system argument and store it as a variable; exit if an argument is not provided    
    if (len(sys.argv) < 2):
        print "Please enter a 'cliname' or 'group' attribute from the .csv file"
        exit()
    else:
        filter_name = sys.argv[1]

    # add users the phantomJS script can use to log into Skytap as
    # uncomment lines as needed and replace "instertusername", "insertpassword", "") with the correct username, password, and API token.
    # user = SkytapUser("user", "insertusername", "insertpassword", "")
    admin = SkytapUser("admin", "insertusername", "insertpassword", "")
    
    # read from .csv file to create a list of all possible screenshots
    allscreenshots = []
    allscreenshots = ProcessCSV('allscreenshots.csv', allscreenshots)
    
    #filter down screenshots based on system argument filter name
    envs_to_run = []
    envs_to_run = allscreenshots.filter_screenshots(filter_name, envs_to_run)
    
    # run environments as admin, if needed
    if envs_to_run > 0:
        rest_client = RestClient(admin.username, admin.apikey)
        rest_client.check_and_edit_envs(envs_to_run, "running")
    
    # for each skytap user, use PhantomJs to log into Skytap as the user and take a series of screenshots
    for user in SkytapUser._registry:
        print user.name
        print user.screenshotlist
        if len(user.screenshotlist) > 0:
            generate_screenshots(user, filter_name)

    # suspend environments as admin, if needed        
    if envs_to_run > 0:
        rest_client.check_and_edit_envs(envs_to_run, "suspended")
    
    exit

if __name__ == "__main__":
    main()
    
        
            
    



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

### uncomment if you want to use multiple account logins
#userUsername = "yourusename"
#userPassword = "yourpassword"

adminUsername = "yourusernamehere"
adminPassword = "yourpasswordhere"
adminAPItoken = "yourAPItokenhere"

# hard-coded number of images that should be processed in one run
chunksize = 35

# hard-coded info used to run environments and for initial account login by phantomjs script
baseURL = "https://cloud.skytap.com"
res_env = "/configurations"
res_acc = "/account"

# lists that will be populated by the script
userScreenshots = []
adminScreenshots = []
envstoRun = []
okaysysargs = []


##### functions related to verifying system arguments #####
# function to generate a list of valid system arguments (system argument is used to determine relevant screenshots)
def makelistofValidArgs():
    for screenshot in allscreenshots:
        if screenshot['cliname'] not in okaysysargs :
            okaysysargs.append(screenshot['cliname'])
        if screenshot['group'] not in okaysysargs:
            okaysysargs.append(screenshot['group'])

# check if an invalid system argument was provided; if not, exit the script
def checkforValidArg():
    # if a flag was not provided by the user or an invalid option was provided, print a list of valid arguments
    if (len(sys.argv) < 2) or (sys.argv[1] not in okaysysargs):
        print "Enter a screenshot list to generate. Choose from:"
        for p in okaysysargs: print p 
        sys.exit()

##### functions related to starting and stopping environments ##### 
# function to generate a list of environments that need to be run
def makelistofEnvstoRun():
    if screenshot['run'] and screenshot['run'] not in envstoRun:
        envstoRun.append(screenshot['run'])

#create API session
def create_session(username, key):
    session = Session()
    session.auth = (username, key)
    session.headers = {"Accept": "application/json",
                        "Content-type": "application/json"}
    return session

# use API session to run or suspend environments
def editenvrunstate(runstate, user, api_key):
    # start and test the API session
    api_session = create_session(user, api_key)
    auth_test = api_session.get(baseURL + res_acc) # Try a get against account
    authed = False if auth_test.status_code == 401 else True
    if not authed:
        print('Credentials incorrect, response code: {0}'.format(auth_test.status_code))
        print('Check your username/api key and try again')
        sys.exit()
    
    # manage runstate of each environment
    params = {'runstate': runstate}
    for env in envstoRun:
        statusChange = 0
        get_url = "{0}{1}/{2}".format(baseURL, res_env, env)
        put_url = "{0}.json".format(get_url)
       
        # function to change the environment runstate
        def changeRunstate():
            if statusChange < 1:
                response = api_session.put(put_url, params=params)
                json_output = json.loads(response.text)  
        
        # funciton to check the environment runstate.        
        def checkRunstate():
            response = api_session.get(get_url)
            json_output = json.loads(response.text)
            # if environment is in desired runstate, move on.
            if json_output['runstate'] == runstate:
                print('Environment ' + env + ' is ' + runstate + '.')        
            # if environment is not in desired runstate, do other things
            else:
                #change the environment runstate. this should only happen once per env.
                changeRunstate()
                #if request was successful but environment is still busy, keep checking the runstate until the environment is in desired state
                if response.status_code == 200:
                    statusChange = 1
                    print('Environment ' + env + ' is switching to ' + runstate + '.')
                    sleep(10)
                    checkRunstate()
               #if the request was not successful, print the error message.
                else:
                    print('Error: Environment ' + env + ' is NOT ' + runstate + '.')
                    print('Error code: {0}'.format(response.status_code))    
        checkRunstate()       

# run environments
def runEnvironments():
    # run the environments as the admin
    if len(envstoRun) > 0:  
        # print the list of environments to run
        print "List of envs to run: "
        for envs in envstoRun: print envs
        editenvrunstate("running", adminUsername, adminAPItoken)
    else: print "No environments to run."

# suspend the environments 
def suspendEnvironments():
    if len(envstoRun) > 0:  
        editenvrunstate("suspended", adminUsername, adminAPItoken)
    else:
        print "No environments to suspend."

##### functions related to handing off relevant screenshot lists to phantomJS script ##### 
# create a more specific .json file with a list of screenshots that phantomJS must generate.
def createScreenshotFile(listname):
    # create a text file with the CLI flag name
    fname = os.path.join(sys.argv[1]+".json")  
    # add any relevant screenshots to that json file
    with open(fname, 'w') as outfile:
        json.dump(listname, outfile)

# pass this file info and the user credentials along to phantomJS.
def startPJS(username, password):
    # use the CLI to run the phantomJS script. pass along arguments from this script
    newsyscommand = "phantomjs screenshotsJS.js " + baseURL + " " + username + " " + password + " " + sys.argv[1]
    print "SWITCH TO PHANTOM JS________"
    os.system(newsyscommand)

def breakintochunks(listname, uname, pword):
    chunks = [listname[x:x+chunksize] for x in xrange(0, len(listname), chunksize)]
    print "breaking into " + str(len(chunks)) + " batches"
    chunknum = 0
    for chunk in chunks:
        print "starting batch #" + str(chunknum)
        createScreenshotFile(chunk)
        startPJS(uname, pword)
        chunknum = chunknum + 1
        print "pausing for 20 seconds"
        sleep(20)

# pass along lists to PhantomJS
def switchtoPJS():
    #if there are any screenshots to generate with user permissions, pass that along to phantomjs
    if len(userScreenshots) > 0:
        if len(userScreenshots) > chunksize:
            breakintochunks(userScreenshots, userUsername, userPassword)
        else:
            createScreenshotFile(userScreenshots)
            startPJS(userUsername, userPassword)   
    #if there are any screenshots to generate with admin permissions, pass that along to phantomjs
    if len(adminScreenshots) > 0:
        if len(adminScreenshots) > chunksize:
            breakintochunks(adminScreenshots, adminUsername, adminPassword)
        else:
            createScreenshotFile(adminScreenshots)
            startPJS(adminUsername, adminPassword) 

##### !!!!!!!!!!!! #####
##### start script #####
with open('allscreenshots.csv', 'rU') as f:
    allscreenshots = [{k: str(v) for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]
makelistofValidArgs()
checkforValidArg()
for screenshot in allscreenshots:
    if (sys.argv[1] == screenshot['cliname'] or sys.argv[1] == screenshot['group']):
        makelistofEnvstoRun()
        if screenshot['permissionLevel'] == "user":
            userScreenshots.append(screenshot)
        if screenshot['permissionLevel'] == "admin":
            adminScreenshots.append(screenshot)
runEnvironments()
switchtoPJS()
suspendEnvironments()
    
exit
#_______    
        
            
    



# this script does prep work for phantomjs.
# it takes a long list of possible screenshots and organizes breaks that up into lists of relevant screenshots for phantomjs to work with.
# a screenshot is considered "relevant" if it matches a CLI argument passed into this script
# this script can also start and suspend Skytap environments if an environment needs to be running for a screenshot

# py system
import json
import os
import sys
from time import sleep

sys.path.append('./lib/py') # Enable 'import' search local directories
from skytap_user import SkytapUser
from process_csv import ProcessCSV
from rest_client import RestClient


# hard-coded number of images that should be processed in one run
IMAGE_CHUNK_SIZE = 35

# Skytap User Credentials
SKYTAP_LOGIN_URL = "https://cloud.skytap.com"
SKYTAP_USER_ROLE = "admin"
SKYTAP_USER_NAME = "username"
SKYTAP_USER_PASS = "password"
SKYTAP_API_TOKEN = "apitoken"

def generate_screenshots(user, filter_name):
    if len(user.screenshotlist) > IMAGE_CHUNK_SIZE:
        run_in_chunks(user, filter_name)
    else:
        switch_to_PhantomJS(filter_name, user.screenshotlist, user.username, user.password)

def run_in_chunks(user, filter_name):
    chunks = [user.screenshotlist[x:x+IMAGE_CHUNK_SIZE] for x in xrange(0, len(user.screenshotlist), IMAGE_CHUNK_SIZE)]
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
    newsyscommand = "phantomjs screenshotsJS.js " + SKYTAP_LOGIN_URL + " " + username + " " + password + " " + filter_name
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
    admin = SkytapUser(SKYTAP_USER_ROLE, SKYTAP_USER_NAME, SKYTAP_USER_PASS, SKYTAP_API_TOKEN)

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







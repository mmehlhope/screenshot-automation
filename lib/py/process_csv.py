import csv
from skytap_user import SkytapUser

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

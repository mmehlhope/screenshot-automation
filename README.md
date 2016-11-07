# screenshot-automation

## Overview
The "screenshot automation script" uses PhantomJS and Python to take a series of screenshots in your Skytap account and save the screenshots to your local machine. It can run environments, loop through a series of screenshots as a logged in Skytap user, and then suspend any environments that it ran.

The "screenshot automation script" is composed of 3 files:
* allscreenshots.csv
The .csv contains the list of all possible screenshots and data about them. 
* screenshotsPY.py
  The .py file is a wrapper (of sorts) that does all of the initial data manipulation and REST API calls. It narrows down the list of screenshots to take (based on a command line argument), sorts them into relevant screenshot lists by user role, starts environments, passes data along to the PhantomJS scripts (and runs that script as many times as needed), and then suspends environments.
* screenshotsJS.js
  The .js file signs into Skytap and loops through the list of relevant screenshots. For each screenshot, PhantomJS:
  * Loads the page in a defined browser windows size (docs and videos use different screen sizes)
  * Clicks, highlights, and/or crops to any elements as requested
  * Takes the screenshot and saves it to a local folder

# Installing the Screenshot Automation Script
1. Install Python 2.7 (https://www.python.org/downloads/) and the Requests python library (http://docs.python-requests.org/en/master/user/install/#install) 
TIP: Python may already be installed on Mac. To verify installation, type `python` at the command line
2. Install PhantomJS 2.1 (http://phantomjs.org/). 
  For example, on a Mac:
  - Download the .zip installation archive from http://phantomjs.org/.
  - Extract the contents. Rename the extracted folder to something simple (example: phantomjs).
  - Place this folder along your home path (example: /Users/username/phantomjs)
  - Add the directory containing the phantomJS.exe (for example, on my machine the file is located at: /Users/username/phantomjs/bin/phantomjs.exe)  to your OS environment variable PATH (for example, add it your bash_profile file [~/.bash_profile] and then reload the bash_profile file). 
  - Verify PhantomJS installation at the command line: `phantomjs --version`
3. Open the screenshotsPY.py file and edit the `admin = SkytapUser` line to include the username, password, and API token for a Skytap account you want the script to use. For example: `admin = SkytapUser("admin", "insertusername", "insertpassword", "")`

# Generating a set of screenshots
1. From the command line, navigate to the location where you saved the script files.
2. Type ```python screenshotsPY.py <argument>.```
   The argument can either be a **cliname** attribute from any of the screenshots in the .csv file, or it can be a **group** attribute from any of the screenshots in the .csv file. For example, ```videos```, ```docs```, ```video_buildfirstenv```, ```used```, and ```notused``` are all valid arguments based on the the sample .csv file included with this project.
3. This script will run and save your screenshots to folders in the location you ran the script from.


# Adding a new screenshot to the list
To add a new screenshot to the list of screenshots, add a new line to the allscreenshots.csv file. 

For each screenshot, enter the following properties:

| Column name   | Explanation           | Example  |
| :------------- |:-------------| :-----|
| pageURL (required) | This is the page that PhantomJS should navigate to. Generally, this is page you’ll be taking a screenshot of.     | https://cloud.skytap.com/configurations/1234567?sort=name&thumbnails=shown |
| imgname (required)     | Name of the image file. PhantomJS will automatically add ".png" to the end of the image.     |   scr-env-main-details |
| click | If PhantomJS should click something, enter the DOM element for PhantomJS to click. If there are multiple matching DOM elements, PhantomJS will click the first one.     |    button.toggle-multi-select-mode  |
| highlight | If PhantomJS should highlight something, enter the DOM element for PhantomJS to highlight. If there are multiple matching DOM elements, PhantomJS will highlight the first one.     |    div.filtering-options  (NOTE: This part of the script executes after click, which is useful for highlighting items in new dialog windows) |
| crop | If PhantomJS should crop the screenshot to show just an element on this page, enter the DOM element that PhantomJS should crop the image to. As usual, if there are multiple of these, PhantomJS will use the first one.   |    div#content  (NOTE: This part of the script executes after click, which is useful for cropping to new dialog windows) |
| cliname (required) | This is the command line argument name that you will use to generate this screenshot. To run a set of screenshots together from the script, give them the same cliname.  |   new  |
| permissionLevel (required) | Permission level of the screenshot user. The script is currently configured to log in as one of two users: user or admin.  |  admin  |
| group (required)  | Used to generate all of the doc or all of the video screenshots from one command. Also used to indicate the screen resolution size. The script is currently configured to use "docs" or "videos" |  docs  |
| run  |If the screenshot needs a running environment, enter the environment ID here. The script will start the environment before taking screenshot and then suspend the environment after taking screenshots.  |  1234567  |

# Suggestions
* Use the Chrome Javascript console to test out a DOM element. For example, you can preview what a highlight willl look like or what PhantomJS will actually try to click on. This can help avoid troubleshooting later. 

# Important Notes
* Skytap does not guarantee that DOM element names, classes, IDs, etc. will remain static each release.

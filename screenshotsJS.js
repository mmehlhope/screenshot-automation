// Helfpul refs:
// http://j4n.co/blog/batch-rendering-screenshots-with-phantomjs
// http://stackoverflow.com/questions/15356219/passing-variable-into-page-evaluate-phantomjs

// Script requirements. don't touch!
var system        = require('system'),
    Page          = require('./lib/js/phantom_page'),
    ParseJsonFile = require('./lib/js/parse_json_file'),
    args          = system.args,
    baseURL       = args[1],
    username      = args[2],
    password      = args[3],
    fname         = args[4],
    URLS          = ParseJsonFile(fname),
    urlIndex      = 0;

// Open a new phantomJS browser window
Page.open(baseURL, function (status) {

    // log in to Skytap by placing values in the appropriate DOM elements and clicking the Sign in button
    Page.evaluate(function(username, password) {
        document.getElementById("userLoginName").value = uname;
        document.getElementById("userLoginPassword").value = pword;
        document.getElementsByClassName("action-button")[0].click();
    }, username, password);


    // once logged in, loop through Skytap pages and manipulate them as defined in the URLs list
    setTimeout(function () {

       // perform the first action that happens once the page is loaded.
        var firstClick = function(page){
            // if an element on the page needs to be clicked, do that
            if (URLS[urlIndex].click) {
                var selector = URLS[urlIndex].click;
                console.log("Clicking: "+selector);
                Page.evaluate(function(selector) {
                    document.querySelectorAll(selector)[0].click();
                }, selector);
            }
        }

        //start related actions that will take the screenshot
        var renderPage = function(page,reswidth,resheight){

            //set the default screenshot size; this is overriden later if you are cropping to a DOM element
            Page.clipRect = {top:0,left:15,width:reswidth,height:resheight};

            console.log("Replacing text in screenshots");

            Page.evaluate(function() {

                //sanitize the screenshot text if needed.
                document.body.innerHTML = document.body.innerHTML.replace(/(oldtext)/g,"newtext");

                //hide alert and informational banners
                // move page contents to account for moving the screenshot 15px to the left earlier in the script
                //check if the page is on the old stack or new stack and then manipulate the appropriate elements
                var productElement = document.getElementById("inner_container");
                if (productElement != null) {
                    document.querySelectorAll("div#site_message")[0].style.display = "none";
                    document.querySelectorAll("div#inner_container")[0].style.marginLeft = "15px";
                } else {
                    document.querySelectorAll("div.alerts")[0].style.display = "none";
                    document.querySelectorAll("div#main")[0].style.marginLeft = "15px";
                };

            });

            //if this is a partial screenshot, crop to a specific DOM element (overrides default screenshot size defined earlier)
            if (URLS[urlIndex].crop) {
                console.log("This is a partial screenshot");
                var s = URLS[urlIndex].crop;
                console.log("selectorName is " +  URLS[urlIndex].crop)
                var clipRect = Page.evaluate(function(s){
                    return document.querySelector(s).getBoundingClientRect();
                    }, s);

                Page.zoomFactor = 1;

                Page.clipRect = {
                    top:    clipRect.top,
                    left:   clipRect.left,
                    width:  clipRect.width,
                    height: clipRect.height
                };

            };

            //highlight element, if needed
            if (URLS[urlIndex].highlight) {
                //Define highlight border style
                var borderStyle = "thick solid red";
                var sh = URLS[urlIndex].highlight;
                console.log("Highlighting: "+sh);
                var clipRect = Page.evaluate(function(sh,borderStyle){
                    document.querySelectorAll(sh)[0].style.background = "yellow";
                    }, sh,borderStyle);
            }

            //actually take the screenshot
            Page.render(URLS[urlIndex].cliname+"/"+URLS[urlIndex].imgname+".png");
            console.log("rendered:", URLS[urlIndex].imgname+".png")

        }


        //main function to loop through
        var takeScreenshot = function(element) {
            console.log("opening URL:", element)
            var page = require("webpage").create();
            //set the default screenshot size based on whether this is a doc screenshot or a video screenshot
            if (URLS[urlIndex].group == "docs") {
                var reswidth = 1024;
                var resheight = 764;
                }
            else if (URLS[urlIndex].group == "videos") {
                var reswidth = 1280;
                var resheight = 720;
            }
            Page.viewportSize = {width:reswidth+15, height:resheight};
            //open the URL
            Page.open(element);
            console.log("waiting for page to load...")
            //start working when the page is loaded
            Page.onLoadFinished = function() {
                console.log("page is loaded")
                //manipulate the page
                firstClick(page)
                //setTimeout(function(){
                //    doMoreThings(page)
                setTimeout(function(){
                    //take the screenshot
                    renderPage(page,reswidth,resheight)
                    console.log(URLS.length - urlIndex-1, "more screenshots in this set!")
                    console.log("~~~~~~~~~~~~~~")
                    //if there are more screenshots in the list, repeat this process
                    if (URLS.length - urlIndex > 1) {
                        urlIndex++;
                        console.log(URLS[urlIndex].pageURL);
                        takeScreenshot(URLS[urlIndex].pageURL);
                    }
                    //if there aren't any more screenshots in the list, exit phantomjs
                    else {
                        console.log("exiting phantomjs");
                        phantom.exit();
                    }
                }, 5000);
            };
        }

        //first action in the script. starts loop to take screenshots.
        takeScreenshot(URLS[urlIndex].pageURL);

    }, 5000);
});


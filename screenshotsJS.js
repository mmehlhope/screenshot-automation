//helfpul refs:
//http://j4n.co/blog/batch-rendering-screenshots-with-phantomjs
//http://stackoverflow.com/questions/15356219/passing-variable-into-page-evaluate-phantomjs

//script requirements. don't touch! 
var page = require('webpage').create();
var system = require('system');
var args = system.args;
var fs = require('fs');

//read command line arguments passed in through the python script. 
var baseURL = args[1];
var username = args[2];
var password = args[3];
var fname = args[4];

//open a new phantomJS browser window
page.open(baseURL, function (status) {
page.includeJs("http://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js", function() {    
                   
    //convert the .json file that python created into a list that this script can use
    function pullURLSObjectFromFile(urlfilename) {
        var content = fs.read(urlfilename);
        return JSON.parse(content);                    
    }
                
    var URLS = pullURLSObjectFromFile(fname+".json");

    //craete local variables for username and pword
    var uname = username;
    var pword = password;
    
    //log in to Skytap by placing values in the appropriate DOM elements and clicking the Sign in button
    page.evaluate(function(uname, pword) {
            document.getElementById("userLoginName").value = uname;
            document.getElementById("userLoginPassword").value = pword;
            document.getElementsByClassName("action-button")[0].click();
        }, uname, pword);
    
    
    //once logged in, loop through Skytap pages and manipulate them as defined in the URLs list
    setTimeout(function () {
        

       //perform the first action that happens once the page is loaded.              
        var firstClick = function(page){               
            //if an element on the page needs to be clicked, do that
            if (URLS[index].click) {
                var clickName = URLS[index].click;
                console.log("Clicking: "+clickName);
                page.evaluate(function(clickName) {
                    document.querySelectorAll(clickName)[0].click();
                }, clickName);

            }                                                        
        }
       
        //start related actions that will take the screenshot
        var renderPage = function(page,reswidth,resheight){
            
            //set the default screenshot size; this is overriden later if you are cropping to a DOM element
            page.clipRect = {top:0,left:15,width:reswidth,height:resheight};
            
            console.log("Replacing text in screenshots");
            
            page.evaluate(function() {
                
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
            if (URLS[index].crop) {
                console.log("This is a partial screenshot");
                var s = URLS[index].crop;
                console.log("selectorName is " +  URLS[index].crop)
                var clipRect = page.evaluate(function(s){
                    return document.querySelector(s).getBoundingClientRect();
                    }, s);
              
                page.zoomFactor = 1;
                
                page.clipRect = {
                    top:    clipRect.top,
                    left:   clipRect.left,
                    width:  clipRect.width,
                    height: clipRect.height
                };
                
            };
            
            //highlight element, if needed
            if (URLS[index].highlight) {
                //Define highlight border style
                var borderStyle = "thick solid red";
                var sh = URLS[index].highlight;
                console.log("Highlighting: "+sh);
                var clipRect = page.evaluate(function(sh,borderStyle){
                    document.querySelectorAll(sh)[0].style.background = "yellow";
                    }, sh,borderStyle);
            }
            
            //actually take the screenshot
            page.render(URLS[index].cliname+"/"+URLS[index].imgname+".png");
            console.log("rendered:", URLS[index].imgname+".png")
                                                   
        }       
        

        //main function to loop through  
        var takeScreenshot = function(element) {     
            console.log("opening URL:", element)
            var page = require("webpage").create();
            //set the default screenshot size based on whether this is a doc screenshot or a video screenshot
            if (URLS[index].group == "docs") {
                var reswidth = 1024;
                var resheight = 764;
                }
            else if (URLS[index].group == "videos") {
                var reswidth = 1280;
                var resheight = 720;
            }
            page.viewportSize = {width:reswidth+15, height:resheight};
            //open the URL
            page.open(element); 
            console.log("waiting for page to load...")
            //start working when the page is loaded
            page.onLoadFinished = function() {
                console.log("page is loaded")
                //manipulate the page
                firstClick(page)
                //setTimeout(function(){
                //    doMoreThings(page)
                setTimeout(function(){
                    //take the screenshot
                    renderPage(page,reswidth,resheight)
                    console.log(URLS.length - index-1, "more screenshots in this set!")
                    console.log("~~~~~~~~~~~~~~")   
                    //if there are more screenshots in the list, repeat this process
                    if (URLS.length - index > 1) {
                        index++;
                        console.log(URLS[index].pageURL);
                        takeScreenshot(URLS[index].pageURL);
                    }
                    //if there aren't any more screenshots in the list, exit phantomjs
                    else {
                        console.log("exiting phantomjs");
                        phantom.exit();
                    }
                }, 5000);
                //}, 5000);
            };
        }
        var index = 0;
    
        //first action in the script. starts loop to take screenshots.
        takeScreenshot(URLS[index].pageURL);
        
    }, 5000);
    });
});


var page = require('webpage').create();
var system = require('system');
var ROOTDIR = "/home/henry/pyLogger";
/*
var env = system.env;
Object.keys(env).forEach(function(key) {
  console.log(key + '=' + env[key]);
});
*/

var args = system.args;

if (args.length >= 2) {
  page.viewportSize = { width: 800, height: 600};
  
  page.open(args[1], function    (status) {
      if (status !== 'success') {
          console.log('Unable to load the address!');
      } else {
        
          page.evaluate(function() {
            document.body.style.margin = "0";
          });        
          // extract element by ID
          if (args.length === 3) {
            var bb = page.evaluate(function (id) { 
                return document.getElementById(id).getBoundingClientRect(); 
            }, args[2]);
            
            page.clipRect = {
                top:    bb.top,
                left:   bb.left,
                width:  bb.width,
                height: bb.height
            };
          }
          else {
            page.clipRect = { top: 0, left: 0, width: 800, height: 600 };
          }
          //console.log('rendering to'+ROOTDIR+'/out.png');  
          page.render(ROOTDIR+'/out.png');
          phantom.exit();
/*        
          window.setTimeout(function () {
          }, 200);
*/  
      }
  });  

/*  
  page.open(system.args[1], function(status) {
    console.log(system.args[1] + ": "+status);
    if(status === "success") {
      page.render('out.png');
    }
    phantom.exit();
  });
*/
}
else {
  console.log("custom");
  page.viewportSize = { width: 800, height: 600};
  page.clipRect = { top: 0, left: 0, width: 800, height: 600 };
  page.content = "Hello World";
  page.setContent(page.content, page);
  page.onLoadFinished = function(status) {
    console.log("ready");
    if(status === "success") {
      page.render(ROOTDIR+'/out.png');
    }
    phantom.exit();
  };  
}



<html>
<head>
    <title>Andy Ajax Polling</title>
    <script src="http://code.jquery.com/jquery-latest.min.js" type="text/javascript" charset="utf-8"></script>

    <style type="text/css" media="screen">
      body{ background:#000;color:#fff;font-size:.9em; }
      .msg{ background:#aaa;padding:.2em; border-bottom:1px #000 solid}
      .old{ background-color:#246499;}
      .new{ background-color:#3B9957;}
    .error{ background-color:#992E36;}
    </style>

    <script type="text/javascript" charset="utf-8">
    function addmsg(type, msg){
        /* Simple helper to add a div.
        type is the name of a CSS class (old/new/error).
        msg is the contents of the div */
        $("#messages").prepend(
            "<div class='msg "+ type +"'>"+ msg +"</div>"
        );
    }

    function waitForMsg(){
        /* This requests the url when it complete (or errors)*/
        $.ajax({
            type: "GET",
            url: window.location.origin+"/ajax_info1",

            async: true, /* If set to non-async, browser shows page as "Loading.."*/
            cache: false,
            timeout:50000, /* Timeout in ms */

            success: function(data){ /* called when request to barge.php completes */
                addmsg("new", data); /* Add response to a .msg div (with the "new" class)*/
                setTimeout(
                    'waitForMsg()', /* Request next message */
                    1000 /* ..after 1 seconds */
                );
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                addmsg("error", textStatus + " (" + errorThrown + ")");
                setTimeout(
                    'waitForMsg()', /* Try again after.. */
                    "15000"); /* milliseconds (15seconds) */
            },
        });
    };

    $(document).ready(function(){
        waitForMsg(); /* Start the inital request */
    });
    </script>
</head>
<body>
    <div id="messages">
        <div class="msg old">
            Andy's ajax call logger
        </div>
    </div>
</body>
</html>

function editWidget(widget_ID, host) {
	var winProps = "width=850,height=600,titlebar=0,toolbar=0,location=0,menubar=0,scrollbars=1,resizable=1,channelmode=0,directories=0,status=1";
	window.open("http://"+host+"/cms/popup.cfm?methodId=113&popup=1&wid=" + widget_ID, "widgetEditor", winProps, true);
}
function editContent(content_id) {
	var winProps = "width=800,height=570,titlebar=0,toolbar=0,location=0,menubar=0,scrollbars=1,resizable=1,channelmode=0,directories=0,status=1";
	window.open("/cms/popup.cfm?methodId=8&popup=1&id=" + content_id, "contentEditor", winProps, true);

}
function popUpWindow(theURL, width, height) {
	var winProps = "width=" + width + ",height=" + height;
	winProps += ",titlebar=0,toolbar=0,location=0,menubar=0,scrollbars=1,resizable=1,channelmode=0,directories=0,status=1";
	window.open(theURL,"popUp",winProps,true);
}
function popUpNoResize(theURL, width, height) {
		var winProps = "width=" + width + ",height=" + height;
		winProps += ",titlebar=0,toolbar=0,location=0,menubar=0,scrollbars=1,resizable=0,channelmode=0,directories=0,status=1";
		window.open(theURL,"popUp",winProps,true);
}
function popUpNoScroll(theURL, width, height) {
	var winProps = "width=" + width + ",height=" + height;
	winProps += ",titlebar=0,toolbar=0,location=0,menubar=0,scrollbars=0,resizable=1,channelmode=0,directories=0,status=1";
	window.open(theURL,"popUp",winProps,true);
}
function emailCheck(emailStr) {
	/*  author: Sandeep V. Tamhankar (stamhankar@hotmail.com) 	*/
	/* conforms closely to RFC 822.                       		*/
	
	/* The following pattern is used to check if the entered e-mail address 	*/
	/* fits the user@domain format.  It also is used to separate the username 	*/
	/* from the domain. 														*/
	var emailPat=/^(.+)@(.+)$/;
	/* The following string represents the pattern for matching all special		*/
	/*  characters.  We don't want to allow special characters in the address. 	*/
	/*  These characters include ( ) < > @ , ; : \ " . [ ]    					*/
	var specialChars="\\(\\)<>@,;:\\\\\\\"\\.\\[\\]";
	/* The following string represents the range of characters allowed in a 	*/
	/* username or domainname.  It really states which chars aren't allowed. 	*/
	var validChars="\[^\\s" + specialChars + "\]";
	/* The following pattern applies if the "user" is a quoted string (in	*/
	/* which case, there are no rules about which characters are allowed	*/
	/* and which aren't; anything goes).  E.g. "jiminy cricket"@disney.com 	*/
	/* is a legal e-mail address. 											*/
	var quotedUser="(\"[^\"]*\")";
	/* The following pattern applies for domains that are IP addresses,  	*/
	/* rather than symbolic names.  E.g. joe@[123.124.233.4] is a legal		*/
	/*  e-mail address. NOTE: The square brackets are required. 			*/
	var ipDomainPat=/^\[(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\]$/;
	/* The following string represents an atom (basically a series of non-special characters.) */
	var atom=validChars + '+';
	/* The following string represents one word in the typical username.*/
	/* For example, in john.doe@somewhere.com, john and doe are words.  */
	/* Basically, a word is either an atom or quoted string. 			*/
	var word="(" + atom + "|" + quotedUser + ")";
	// The following pattern describes the structure of the user
	var userPat=new RegExp("^" + word + "(\\." + word + ")*$");
	/* The following pattern describes the structure of a normal symbolic domain, as opposed to ipDomainPat, shown above. */
	var domainPat=new RegExp("^" + atom + "(\\." + atom +")*$")	;
	/* Finally, let's start trying to figure out if the supplied address is valid. */	
	/* Begin with the coarse pattern to simply break up user@domain into different pieces that are easy to analyze. */
	var matchArray=emailStr.match(emailPat);
	if (matchArray==null) {
	/* Too many/few @'s or something; basically, this address doesn't even fit the general mould of a valid e-mail address. */
		alert("Email address seems incorrect (check @ and .'s)");
		return false;
	}
	var user=matchArray[1];
	var domain=matchArray[2];
	
	// See if "user" is valid 
	if (user.match(userPat)==null) {
	    // user is not valid
	    alert("The username doesn't seem to be valid.");
	    return false;
	}
	
	/* if the e-mail address is at an IP address (as opposed to a symbolic host name) make sure the IP address is valid. */
	var IPArray=domain.match(ipDomainPat);
	if (IPArray!=null) {
	    // this is an IP address
		  for (var i=1;i<=4;i++) {
		    if (IPArray[i]>255) {
		        alert("Destination IP address is invalid!");
			return false;
		    }
	    }
	    return true;
	}	
	// Domain is symbolic name
	var domainArray=domain.match(domainPat);
	if (domainArray==null) {
		alert("The domain name doesn't seem to be valid.");
	    return false;
	}	
	/* domain name seems valid, but now make sure that it ends in a 			*/
	/* three-letter word (like com, edu, gov) or a two-letter word,				*/
	/*  representing country (uk, nl), and that there's a hostname preceding  	*/
	/*   the domain or country. 												*/
	
	/* Now we need to break up the domain to get a count of how many atoms it consists of. */
	var atomPat=new RegExp(atom,"g");
	var domArr=domain.match(atomPat);
	var len=domArr.length;
	if (domArr[domArr.length-1].length<2 || 
	    domArr[domArr.length-1].length>4) {
	   // the address must end in a two, three, or four letter word (four letter to support the .name domain)
	   alert("The address must end in a three or four letter domain, or two letter country.");
	   return false;
	}
	
	// Make sure there's a host name preceding the domain.
	if (len<2) {
	   var errStr="This address is missing a hostname!";
	   alert(errStr);
	   return false;
	}
	
	// If we've gotten this far, everything's valid!
	return true;
}
function forgotPassword(email) {
 var theURL = "/passwordLookup.cfm?emailAddr=" + email;
 popUpWindow(theURL, 300,320);
}
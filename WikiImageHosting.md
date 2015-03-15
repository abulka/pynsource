### Using the File Download area ###
Yes you can put files in the download area? But
```
http://pynsource.googlecode.com/files/pynsource_screenshot0.jpg
```
triggers a download!  So use html markup e.g. the following markup
```
<img src="http://pynsource.googlecode.com/files/pynsource_screenshot0.jpg" alt="Logo"/>
```
which renders properly:

<img src='http://pynsource.googlecode.com/files/pynsource_screenshot0.jpg' alt='Logo' />

however
  * its a questionable use of the download area!
  * no file structure in the download area thus everything is flat, thus would get messy mixing download releases and images for the wiki.
  * though at least it won't get featured on the home page unless I tag it as featured

### Refer to svn files ###

This works and is the simplest.
Take the raw url from the google code source browser and

e.g.
| **replace this portion of the url**||
|:-----------------------------------|:|
|`http://code.google.com/p/pynsource/source/browse/`|trunk/Admin/todo/class%20variables%20should%20point.gif|
| **with**|  |
|`http://pynsource.googlecode.com/svn/`|trunk/Admin/todo/class%20variables%20should%20point.gif|

thus:

![http://pynsource.googlecode.com/svn/trunk/Admin/todo/class%20variables%20should%20point.gif](http://pynsource.googlecode.com/svn/trunk/Admin/todo/class%20variables%20should%20point.gif)

### Referring to files in the wiki portion of svn ###

This is the same as the svn url technique.  Just put the images in the wiki subfolder under images and add **`http://pynsource.googlecode.com/svn/`** to the path

e.g.
```
http://pynsource.googlecode.com/svn/wiki/images/pynsource_screenshot0.jpg
```

![http://pynsource.googlecode.com/svn/wiki/images/pynsource_screenshot0.jpg](http://pynsource.googlecode.com/svn/wiki/images/pynsource_screenshot0.jpg)

p.s.

this gives you raw svn browsing in the browser

http://pynsource.googlecode.com/svn/
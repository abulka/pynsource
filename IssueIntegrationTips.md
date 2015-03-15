# Introduction #

These tips (annotated by me) are from the page

http://code.google.com/p/support/wiki/IssueTracker#Issue_details_and_updates

# Details #

## "short form" syntax ##

The issue tracker handles an easy-to-use "short form" syntax to set an issue's status to Fixed. This would be used when the source code change you are committing completely fixes a defect or implements a requested enhancement. The syntax is any one of the following:

```
(Fixes issue NNN)	 Enclose command in parentheses
Fixes issue NNN.	 Full sentence in your log message description
Fixes issue NNN	         On a line by itself
```

The word Fixes can replaced with Closes or Resolves. The issue number can have a leading pound-sign (#) or not.

**Just mix the above text in with your normal commit comment.**

### multi-line "long form" syntax ###

The other commit-log commands use a multi-line "long form" syntax that is more powerful. You might want to update an issue that is partly resolved or mitigated by your commit. You might want to enter a new issue as part of a commit, if you know that you are introducing a problem that you want to remember to resolve later. You might request a code review as part of a commit when you believe that you have finished work on a branch and you want a teammate to review it before you merge it into the trunk.

These commands begin on some line in your commit-log message and continue until the end of the message. The syntax is:

```
Your commit log message descriptive text...
                      BLANK LINE
COMMAND-LINE          e.g. Update issue NNN
ISSUE-FIELD-UPDATE+   OPTIONAL
COMMENT-TEXT...       THIS TEXT APPEARS ON THE ISSUE PAGE
```

Where COMMAND-LINE is one of the following:

```
Update issue NNN
New issue
New review
```
@echo off

REM based on http://billreminder.gnulinuxbrasil.org/?p=11
REM if you get synch lock error reset the google repository from the google code gui (bottom of source tab)
REM ignore the error svnsync: warning: W200007: Target server does not support atomic revision property edits; consider upgrading it to 1.7 or using an external locking program
REM

set from=https://pyidea.svn.sourceforge.net/svnroot/pyidea/pynsource/trunk
set to=https://pynsource.googlecode.com/svn
set source_username=abulka
set target_username=abulka
set to_auth=--sync-username %target_username% --sync-password a8w2w2x3

REM svnsync init –username [your username] https://[your project].googlecode.com/svn https://[your project].svn.sourceforge.net/svnroot/[your project]
REM svnsync sync –username [your username] https://[your project].googlecode.com/svn

@echo on

REM svn propdel --revprop -r0 svn:sync-lock %to%
REM svnsync init --steal-lock --source-username %source_username% %to_auth% %to% %from%
svnsync sync %to_auth% %to%

@echo off

REM --source-username ARG    : connect to source repository with username ARG
REM --source-password ARG    : connect to source repository with password ARG
REM --sync-username ARG      : connect to sync repository with username ARG
REM --sync-password ARG      : connect to sync repository with password ARG
  


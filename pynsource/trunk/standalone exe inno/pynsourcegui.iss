[Icons]
Name: {group}\PyNSourceGui; Filename: {app}\pyNsourceGui.exe; IconFilename: {app}\pyNsourceGui.exe; IconIndex: 0
Name: {group}\Readme; Filename: {app}\Readme.txt
[Setup]
AppCopyright=© Andy Bulka
AppName=PyNSource Gui
AppVerName=1.4c
DefaultDirName={pf}\PyNSource
ShowLanguageDialog=yes
AppPublisher=Andy Bulka
AppPublisherURL=http://www.atug.com/andypatterns/pynsource.htm
AppVersion=1.4c
UninstallDisplayIcon={app}\pyNsourceGui.exe
UninstallDisplayName=PyNSource Gui
DefaultGroupName=PyNSource
[Files]
Source: ..\pynsource\dist\pyNsourceGui.exe; DestDir: {app}
Source: ..\pynsource\dist\python23.dll; DestDir: {app}
Source: ..\pynsource\dist\w9xpopen.exe; DestDir: {app}
Source: ..\pynsource\dist\wxc.pyd; DestDir: {app}
Source: ..\pynsource\dist\wxmsw24h.dll; DestDir: {app}
Source: ..\pynsource\dist\_sre.pyd; DestDir: {app}
Source: ..\pynsource\dist\datetime.pyd; DestDir: {app}
Source: ..\pynsource\dist\library.zip; DestDir: {app}
Source: ..\pynsource\dist\oglc.pyd; DestDir: {app}
Source: ..\pynsource\Readme.txt; DestDir: {app}

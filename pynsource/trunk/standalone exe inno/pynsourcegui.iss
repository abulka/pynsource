[Icons]
Name: {group}\PyNSourceGui; Filename: {app}\pyNsourceGui.exe; IconFilename: {app}\pyNsourceGui.exe; IconIndex: 0
Name: {group}\Readme; Filename: {app}\Readme.txt
[Setup]
AppCopyright=© Andy Bulka
AppName=PyNSource Gui
AppVerName=1.5
DefaultDirName={pf}\PyNSource
ShowLanguageDialog=yes
AppPublisher=Andy Bulka
AppPublisherURL=http://www.andypatterns.com/index.php/products/pynsource_-_uml_tool_for_python/
AppVersion=1.5
UninstallDisplayIcon={app}\pyNsourceGui.exe
UninstallDisplayName=PyNSource Gui
DefaultGroupName=PyNSource
VersionInfoVersion=1.5

[Files]
Source: ..\pynsource\dist\*; DestDir: {app}; Flags: recursesubdirs
Source: ..\Readme.txt; DestDir: {app}
Source: ..\pynsource\dist\pyNsourceGui.exe; DestDir: {app}; 

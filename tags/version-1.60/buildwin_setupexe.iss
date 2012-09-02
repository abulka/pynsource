[Icons]
Name: {group}\PyNSourceGui; Filename: {app}\pyNsourceGui.exe; IconFilename: {app}\pyNsourceGui.exe; IconIndex: 0
Name: {group}\Readme; Filename: {app}\Readme.txt
[Setup]
AppCopyright=© Andy Bulka
AppName=PyNSource Gui
AppVersion=1.60
DefaultDirName={pf}\PyNSource
ShowLanguageDialog=yes
AppPublisher=Andy Bulka
AppPublisherURL=http://www.andypatterns.com/index.php/products/pynsource/
UninstallDisplayIcon={app}\pyNsourceGui.exe
UninstallDisplayName=PyNSource Gui
DefaultGroupName=PyNSource
VersionInfoVersion=1.60
OutputDir=dist
OutputBaseFilename=pyNsource-1.60-win32-setup

[Files]
Source: src\dist\pyNsourceGui.exe; DestDir: {app}; 
Source: src\dist\*; DestDir: {app}; Flags: recursesubdirs
Source: Readme.txt; DestDir: {app}
Source: version.txt; DestDir: {app}

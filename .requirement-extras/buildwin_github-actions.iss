[Icons]
;Name: {group}\Pynsource; Filename: {app}\Pynsource.exe; IconFilename: {app}\Pynsource.exe; IconIndex: 0
Name: {group}\Pynsource; Filename: {app}\Pynsource.exe; IconFilename: "{app}\pynsource.ico"
; Name: {group}\Readme; Filename: {app}\Readme.txt; AfterInstall: ConvertLineEndings_2019('{app}\Readme.txt')
; Name: {group}\Changelog; Filename: {app}\Changelog.txt; AfterInstall: ConvertLineEndings_2019('{app}\Changelog.txt')
Name: {group}\Readme; Filename: {app}\Readme.txt
Name: {group}\Changelog; Filename: {app}\Changelog.txt

[Setup]
AppCopyright=Andy Bulka
AppName=Pynsource
AppVersion=1.78
DefaultDirName={commonpf}\Pynsource
ShowLanguageDialog=yes
AppPublisher=Andy Bulka - WWare
AppPublisherURL=http://www.pynsource.com
UninstallDisplayIcon={app}\Pynsource.exe
UninstallDisplayName=Pynsource
DefaultGroupName=Pynsource
VersionInfoVersion=1.78
; cwd seems to be the location of THIS file, so relative links get us back to pynsource/
OutputDir=..\dist-inno\
OutputBaseFilename=pynsource-win-1.78-setup
ArchitecturesInstallIn64BitMode=x64

[Files]
; cwd seems to be the location of THIS file, so relative links get us back to pynsource/
Source: ..\dist\Pynsource.exe; DestDir: {app}; 
;Source: ..\dist\*; DestDir: {app}; Flags: recursesubdirs
Source: ..\README.md; DestDir: {app}; DestName: Readme.txt
Source: ..\CHANGELOG.md; DestDir: {app}; DestName: Changelog.txt
Source: ..\src\media\pynsource.ico; DestDir: {app}

; [Code]
; { 
; Converts lf to crlf line endings
; Called during installation,after the readme.txt is copied to the user's machine.
; Had to make some hack changes to handle unicode, cos Inno by default only handles ansi - sad
; See https://stackoverflow.com/questions/20912510/loadstringfromfile-and-stringchangeex-from-unicode-inno-setup-ansi-file 
; }
; const
;    LF = #10;
;    CR = #13;
;    CRLF = CR + LF;
; procedure ConvertLineEndings_2019(CurrentFileName: String);
; var
;   FilePath : String;
;   UnicodeStr: string;
;   ANSIStr: AnsiString;
; begin
;   FilePath := ExpandConstant(CurrentFileName);
;   {MsgBox('ConvertLineEndings_2019 ' + FilePath + '.', mbInformation, MB_OK);}
;   if LoadStringFromFile(FilePath, ANSIStr) then
;   begin
;     UnicodeStr := String(ANSIStr);
;     {MsgBox('about to do the conversion ' + FilePath + '.', mbInformation, MB_OK);}
;     if StringChangeEx(UnicodeStr, LF, CRLF, False) > 0 then
;       begin
;       SaveStringToFile(FilePath, AnsiString(UnicodeStr), False);
;       {MsgBox('converted and saved ' + FilePath + '.', mbInformation, MB_OK);}
;       end
; {
;     else
;       MsgBox('could not convert? ' + FilePath + '.', mbInformation, MB_OK);
; }
;   end;
; end;

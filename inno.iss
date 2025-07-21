[Setup]
AppName=Mini Market POS
AppVersion=1.0
AppPublisher=Jaime M. Estrada Bernabé
AppPublisherURL=https://paginaweb-ro9v.onrender.com/
AppSupportURL=https://paginaweb-ro9v.onrender.com
DefaultDirName={localappdata}\Mini Market POS
DefaultGroupName=Mini Market POS
OutputBaseFilename=MiniMarketPOSSetup
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=no


[Files]
Source: "C:\Users\smart\OneDrive\Escritorio\tiendita-gui\dist\MiniMarketPOS.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Mini Market POS"; Filename: "{app}\MiniMarketPOS.exe"
Name: "{userdesktop}\Mini Market POS"; Filename: "{app}\MiniMarketPOS.exe"

[Run]
Filename: "{app}\MiniMarketPOS.exe"; Description: "Iniciar Mini Market POS"; Flags: nowait postinstall skipifsilent

@echo off
rem Halo CE Universal rally: fills your system link game with bots that run
rem to where you stand. For a PC where HaloLauncher.exe installed the game
rem (built from github.com/cybersecurity/halo-ce-universal or this fork).
rem
rem   rally.cmd [bots]   1 to 127 bots; 127, a game of 128, if left out
rem
rem It downloads its two helpers from this repository next to itself, adds
rem the position dump the bots steer by to the installed game's source
rem (rally_patch.py) and rebuilds the game when that is new, then starts
rem Halo. Create a system link game, press a key here, and the bots join.
rem Run it again while that Halo is running for another round of bots.
setlocal
set "RALLY_REPO=https://raw.githubusercontent.com/bnunu/halo-ce-universal/main/tools/rally"
set "RALLY_BOTS=%~1"
if not defined RALLY_BOTS set "RALLY_BOTS=127"
set "RALLY_HERE=%~dp0"

set "RALLY_ROOT="
for /f "tokens=2,*" %%a in ('reg query "HKCU\Software\HaloCEUniversal" /v InstallRoot 2^>nul ^| findstr /i "InstallRoot"') do set "RALLY_ROOT=%%b"
if not defined RALLY_ROOT set "RALLY_ROOT=%LOCALAPPDATA%\HaloCEUniversal"
set "RALLY_PLAYERS=%RALLY_ROOT%\game\source\game\players.c"
set "RALLY_EXE=%RALLY_ROOT%\game\build\windows\halo.exe"
set "RALLY_PYTHON=%RALLY_ROOT%\tools\python\python.exe"

if not exist "%RALLY_EXE%" (
	echo Halo CE Universal isn't installed in %RALLY_ROOT%.
	echo Install it with HaloLauncher.exe first.
	goto failed
)
findstr /c:"HALO_PORT_MAXIMUM_NETWORK_PLAYERS" "%RALLY_PLAYERS%" >nul 2>&1 || (
	echo This Halo is from before games of more than 16 players.
	echo Open Halo CE Universal, click Update now, then run this again.
	goto failed
)

echo Getting the rally's helpers...
curl.exe -fsSL -o "%RALLY_HERE%rally_patch.py" "%RALLY_REPO%/rally_patch.py" || goto offline
curl.exe -fsSL -o "%RALLY_HERE%system_link_bots_rally.py" "%RALLY_REPO%/system_link_bots_rally.py" || goto offline

rem Halo running already (another round): only the bots
tasklist /fi "imagename eq halo.exe" 2>nul | "%SystemRoot%\System32\find.exe" /i "halo.exe" >nul && goto running

rem the position dump, once (and again after each Halo update, which
rem brings back the original players.c); the game is rebuilt when its
rem source is newer
"%RALLY_PYTHON%" "%RALLY_HERE%rally_patch.py" "%RALLY_PLAYERS%" || goto failed
powershell -NoProfile -Command "exit [int]((Get-Item -LiteralPath $env:RALLY_EXE).LastWriteTime -lt (Get-Item -LiteralPath $env:RALLY_PLAYERS).LastWriteTime)"
if not errorlevel 1 goto play
echo Rebuilding Halo with it (a minute or two)...
start "" /wait "%RALLY_ROOT%\HaloLauncher.exe" --install --no-shortcuts
if errorlevel 1 goto failed

:play
rem HALO_POSITIONS in the launcher's settings too (Settings, other variables),
rem so that Halo tells the bots where players are however it is started
findstr /b /c:"env.HALO_POSITIONS=1" "%RALLY_ROOT%\launcher.ini" >nul 2>&1 || >>"%RALLY_ROOT%\launcher.ini" echo env.HALO_POSITIONS=1
del "%RALLY_ROOT%\data\positions.txt" >nul 2>&1
set "HALO_POSITIONS=1"
start "" "%RALLY_ROOT%\HaloLauncher.exe" --play
echo.
echo Halo is starting.
goto bots

:running
rem the bots need the running game to tell them where players are
set "RALLY_POSITIONS=%RALLY_ROOT%\data\positions.txt"
rem it does (the positions were written in the last few seconds): go ahead
powershell -NoProfile -Command "exit [int](((Get-Date) - (Get-Item -LiteralPath $env:RALLY_POSITIONS).LastWriteTime).TotalSeconds -gt 5)" >nul 2>&1
if not errorlevel 1 goto running_confirmed
rem a Halo update took the position dump out: they would stand still
findstr /c:"demo_dump_player_positions" "%RALLY_PLAYERS%" >nul 2>&1 || goto restart
powershell -NoProfile -Command "exit [int]((Get-Item -LiteralPath $env:RALLY_EXE).LastWriteTime -lt (Get-Item -LiteralPath $env:RALLY_PLAYERS).LastWriteTime)"
if errorlevel 1 goto restart
rem built with it; whether this Halo was started with HALO_POSITIONS shows
rem once the game is under way (the launcher's settings get it for next time)
findstr /b /c:"env.HALO_POSITIONS=1" "%RALLY_ROOT%\launcher.ini" >nul 2>&1 || >>"%RALLY_ROOT%\launcher.ini" echo env.HALO_POSITIONS=1
echo.
echo Halo is running: bringing in another round of bots. If they stand still,
echo close Halo and run this command again.
goto bots

:running_confirmed
findstr /b /c:"env.HALO_POSITIONS=1" "%RALLY_ROOT%\launcher.ini" >nul 2>&1 || >>"%RALLY_ROOT%\launcher.ini" echo env.HALO_POSITIONS=1
echo.
echo Halo is running: bringing in another round of bots.

:bots
echo In Halo: Multiplayer, create a system link game, and wait in the lobby.
echo Then come back here and press a key: %RALLY_BOTS% bots join, the game
echo starts, and about 3 seconds in they run to where you are standing.
echo Ctrl+C here takes them out again.
pause >nul
"%RALLY_PYTHON%" "%RALLY_HERE%system_link_bots_rally.py" --machines %RALLY_BOTS% --start --positions "%RALLY_ROOT%\data\positions.txt" --gather machine:0
pause
exit /b 0

:restart
echo.
echo Halo was updated since the rally set it up, so it can't tell the bots
echo where to go and they would stand still. Close Halo, then run this
echo command again: it sets the rally up again.
goto failed

:offline
echo Couldn't download the rally's helpers from %RALLY_REPO%.
echo Check the internet connection, then try again.
:failed
echo.
pause
exit /b 1

param([switch]$BuildBlockout)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$projectFile = Join-Path $projectRoot 'Multimodal.uproject'
$engineRoot = 'D:\Epic Games\UE_5.8'
$editor = Join-Path $engineRoot 'Engine/Binaries/Win64/UnrealEditor.exe'
$versionFile = Join-Path $engineRoot 'Engine/Build/Build.version'
if (!(Test-Path -LiteralPath $editor) -or !(Test-Path -LiteralPath $versionFile)) {
    throw 'UE 5.8 installation must finish before launching.'
}
$version = Get-Content -LiteralPath $versionFile -Raw | ConvertFrom-Json
if ($version.MajorVersion -ne 5 -or $version.MinorVersion -ne 8) {
    throw 'Refusing to launch a different Unreal Engine version.'
}
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'An Unreal Editor is already running. Inspect that session before starting another.'
}
$mapFile = Join-Path $projectRoot 'Content/ClientHome_Haeso/Maps/Lvl_ClientHome_Blockout.umap'
$map = if (Test-Path -LiteralPath $mapFile) { '/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Blockout' } else { '/Engine/Maps/Entry' }
# Command-line overrides leave all shared project settings unchanged.
$editorArgs = @(('"' + $projectFile + '"'), $map, '-ModelContextProtocolStartServer', '-EnablePlugins=PythonScriptPlugin', '-NoSplash')
if ($BuildBlockout) {
    if (Test-Path -LiteralPath $mapFile) {
        throw 'The blockout already exists; launch without -BuildBlockout.'
    }
    $buildScript = (Join-Path $PSScriptRoot 'build_blockout.py').Replace('\', '/')
    $editorArgs += ('-ExecutePythonScript="' + $buildScript + '"')
}
$editorProcess = Start-Process -FilePath $editor -ArgumentList $editorArgs -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
Write-Output ('Started UE 5.8 editor, PID ' + $editorProcess.Id + ', map ' + $map)

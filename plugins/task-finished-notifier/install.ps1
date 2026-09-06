$ErrorActionPreference = 'Stop'
$sourcePlugin = $PSScriptRoot
$validationDeps = [IO.Path]::GetFullPath((Join-Path $sourcePlugin '../../.plugin-validation-deps'))
if (Test-Path -LiteralPath $validationDeps) {
    $env:PYTHONPATH = $validationDeps + [IO.Path]::PathSeparator + $env:PYTHONPATH
}
$personalRoot = Join-Path $env:USERPROFILE '.agents/plugins'
$pluginParent = Join-Path $env:USERPROFILE 'plugins'
$installedSource = Join-Path $pluginParent 'task-finished-notifier'
$creatorRoot = Join-Path $env:USERPROFILE '.codex/skills/.system/plugin-creator'
$marketplace = Join-Path $personalRoot 'marketplace.json'
if (Test-Path -LiteralPath $installedSource) {
    throw "Plugin source already exists; refusing to overwrite: $installedSource"
}
if (Test-Path -LiteralPath $marketplace) {
    $marketName = & python (Join-Path $creatorRoot 'scripts/read_marketplace_name.py')
    if ($LASTEXITCODE -ne 0) { throw 'Invalid personal marketplace' }
    $marketName = $marketName.Trim()
} else {
    $marketName = 'personal'
}
& python (Join-Path $creatorRoot 'scripts/create_basic_plugin.py') task-finished-notifier --path $pluginParent --with-marketplace --force
if ($LASTEXITCODE -ne 0) { throw 'Scaffolding failed' }
foreach ($part in @('.codex-plugin', 'hooks', 'scripts', 'README.md')) {
    Copy-Item -LiteralPath (Join-Path $sourcePlugin $part) -Destination $installedSource -Recurse -Force
}
& python (Join-Path $creatorRoot 'scripts/validate_plugin.py') $installedSource
if ($LASTEXITCODE -ne 0) { throw 'Plugin validation failed' }
& codex plugin add "task-finished-notifier@$marketName" --json
if ($LASTEXITCODE -ne 0) { throw 'Plugin installation failed' }
Write-Output 'Installed. Review and trust the Stop hook in Codex /hooks, then start a new conversation.'

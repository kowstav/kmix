$ErrorActionPreference='Stop'
$nodePath='C:\Users\91707\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$manifest=Get-Content -LiteralPath research_round9_preservation_links_manifest.json -Raw | ConvertFrom-Json
$env:HP_NETWORK_TIMEOUT_MS='180000'
$verified=@()
foreach($row in $manifest.files) {
  $dir=Join-Path (Get-Location).Path ('research_round9_native_evidence\'+$row.job)
  if (!(Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  $destination=Join-Path $dir $row.filename
  if ((Test-Path -LiteralPath $destination) -and ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() -eq $row.sha256)) {
    $verified+=$row; continue
  }
  & $nodePath kaggle_research_client.mjs download $row.remote_path $destination
  if ($LASTEXITCODE -ne 0) { throw ('Failed checkpoint download: '+$row.filename) }
  if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw ('SHA mismatch: '+$row.filename) }
  $verified+=$row
}
$result=@{all_sha256_verified=$true; verified_files=$verified.Count; bytes=($verified | Measure-Object -Property bytes -Sum).Sum; manifest='research_round9_preservation_links_manifest.json'; snapshot_time_utc=[DateTime]::UtcNow.ToString('o')}
$result | ConvertTo-Json | Set-Content -LiteralPath research_round9_downloaded_models_verified.json -Encoding utf8
$result | ConvertTo-Json

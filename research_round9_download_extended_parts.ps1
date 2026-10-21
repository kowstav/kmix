$ErrorActionPreference='Stop'
$nodePath='C:\Users\91707\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$manifest=Get-Content -LiteralPath research_round9_compact_download_parts_v2_results.json -Raw | ConvertFrom-Json
if ($manifest.status -ne 'COMPLETE_VERIFIED_EXTENDED_ZIP_DOWNLOAD_PARTS') { throw 'Remote parts are not complete.' }
$dir=Join-Path (Get-Location).Path 'research_round9_extended_parts_v2'
New-Item -ItemType Directory -Path $dir -Force | Out-Null
$env:HP_NETWORK_TIMEOUT_MS='180000'
foreach($row in $manifest.parts) {
  $dest=Join-Path $dir $row.filename
  if ((Test-Path -LiteralPath $dest) -and ((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLower() -eq $row.sha256)) { continue }
  & $nodePath kaggle_research_client.mjs download $row.remote_path $dest
  if ($LASTEXITCODE -ne 0) { throw ('Part download failed: '+$row.filename) }
  if ((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw ('Part SHA mismatch: '+$row.filename) }
}
$archive=Join-Path (Get-Location).Path 'research_round9_extended_evidence_v2.zip'
if (!(Test-Path -LiteralPath $archive) -or ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLower() -ne $manifest.source_sha256)) {
  $out=[IO.File]::Open($archive,[IO.FileMode]::Create,[IO.FileAccess]::Write)
  try {
    foreach($row in $manifest.parts) {
      $input=[IO.File]::OpenRead((Join-Path $dir $row.filename))
      try { $input.CopyTo($out,1048576) } finally { $input.Dispose() }
    }
  } finally { $out.Dispose() }
}
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLower() -ne $manifest.source_sha256) { throw 'Combined ZIP SHA mismatch.' }
@{status='LOCAL_PARTS_AND_CONCATENATED_SHA_VERIFIED';bytes=$manifest.source_bytes;sha256=$manifest.source_sha256;parts=$manifest.parts.Count;timestamp=[DateTime]::UtcNow.ToString('o');deletions=@()} | ConvertTo-Json | Set-Content -LiteralPath research_round9_extended_download_verified.json -Encoding utf8
Get-Content -LiteralPath research_round9_extended_download_verified.json

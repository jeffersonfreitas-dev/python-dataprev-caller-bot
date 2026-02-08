$repoPath = "C:\Users\jeffe\PycharmProjects\DataprevCallerBot"
$filePath = "$repoPath\test.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $filePath -Value "Atualizado em $timestamp"
Set-Location $repoPath
git add .
git commit -m "Atualizacao automatica em $timestamp"
git push
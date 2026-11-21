$source = "D:\AI-Multimodal-Triage_System\Multimodal_TRIAGEAI_Capstone_Final_PPT_v2.pptx"
$destination1 = "D:\AI-Multimodal-Triage_System\Multimodal_TRIAGEAI_Capstone_Final_PPT.pptx"
$destination2 = "D:\AI-Multimodal-Triage_System\Multimodal_TRIAGEAI_Capstone_Final_PPT_Streamlined.pptx"

Write-Host "Syncing $source into PowerPoint destinations once unlocked..."
try {
    Copy-Item -Path $source -Destination $destination1 -Force -ErrorAction SilentlyContinue
    Write-Host "Updated $destination1"
} catch {}

try {
    Copy-Item -Path $source -Destination $destination2 -Force -ErrorAction SilentlyContinue
    Write-Host "Updated $destination2"
} catch {}

if (-not $copied) {
    Write-Host "Could not overwrite yet because the file is still locked. Please close PowerPoint and run this script again."
}

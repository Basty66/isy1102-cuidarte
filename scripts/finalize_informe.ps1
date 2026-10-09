<#
    finalize_informe.ps1
    Abre el informe en Microsoft Word, actualiza el indice (TOC) con numeros de
    pagina reales, guarda el .docx y exporta una copia en PDF.

    Uso:  powershell -ExecutionPolicy Bypass -File scripts\finalize_informe.ps1
    Requiere Microsoft Word instalado. Si no lo esta, el .docx sigue siendo
    valido: Word actualiza el indice solo al abrirlo (updateFields = true).
#>

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$docx = Join-Path $root 'Informe_Seguridad_Calidad_Cuidarte_ISY1102.docx'
$pdf  = Join-Path $root 'Informe_Seguridad_Calidad_Cuidarte_ISY1102.pdf'

if (-not (Test-Path $docx)) {
    throw "No existe $docx. Ejecuta antes: python scripts\generate_informe_docx.py"
}

$word = $null
$doc  = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $doc = $word.Documents.Open($docx, $false, $false)

    # Indice con numeracion de pagina real.
    # Nota: NO usar $doc.Fields.Update() ni $doc.Repaginate() aqui: sobre este
    # documento (24 tablas) se cuelgan indefinidamente. Actualizar solo el TOC
    # es suficiente y toma ~1 s.
    for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) {
        $doc.TablesOfContents.Item($i).Update()
    }

    $doc.Save()
    $doc.ExportAsFixedFormat($pdf, 17)   # 17 = wdExportFormatPDF

    Write-Output "OK  docx actualizado : $docx"
    Write-Output "OK  pdf exportado    : $pdf"
}
finally {
    if ($doc)  { $doc.Close([ref]0) | Out-Null }
    if ($word) { $word.Quit() | Out-Null }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect()
}

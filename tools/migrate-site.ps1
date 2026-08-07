Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

$repoRoot = Split-Path -Parent $PSScriptRoot
$siteRoot = Join-Path $repoRoot "site"
$pagesRoot = Join-Path $siteRoot "pages"
$mediaRoot = Join-Path $siteRoot "assets/media"
$docsRoot = Join-Path $repoRoot "docs"
$reportsRoot = Join-Path $repoRoot "reports"

foreach ($dir in @($siteRoot, $pagesRoot, $mediaRoot, $docsRoot, $reportsRoot)) {
  if (-not (Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir | Out-Null
  }
}

function Escape-Html {
  param([string]$Text)
  if ($null -eq $Text) { return "" }
  return [System.Net.WebUtility]::HtmlEncode($Text)
}

function Slugify {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) { return "untitled" }
  $slug = $Text.ToLowerInvariant()
  $slug = [regex]::Replace($slug, "[^a-z0-9]+", "-")
  $slug = [regex]::Replace($slug, "-+", "-")
  $slug = $slug.Trim("-")
  if ([string]::IsNullOrWhiteSpace($slug)) { return "untitled" }
  return $slug
}

function Read-ZipEntryText {
  param(
    [System.IO.Compression.ZipArchive]$Zip,
    [string]$EntryPath
  )
  $entry = $Zip.Entries | Where-Object { $_.FullName -eq $EntryPath } | Select-Object -First 1
  if (-not $entry) { return $null }
  $reader = New-Object System.IO.StreamReader($entry.Open())
  try {
    return $reader.ReadToEnd()
  } finally {
    $reader.Close()
  }
}

function Get-OfficeDocumentPath {
  param([System.IO.Compression.ZipArchive]$Zip)
  $relsText = Read-ZipEntryText -Zip $Zip -EntryPath "_rels/.rels"
  if (-not $relsText) {
    return "word/document.xml"
  }

  [xml]$relsXml = $relsText
  $relationship = $relsXml.Relationships.Relationship |
    Where-Object { $_.Type -like "*officeDocument" } |
    Select-Object -First 1

  if (-not $relationship) {
    return "word/document.xml"
  }

  $target = [string]$relationship.Target
  $target = $target.TrimStart("/")
  return $target
}

function Get-RelationshipMap {
  param(
    [System.IO.Compression.ZipArchive]$Zip,
    [string]$DocumentPath
  )

  $docDir = Split-Path $DocumentPath -Parent
  $docName = Split-Path $DocumentPath -Leaf
  $relsPath = if ([string]::IsNullOrWhiteSpace($docDir)) {
    "_rels/$docName.rels"
  } else {
    "$docDir/_rels/$docName.rels"
  }

  $relsText = Read-ZipEntryText -Zip $Zip -EntryPath $relsPath
  $map = @{}
  if (-not $relsText) {
    return $map
  }

  [xml]$relsXml = $relsText
  foreach ($rel in $relsXml.Relationships.Relationship) {
    $id = [string]$rel.Id
    $target = [string]$rel.Target
    $mode = [string]$rel.GetAttribute("TargetMode")
    if ($mode -eq "External") {
      $map[$id] = $target
      continue
    }

    $combined = if ([string]::IsNullOrWhiteSpace($docDir)) {
      $target
    } else {
      "$docDir/$target"
    }

    $parts = $combined -split "/"
    $stack = New-Object System.Collections.Generic.List[string]
    foreach ($part in $parts) {
      if ([string]::IsNullOrWhiteSpace($part) -or $part -eq ".") { continue }
      if ($part -eq "..") {
        if ($stack.Count -gt 0) { $stack.RemoveAt($stack.Count - 1) }
      } else {
        $stack.Add($part)
      }
    }

    $map[$id] = ($stack -join "/")
  }

  return $map
}

function Get-NumberingFormatMap {
  param(
    [System.IO.Compression.ZipArchive]$Zip,
    [string]$DocumentPath
  )

  $docDir = Split-Path $DocumentPath -Parent
  $numberingPath = if ([string]::IsNullOrWhiteSpace($docDir)) {
    "numbering.xml"
  } else {
    "$docDir/numbering.xml"
  }

  $numberingText = Read-ZipEntryText -Zip $Zip -EntryPath $numberingPath
  $result = @{}
  if (-not $numberingText) {
    return $result
  }

  [xml]$numberingXml = $numberingText
  $ns = New-Object System.Xml.XmlNamespaceManager($numberingXml.NameTable)
  $wNs = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  $ns.AddNamespace("w", $wNs)

  $abstractMap = @{}
  $abstractNodes = $numberingXml.SelectNodes("//w:abstractNum", $ns)
  foreach ($abstract in $abstractNodes) {
    $abstractId = $abstract.GetAttribute("abstractNumId", $wNs)
    if ([string]::IsNullOrWhiteSpace($abstractId)) { continue }

    $levelMap = @{}
    $levelNodes = $abstract.SelectNodes("./w:lvl", $ns)
    foreach ($lvl in $levelNodes) {
      $ilvl = $lvl.GetAttribute("ilvl", $wNs)
      if ([string]::IsNullOrWhiteSpace($ilvl)) { continue }
      $numFmtNode = $lvl.SelectSingleNode("./w:numFmt", $ns)
      $fmt = "decimal"
      if ($numFmtNode) {
        $val = $numFmtNode.GetAttribute("val", $wNs)
        if (-not [string]::IsNullOrWhiteSpace($val)) {
          $fmt = $val
        }
      }
      $levelMap[$ilvl] = $fmt
    }

    $abstractMap[$abstractId] = $levelMap
  }

  $numNodes = $numberingXml.SelectNodes("//w:num", $ns)
  foreach ($numNode in $numNodes) {
    $numId = $numNode.GetAttribute("numId", $wNs)
    if ([string]::IsNullOrWhiteSpace($numId)) { continue }

    $abstractIdNode = $numNode.SelectSingleNode("./w:abstractNumId", $ns)
    if (-not $abstractIdNode) { continue }
    $abstractId = $abstractIdNode.GetAttribute("val", $wNs)

    $effectiveLevelMap = @{}
    if (-not [string]::IsNullOrWhiteSpace($abstractId) -and $abstractMap.ContainsKey($abstractId)) {
      foreach ($pair in $abstractMap[$abstractId].GetEnumerator()) {
        $effectiveLevelMap[$pair.Key] = $pair.Value
      }
    }

    $overrideNodes = $numNode.SelectNodes("./w:lvlOverride", $ns)
    foreach ($override in $overrideNodes) {
      $ilvl = $override.GetAttribute("ilvl", $wNs)
      if ([string]::IsNullOrWhiteSpace($ilvl)) { continue }
      $overrideFmtNode = $override.SelectSingleNode("./w:lvl/w:numFmt", $ns)
      if ($overrideFmtNode) {
        $overrideFmt = $overrideFmtNode.GetAttribute("val", $wNs)
        if (-not [string]::IsNullOrWhiteSpace($overrideFmt)) {
          $effectiveLevelMap[$ilvl] = $overrideFmt
        }
      }
    }

    foreach ($pair in $effectiveLevelMap.GetEnumerator()) {
      $result["$numId|$($pair.Key)"] = $pair.Value
    }
  }

  return $result
}

function Get-ListTypeFromWordNumFormat {
  param([string]$Format)
  if ([string]::IsNullOrWhiteSpace($Format)) { return "ol" }

  $f = $Format.ToLowerInvariant()
  if ($f -in @("bullet", "none", "picture")) {
    return "ul"
  }

  return "ol"
}

function Get-ParagraphText {
  param(
    [System.Xml.XmlNode]$Paragraph,
    [System.Xml.XmlNamespaceManager]$Ns
  )

  $tokens = $Paragraph.SelectNodes(".//w:t|.//w:br|.//w:cr|.//w:tab", $Ns)
  if (-not $tokens -or $tokens.Count -eq 0) {
    return ""
  }

  $sb = New-Object System.Text.StringBuilder
  foreach ($token in $tokens) {
    switch ($token.LocalName) {
      "t" {
        [void]$sb.Append([string]$token.InnerText)
      }
      "tab" {
        [void]$sb.Append(" ")
      }
      default {
        [void]$sb.Append("`n")
      }
    }
  }

  $text = $sb.ToString()
  $text = [regex]::Replace($text, "[ \t]+`n", "`n")
  $text = [regex]::Replace($text, "`n[ \t]+", "`n")
  $text = [regex]::Replace($text, "[ \t]{2,}", " ")
  $text = [regex]::Replace($text, "`n{3,}", "`n`n")
  return $text.Trim()
}

function Split-InlineNumberedSegments {
  param([string]$Text)

  if ([string]::IsNullOrWhiteSpace($Text)) {
    return @()
  }

  $pattern = "(?<!\S)\d+[\.)]\s+"
  $matches = [regex]::Matches($Text, $pattern)
  if ($matches.Count -lt 2) {
    return @($Text)
  }

  $segments = New-Object System.Collections.Generic.List[string]

  $prefix = $Text.Substring(0, $matches[0].Index).Trim()
  if (-not [string]::IsNullOrWhiteSpace($prefix)) {
    $segments.Add($prefix)
  }

  for ($i = 0; $i -lt $matches.Count; $i++) {
    $start = $matches[$i].Index
    $end = if ($i -lt ($matches.Count - 1)) { $matches[$i + 1].Index } else { $Text.Length }
    $part = $Text.Substring($start, $end - $start).Trim()
    if (-not [string]::IsNullOrWhiteSpace($part)) {
      $segments.Add($part)
    }
  }

  return @($segments)
}

function Get-ParagraphLinks {
  param(
    [System.Xml.XmlNode]$Paragraph,
    [System.Xml.XmlNamespaceManager]$Ns,
    [hashtable]$RelMap
  )

  $urls = New-Object System.Collections.Generic.List[string]
  $hyperlinks = $Paragraph.SelectNodes(".//w:hyperlink", $Ns)
  foreach ($hl in $hyperlinks) {
    $rid = $hl.GetAttribute("id", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
    if ($rid -and $RelMap.ContainsKey($rid)) {
      $url = [string]$RelMap[$rid]
      if ($url -and $url -match "^https?://") {
        $urls.Add($url)
      }
    }
  }

  return $urls
}

function Get-UrlsFromText {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) { return @() }
  $urlPattern = "https?://.*?(?=https?://|\s|[\)\]<>`"]|$)"
  $urlMatches = [regex]::Matches($Text, $urlPattern, "IgnoreCase")
  $urls = @()
  foreach ($m in $urlMatches) {
    $url = $m.Value.TrimEnd(".", ",", ";")
    $urls += $url
  }
  return $urls
}

function Normalize-Url {
  param([string]$Url)
  if ([string]::IsNullOrWhiteSpace($Url)) { return $null }

  $normalized = $Url.Trim().TrimEnd(".", ",", ";")
  $protoMatches = [regex]::Matches($normalized, "https?://", "IgnoreCase")
  if ($protoMatches.Count -gt 1) {
    $secondIndex = $protoMatches[1].Index
    $firstPart = $normalized.Substring(0, $secondIndex)
    $secondPart = $normalized.Substring($secondIndex)

    if ($firstPart -eq $secondPart) {
      $normalized = $firstPart
    } elseif ($firstPart -match "^https?://[^\s]+$") {
      $normalized = $firstPart
    }
  }

  if ($normalized -match "^(https?://.+?)https$") {
    $normalized = $Matches[1]
  }

  return $normalized
}

function Get-GyazoPreviewUrl {
  param([string]$Url)
  if ([string]::IsNullOrWhiteSpace($Url)) { return $null }

  if ($Url -match "gyazo\.com/([A-Za-z0-9]+)") {
    return "https://i.gyazo.com/$($Matches[1]).png"
  }

  if ($Url -match "i\.gyazo\.com/([A-Za-z0-9]+)\.(png|jpg|jpeg|gif|webp)") {
    return "https://i.gyazo.com/$($Matches[1]).$($Matches[2])"
  }

  return $null
}

function Linkify-Text {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) { return "" }

  $pattern = "https?://.*?(?=https?://|\s|[\)\]<>`"]|$)"
  $output = [regex]::Replace($Text, $pattern, {
      param($m)
      $url = $m.Value.TrimEnd(".", ",", ";")
      $safe = Escape-Html $url
      return ('<a href="{0}" target="_blank" rel="noopener noreferrer">{0}</a>' -f $safe)
    })

  return $output
}

function Get-YouTubeEmbedUrl {
  param([string]$Url)
  if ($Url -match "youtu\.be/([A-Za-z0-9_-]{11})") {
    return "https://www.youtube.com/embed/$($Matches[1])"
  }

  if ($Url -match "youtube\.com/watch\?v=([A-Za-z0-9_-]{11})") {
    return "https://www.youtube.com/embed/$($Matches[1])"
  }

  if ($Url -match "youtube\.com/embed/([A-Za-z0-9_-]{11})") {
    return "https://www.youtube.com/embed/$($Matches[1])"
  }

  return $null
}

function Get-PanoptoEmbedUrl {
  param([string]$Url)
  if ($Url -notmatch "panopto") { return $null }
  try {
    $uri = [System.Uri]$Url
    $builder = New-Object System.UriBuilder($uri)
    if ($builder.Path -match "/Pages/Viewer\.aspx") {
      $builder.Path = $builder.Path -replace "/Pages/Viewer\.aspx", "/Panopto/Pages/Embed.aspx"
    } elseif ($builder.Path -notmatch "/Embed\.aspx") {
      $builder.Path = "/Panopto/Pages/Embed.aspx"
    }

    if ($builder.Query -match "id=") {
      return $builder.Uri.AbsoluteUri
    }

    return $Url
  } catch {
    return $Url
  }
}

function Is-EmbeddableVideoUrl {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) { return $false }

  $candidate = $Text.Trim()
  if ($candidate -notmatch "^https?://") { return $false }
  if (Get-YouTubeEmbedUrl -Url $candidate) { return $true }
  if ($candidate -match "panopto") { return $true }
  return $false
}

function Copy-DocxMedia {
  param(
    [System.IO.Compression.ZipArchive]$Zip,
    [string]$DocumentPath,
    [string]$Slug
  )

  $docDir = Split-Path $DocumentPath -Parent
  if ([string]::IsNullOrWhiteSpace($docDir)) {
    $mediaPrefix = "media/"
  } else {
    $mediaPrefix = "$docDir/media/"
  }

  $targetDir = Join-Path $mediaRoot $Slug
  if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir | Out-Null
  }

  $output = New-Object System.Collections.Generic.List[string]

  foreach ($entry in $Zip.Entries) {
    if (-not $entry.FullName.StartsWith($mediaPrefix)) { continue }
    $fileName = [System.IO.Path]::GetFileName($entry.FullName)
    if ([string]::IsNullOrWhiteSpace($fileName)) { continue }

    $destPath = Join-Path $targetDir $fileName
    $inStream = $entry.Open()
    $outStream = [System.IO.File]::Create($destPath)
    try {
      $inStream.CopyTo($outStream)
    } finally {
      $inStream.Close()
      $outStream.Close()
    }

    $output.Add("../assets/media/$Slug/$fileName")
  }

  return $output
}

function Is-HeadingLike {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) { return $false }
  if ($Text -match "https?://") { return $false }
  if ($Text.Length -gt 78) { return $false }
  if ($Text -match "[\.\!\?]$") { return $false }
  $words = @($Text -split "\s+" | Where-Object { $_ }).Count
  if ($words -gt 11) { return $false }
  return $true
}

function Convert-ParagraphsToHtml {
  param(
    [System.Collections.Generic.List[object]]$Paragraphs,
    [string]$PageTitle
  )

  $html = New-Object System.Collections.Generic.List[string]
  $html.Add('<section class="section-card">')
  $html.Add('<h2>Content</h2>')

  $listTypes = New-Object System.Collections.Generic.List[string]
  $listItemOpen = New-Object System.Collections.Generic.List[bool]

  $closeAllLists = {
    while ($listTypes.Count -gt 0) {
      $idx = $listTypes.Count - 1
      if ($listItemOpen[$idx]) {
        $html.Add("</li>")
      }
      $html.Add("</$($listTypes[$idx])>")
      $listTypes.RemoveAt($idx)
      $listItemOpen.RemoveAt($idx)
    }
  }

  $buildGyazoPreviewBlock = {
    param([string]$SourceText)
    if ([string]::IsNullOrWhiteSpace($SourceText)) { return "" }

    $snippets = New-Object System.Collections.Generic.List[string]
    $seen = @{}
    $urls = @(Get-UrlsFromText -Text $SourceText)

    foreach ($u in $urls) {
      $clean = Normalize-Url $u
      if ([string]::IsNullOrWhiteSpace($clean)) { continue }
      if ($seen.ContainsKey($clean)) { continue }

      $preview = Get-GyazoPreviewUrl -Url $clean
      if ([string]::IsNullOrWhiteSpace($preview)) { continue }

      $seen[$clean] = $true
      $safeLink = Escape-Html $clean
      $safePreview = Escape-Html $preview
      $snippets.Add('<figure class="image-figure gyazo-inline">')
      $snippets.Add(('<a href="{0}" target="_blank" rel="noopener noreferrer"><img src="{1}" alt="Gyazo preview" loading="lazy" /></a>' -f $safeLink, $safePreview))
      $snippets.Add('<figcaption class="image-caption">Gyazo preview (click image to open link).</figcaption>')
      $snippets.Add('</figure>')
    }

    return ($snippets -join "`n")
  }

  $appendListItem = {
    param(
      [string]$ItemHtml,
      [int]$Level,
      [string]$Type,
      [int]$IndentLevel
    )

    if ([string]::IsNullOrWhiteSpace($Type)) {
      $Type = "ul"
    }

    if ($Level -lt 0) {
      $Level = 0
    }

    $currentDepth = $listTypes.Count - 1

    if ($currentDepth -lt 0 -and $Level -gt 0) {
      $Level = 0
    }

    if ($currentDepth -ge 0 -and $Level -gt ($currentDepth + 1)) {
      $Level = $currentDepth + 1
    }

    if ($currentDepth -lt 0) {
      $html.Add("<$Type>")
      $listTypes.Add($Type)
      $listItemOpen.Add($false)
      $currentDepth = $listTypes.Count - 1
    }

    if ($Level -le $currentDepth) {
      while ($listTypes.Count -gt ($Level + 1)) {
        $idx = $listTypes.Count - 1
        if ($listItemOpen[$idx]) {
          $html.Add("</li>")
        }
        $html.Add("</$($listTypes[$idx])>")
        $listTypes.RemoveAt($idx)
        $listItemOpen.RemoveAt($idx)
      }

      if ($listItemOpen[$Level]) {
        $html.Add("</li>")
        $listItemOpen[$Level] = $false
      }
    } elseif ($Level -gt $currentDepth) {
      for ($l = $currentDepth + 1; $l -le $Level; $l++) {
        $listTypeAtLevel = if ($l -eq $Level) { $Type } else { "ul" }
        $html.Add("<$listTypeAtLevel>")
        $listTypes.Add($listTypeAtLevel)
        $listItemOpen.Add($false)
      }
    }

    if ($listTypes[$Level] -ne $Type) {
      if ($listItemOpen[$Level]) {
        $html.Add("</li>")
        $listItemOpen[$Level] = $false
      }
      $html.Add("</$($listTypes[$Level])>")
      $html.Add("<$Type>")
      $listTypes[$Level] = $Type
    }

    $indentClass = if ($IndentLevel -gt 0) { (' class="indent-level-{0}"' -f $IndentLevel) } else { "" }
    $html.Add("<li$indentClass>$ItemHtml")
    $listItemOpen[$Level] = $true
  }

  $started = $false
  foreach ($p in $Paragraphs) {
    $text = [string]$p.Text
    if ([string]::IsNullOrWhiteSpace($text)) { continue }

    if (-not $started -and $text -eq $PageTitle) {
      $started = $true
      continue
    }
    $started = $true

    $style = [string]$p.Style
    $isList = [bool]$p.IsList
    $listLevel = [int]$p.ListLevel
    $listTypeFromWord = [string]$p.ListType
    $indentLevel = [int]$p.IndentLevel

    if ($text -match "^(Note|Important|Tip|Warning)\s*[:\-]\s*(.+)$") {
      & $closeAllLists
      $prefix = $Matches[1].ToLowerInvariant()
      $body = Linkify-Text (Escape-Html $Matches[2])
      $noteClass = switch ($prefix) {
        "important" { "note note--important" }
        "warning" { "note note--important" }
        "tip" { "note note--tip" }
        default { "note" }
      }
      $label = Escape-Html $Matches[1]
      $html.Add(('<aside class="{0}"><p><strong>{1}:</strong> {2}</p></aside>' -f $noteClass, $label, $body))
      continue
    }

    $orderedByText = $text -match "^\d+[\.)]\s+"
    $unorderedByText = $text -match "^[-*]\s*|^[\u2022\u25CF\u25E6]\s*"

    if ($isList -or $orderedByText -or $unorderedByText) {
      $resolvedType = if (-not [string]::IsNullOrWhiteSpace($listTypeFromWord)) {
        $listTypeFromWord
      } elseif ($unorderedByText) {
        "ul"
      } else {
        "ol"
      }

      $itemText = $text
      if (-not $isList) {
        $itemText = $itemText -replace "^\d+[\.)]\s+", "" -replace "^[-*\u2022\u25CF\u25E6]\s*", ""
      }

      $gyazoPreviews = & $buildGyazoPreviewBlock -SourceText $itemText
      $safeItem = Linkify-Text (Escape-Html $itemText.Trim())
      if (-not [string]::IsNullOrWhiteSpace($gyazoPreviews)) {
        $safeItem = "$gyazoPreviews`n$safeItem"
      }
      if (-not [string]::IsNullOrWhiteSpace($safeItem)) {
        & $appendListItem -ItemHtml $safeItem -Level $listLevel -Type $resolvedType -IndentLevel $indentLevel
      }
      continue
    }

    $headingLevel = $null
    if ($style -match "Heading\s*1|Heading1") { $headingLevel = 2 }
    elseif ($style -match "Heading\s*2|Heading2") { $headingLevel = 3 }
    elseif ($style -match "Heading\s*3|Heading3") { $headingLevel = 3 }
    elseif (Is-HeadingLike $text) { $headingLevel = 3 }

    if ($headingLevel) {
      & $closeAllLists
      $safeHeading = Linkify-Text (Escape-Html $text)
      $html.Add("<h$headingLevel>$safeHeading</h$headingLevel>")
      continue
    }

    $deepestListIndex = $listTypes.Count - 1
    if ($deepestListIndex -ge 0 -and $listItemOpen[$deepestListIndex] -and $text -match "^https?://\S+$") {
      $gyazoPreviews = & $buildGyazoPreviewBlock -SourceText $text
      if (-not [string]::IsNullOrWhiteSpace($gyazoPreviews)) {
        $html.Add($gyazoPreviews)
      }

      $safeNestedParagraph = Linkify-Text (Escape-Html $text)
      $nestedIndentClass = if ($indentLevel -gt 0) { (' class="indent-level-{0}"' -f $indentLevel) } else { "" }
      $html.Add("<p$nestedIndentClass>$safeNestedParagraph</p>")
      continue
    }

    & $closeAllLists
    $gyazoPreviews = & $buildGyazoPreviewBlock -SourceText $text
    if (-not [string]::IsNullOrWhiteSpace($gyazoPreviews)) {
      $html.Add($gyazoPreviews)
    }

    $safeParagraph = Linkify-Text (Escape-Html $text)
    $indentClass = if ($indentLevel -gt 0) { (' class="indent-level-{0}"' -f $indentLevel) } else { "" }
    $html.Add("<p$indentClass>$safeParagraph</p>")
  }

  & $closeAllLists
  $html.Add('</section>')

  return ($html -join "`n")
}

function Convert-TablesToHtml {
  param([System.Collections.Generic.List[object]]$Tables)
  if ($Tables.Count -eq 0) { return "" }

  $html = New-Object System.Collections.Generic.List[string]
  $html.Add('<section class="section-card">')
  $html.Add('<h2>Normalized Tables</h2>')

  $index = 1
  foreach ($table in $Tables) {
    $rows = [System.Collections.Generic.List[object]]$table
    if ($rows.Count -eq 0) { continue }

    $html.Add("<h3>Table $index</h3>")
    $html.Add('<table class="table-normalized">')

    $headerDone = $false
    foreach ($row in $rows) {
      $cells = [System.Collections.Generic.List[string]]$row
      if (-not $headerDone) {
        $html.Add("<thead><tr>")
        foreach ($cell in $cells) {
          $safe = Linkify-Text (Escape-Html $cell)
          $html.Add(('<th scope="col">{0}</th>' -f $safe))
        }
        $html.Add("</tr></thead>")
        $html.Add("<tbody>")
        $headerDone = $true
      } else {
        $html.Add("<tr>")
        foreach ($cell in $cells) {
          $safe = Linkify-Text (Escape-Html $cell)
          $html.Add("<td>$safe</td>")
        }
        $html.Add("</tr>")
      }
    }

    if ($headerDone) {
      $html.Add("</tbody>")
    }

    $html.Add("</table>")
    $index++
  }

  $html.Add('</section>')
  return ($html -join "`n")
}

function Convert-MediaToHtml {
  param(
    [System.Collections.Generic.List[string]]$Urls,
    [System.Collections.Generic.List[string]]$ImagePaths,
    [string]$PageTitle
  )

  $videoEmbeds = New-Object System.Collections.Generic.List[object]
  $gyazoLinks = New-Object System.Collections.Generic.List[string]
  $otherLinks = New-Object System.Collections.Generic.List[string]

  foreach ($url in $Urls) {
    if ([string]::IsNullOrWhiteSpace($url)) { continue }

    $yt = Get-YouTubeEmbedUrl -Url $url
    if ($yt) {
      $videoEmbeds.Add([pscustomobject]@{ Kind = "youtube"; Source = $url; Embed = $yt })
      continue
    }

    if ($url -match "panopto") {
      $videoEmbeds.Add([pscustomobject]@{ Kind = "panopto"; Source = $url; Embed = (Get-PanoptoEmbedUrl -Url $url) })
      continue
    }

    if ($url -match "gyazo\.com") {
      $gyazoLinks.Add($url)
      continue
    }

    $otherLinks.Add($url)
  }

  $html = New-Object System.Collections.Generic.List[string]

  if ($videoEmbeds.Count -gt 0) {
    $html.Add('<details class="accordion">')
    $html.Add("<summary>Video Resources ($($videoEmbeds.Count))</summary>")
    $html.Add('<div class="accordion-body media-stack">')

    $videoIndex = 1
    foreach ($video in $videoEmbeds) {
      $iframeClass = if ($video.Kind -eq "panopto") { "panopto-embed" } else { "video-embed" }
      $title = Escape-Html "$PageTitle video $videoIndex"
      $embed = Escape-Html $video.Embed
      $source = Escape-Html $video.Source

      $html.Add('<details class="accordion accordion--nested video-accordion">')
      $html.Add(('<summary>Video {0}</summary>' -f $videoIndex))
      $html.Add('<div class="accordion-body">')
      $html.Add('<article class="embed-card">')
      $html.Add(('<h3 class="embed-title">Video {0}</h3>' -f $videoIndex))
      $html.Add(('<iframe class="{0}" src="{1}" title="{2}" loading="lazy" allowfullscreen></iframe>' -f $iframeClass, $embed, $title))
      $html.Add(('<p><a href="{0}" target="_blank" rel="noopener noreferrer">Open source link</a></p>' -f $source))
      $html.Add('</article>')
      $html.Add('</div>')
      $html.Add('</details>')
      $videoIndex++
    }

    $html.Add('</div>')
    $html.Add('</details>')
  }

  if (@($ImagePaths).Count -gt 0 -or $otherLinks.Count -gt 0) {
    $html.Add('<section class="section-card">')
    $html.Add('<h2>Media Links</h2>')

    if (@($ImagePaths).Count -gt 0) {
      $html.Add('<div class="media-list">')
      $imgIndex = 1
      foreach ($img in @($ImagePaths)) {
        $safeImg = Escape-Html $img
        $alt = Escape-Html "$PageTitle image $imgIndex"
        $html.Add('<figure class="image-figure">')
        $html.Add(('<img src="{0}" alt="{1}" loading="lazy" />' -f $safeImg, $alt))
        $html.Add(('<figcaption class="image-caption">Extracted image {0} from source document.</figcaption>' -f $imgIndex))
        $html.Add('</figure>')
        $imgIndex++
      }
      $html.Add('</div>')
    }

    if ($otherLinks.Count -gt 0) {
      $html.Add('<h3>External Links</h3>')
      $html.Add('<div class="media-list">')
      foreach ($o in $otherLinks) {
        $safe = Escape-Html $o
        $html.Add(('<article class="link-card"><a href="{0}" target="_blank" rel="noopener noreferrer">{0}</a></article>' -f $safe))
      }
      $html.Add('</div>')
    }

    $html.Add('</section>')
  }

  return ($html -join "`n")
}

function Build-NavHtml {
  param(
    [System.Collections.Generic.List[object]]$Pages
  )

  $groups = @{
    "Students" = @()
    "Lecturers" = @()
    "Assessments" = @()
    "Other" = @()
  }

  foreach ($page in $Pages) {
    $category = [string]$page.Category
    if (-not $groups.ContainsKey($category)) {
      $category = "Other"
    }
    $groups[$category] += $page
  }

  $sb = New-Object System.Text.StringBuilder
  [void]$sb.AppendLine('<nav class="nav-rail" aria-label="Module navigation">')
  [void]$sb.AppendLine('<h2 class="nav-title">Module Navigation</h2>')
  [void]$sb.AppendLine('<p><a href="./index.html" data-page="home" data-label="Home">Home</a></p>')

  foreach ($groupName in @("Students", "Lecturers", "Assessments", "Other")) {
    $groupPages = $groups[$groupName] | Sort-Object -Property NavOrder
    if (-not $groupPages -or @($groupPages).Count -eq 0) { continue }

    [void]$sb.AppendLine("<h3>$groupName</h3>")
    [void]$sb.AppendLine("<ul>")

    foreach ($item in $groupPages) {
      $href = "pages/$($item.FileName)"
      $label = Escape-Html $item.NavTitle
      [void]$sb.AppendLine(('<li><a href="{0}" data-page="{0}" data-label="{1}">{1}</a></li>' -f $href, $label))
    }

    [void]$sb.AppendLine("</ul>")
  }

  [void]$sb.AppendLine('</nav>')
  return $sb.ToString()
}

function Build-ShellPage {
  param(
    [string]$Title,
    [string]$NavHtml,
    [string]$HomeHtml,
    [string]$StylesheetPath,
    [string]$ScriptPath
  )

  return @"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>$(Escape-Html $Title)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="${StylesheetPath}?v=20260805d" />
</head>
<body>
  <header class="module-header">
    <div class="module-header__inner">
      <h1>3D INTERACTIVE MEDIA DEVELOPMENT</h1>
      <p>Normalized content migration with a shared Neo-Brutalist style system.</p>
    </div>
  </header>
  <div class="site-shell">
$NavHtml
    <section class="content-shell" aria-live="polite">
      <div id="content-meta" class="content-meta">Home</div>
      <div class="content-body">
        <iframe id="content-frame" class="content-frame" title="Tutorial content"></iframe>
        <main class="content-area home-content" id="home-content">
          <h1 class="page-title">Home</h1>
$HomeHtml
        </main>
      </div>
    </section>
  </div>
  <script src="${ScriptPath}?v=20260805d"></script>
</body>
</html>
"@
}

function Build-ContentPage {
  param(
    [string]$Title,
    [string]$PageTitle,
    [string]$ContentHtml,
    [string]$StylesheetPath
  )

  return @"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>$(Escape-Html $Title)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="${StylesheetPath}?v=20260805l" />
</head>
<body class="content-page">
  <main class="content-area content-page-area" id="main-content">
    <h1 class="page-title">$(Escape-Html $PageTitle)</h1>
$ContentHtml
  </main>
  <script src="../assets/js/site.js?v=20260805f"></script>
</body>
</html>
"@
}

function Parse-Docx {
  param(
    [System.IO.FileInfo]$File,
    [int]$NavOrder
  )

  $sourceRel = Resolve-Path -Relative $File.FullName
  $baseName = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
  $slug = Slugify $baseName
  $outputFileName = "$slug.html"

  $zip = [System.IO.Compression.ZipFile]::OpenRead($File.FullName)
  try {
    $docPath = Get-OfficeDocumentPath -Zip $zip
    $docText = Read-ZipEntryText -Zip $zip -EntryPath $docPath
    if (-not $docText) {
      return [pscustomobject]@{
        SourceFile = $sourceRel
        FileName = $outputFileName
        TargetPage = "site/pages/$outputFileName"
        NavTitle = $baseName
        Category = if ($File.DirectoryName -match "Lecturers") { "Lecturers" } else { "Students" }
        NavOrder = $NavOrder
        PageTitle = $baseName
        ContentHtml = '<section class="section-card"><h2>Content unavailable</h2><p>This source document could not be parsed automatically and needs manual conversion.</p></section>'
        MediaAssets = "none"
        Confidence = "0.25"
        Risks = "Unable to locate primary document XML."
        RawCounts = [pscustomobject]@{ Paragraphs = 0; Lists = 0; Tables = 0; Images = 0; Links = 0; Gyazo = 0; YouTube = 0; Panopto = 0 }
      }
    }

    [xml]$docXml = $docText
    $ns = New-Object System.Xml.XmlNamespaceManager($docXml.NameTable)
    $ns.AddNamespace("w", "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
    $ns.AddNamespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
    $wNs = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    $relMap = Get-RelationshipMap -Zip $zip -DocumentPath $docPath
    $numberingMap = Get-NumberingFormatMap -Zip $zip -DocumentPath $docPath

    $paragraphs = New-Object System.Collections.Generic.List[object]
    $tables = New-Object System.Collections.Generic.List[object]
    $allUrls = New-Object System.Collections.Generic.List[string]

    $body = $docXml.SelectSingleNode("//w:body", $ns)
    if ($body) {
      foreach ($node in $body.ChildNodes) {
        if ($node.LocalName -eq "p") {
          $text = Get-ParagraphText -Paragraph $node -Ns $ns
          $styleNode = $node.SelectSingleNode("./w:pPr/w:pStyle", $ns)
          $style = ""
          if ($styleNode) {
            $style = $styleNode.GetAttribute("val", "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
          }

          $numPrNode = $node.SelectSingleNode("./w:pPr/w:numPr", $ns)
          $isList = $null -ne $numPrNode
          $numId = ""
          $listLevel = 0
          $listType = ""

          if ($numPrNode) {
            $numIdNode = $numPrNode.SelectSingleNode("./w:numId", $ns)
            if ($numIdNode) {
              $numId = $numIdNode.GetAttribute("val", $wNs)
            }

            $ilvlNode = $numPrNode.SelectSingleNode("./w:ilvl", $ns)
            if ($ilvlNode) {
              $ilvlRaw = $ilvlNode.GetAttribute("val", $wNs)
              $tmpLevel = 0
              if ([int]::TryParse($ilvlRaw, [ref]$tmpLevel)) {
                $listLevel = $tmpLevel
              }
            }

            if (-not [string]::IsNullOrWhiteSpace($numId)) {
              $key = "$numId|$listLevel"
              if ($numberingMap.ContainsKey($key)) {
                $listType = Get-ListTypeFromWordNumFormat -Format ([string]$numberingMap[$key])
              }
            }
          }

          $indentLevel = 0
          $indNode = $node.SelectSingleNode("./w:pPr/w:ind", $ns)
          if ($indNode) {
            $leftRaw = $indNode.GetAttribute("left", $wNs)
            if ([string]::IsNullOrWhiteSpace($leftRaw)) {
              $leftRaw = $indNode.GetAttribute("start", $wNs)
            }

            $leftTwips = 0
            if ([int]::TryParse($leftRaw, [ref]$leftTwips)) {
              $indentLevel = [math]::Floor($leftTwips / 360)
              if ($indentLevel -lt 0) { $indentLevel = 0 }
              if ($indentLevel -gt 6) { $indentLevel = 6 }
            }
          }

          $links = Get-ParagraphLinks -Paragraph $node -Ns $ns -RelMap $relMap
          $urlsInText = Get-UrlsFromText -Text $text

          foreach ($u in $links + $urlsInText) {
            $cleanUrl = Normalize-Url $u
            if (-not [string]::IsNullOrWhiteSpace($cleanUrl) -and -not $allUrls.Contains($cleanUrl)) {
              $allUrls.Add($cleanUrl)
            }
          }

          $textLines = @($text -split "`r?`n" | ForEach-Object { $_.Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
          if (-not $textLines -or $textLines.Count -eq 0) {
            $textLines = @($text)
          }

          foreach ($line in $textLines) {
            $lineSegments = Split-InlineNumberedSegments -Text $line
            foreach ($segment in $lineSegments) {
              $seg = $segment.Trim()
              if ([string]::IsNullOrWhiteSpace($seg)) { continue }

              $paragraphs.Add([pscustomobject]@{
                  Text = $seg
                  Style = $style
                  IsList = $isList
                  NumId = $numId
                  ListLevel = $listLevel
                  ListType = $listType
                  IndentLevel = $indentLevel
                  Links = $links
                })
            }
          }
        }

        if ($node.LocalName -eq "tbl") {
          $rows = New-Object System.Collections.Generic.List[object]
          $rowNodes = $node.SelectNodes("./w:tr", $ns)
          foreach ($row in $rowNodes) {
            $cells = New-Object System.Collections.Generic.List[string]
            $cellNodes = $row.SelectNodes("./w:tc", $ns)
            foreach ($cell in $cellNodes) {
              $cellTexts = $cell.SelectNodes(".//w:t", $ns) | ForEach-Object { [string]$_.InnerText }
              $cells.Add((($cellTexts -join " ").Trim()))
            }
            $rows.Add($cells)
          }
          $tables.Add($rows)
        }
      }
    }

    $imagePaths = New-Object System.Collections.Generic.List[string]
    foreach ($img in @(Copy-DocxMedia -Zip $zip -DocumentPath $docPath -Slug $slug)) {
      if ($img) {
        $imagePaths.Add([string]$img)
      }
    }

    $firstText = ($paragraphs | Where-Object { $_.Text -and $_.Text.Trim() -and $_.Text -notmatch "^https?://" } | Select-Object -First 1)
    $pageTitle = if ($firstText) { [string]$firstText.Text } else { $baseName }

    $contentCore = Convert-ParagraphsToHtml -Paragraphs $paragraphs -PageTitle $pageTitle
    $tableHtml = Convert-TablesToHtml -Tables $tables
    $mediaHtml = Convert-MediaToHtml -Urls $allUrls -ImagePaths $imagePaths -PageTitle $pageTitle
    $combinedHtml = @($contentCore, $tableHtml, $mediaHtml) -join "`n"

    $paragraphCount = @($paragraphs | Where-Object { $_.Text -and $_.Text.Trim() }).Count
    $listCount = @($paragraphs | Where-Object { $_.IsList }).Count
    $tableCount = $tables.Count
    $imageCount = $imagePaths.Count
    $linkCount = $allUrls.Count
    $gyazoCount = @($allUrls | Where-Object { $_ -match "gyazo\.com" }).Count
    $ytCount = @($allUrls | Where-Object { $_ -match "youtube\.com|youtu\.be" }).Count
    $panoptoCount = @($allUrls | Where-Object { $_ -match "panopto" }).Count

    $confidence = 0.92
    $risks = New-Object System.Collections.Generic.List[string]

    if ($paragraphCount -lt 20) {
      $confidence -= 0.1
      $risks.Add("Low paragraph count; verify extracted structure.")
    }

    if ($tableCount -gt 0) {
      $confidence -= 0.08
      $risks.Add("Table semantics converted generically; verify headers.")
    }

    if ($imageCount -gt 0) {
      $confidence -= 0.05
      $risks.Add("Image placement inferred into media section, not original in-flow position.")
    }

    if ($gyazoCount -gt 20) {
      $confidence -= 0.08
      $risks.Add("Large number of Gyazo links; preview availability may vary by source asset.")
    }

    if ($baseName -match "\(2\)") {
      $confidence -= 0.06
      $risks.Add("Duplicate filename variant detected; confirm canonical source.")
    }

    if ($confidence -lt 0.4) { $confidence = 0.4 }

    $category = if ($File.DirectoryName -match "Lecturers") { "Lecturers" } else { "Students" }

    return [pscustomobject]@{
      SourceFile = $sourceRel
      FileName = $outputFileName
      TargetPage = "site/pages/$outputFileName"
      NavTitle = $baseName
      Category = $category
      NavOrder = $NavOrder
      PageTitle = $pageTitle
      ContentHtml = $combinedHtml
      MediaAssets = if ($imageCount -gt 0) { "assets/media/$slug/*" } else { "none" }
      Confidence = ("{0:N2}" -f $confidence)
      Risks = if ($risks.Count -gt 0) { ($risks -join " ") } else { "Low risk in automated conversion." }
      RawCounts = [pscustomobject]@{
        Paragraphs = $paragraphCount
        Lists = $listCount
        Tables = $tableCount
        Images = $imageCount
        Links = $linkCount
        Gyazo = $gyazoCount
        YouTube = $ytCount
        Panopto = $panoptoCount
      }
    }
  } finally {
    $zip.Dispose()
  }
}

function Parse-QuizPage {
  param(
    [string]$QuizPath,
    [int]$NavOrder
  )

  $raw = Get-Content -Path $QuizPath -Raw
  $title = "Unity3D Physics Quiz"
  $titleMatch = [regex]::Match($raw, "<title>(.*?)</title>", "Singleline,IgnoreCase")
  if ($titleMatch.Success) {
    $title = $titleMatch.Groups[1].Value.Trim()
  }

  $scriptBody = ""
  $scriptMatch = [regex]::Match($raw, "<script>([\s\S]*?)</script>", "IgnoreCase")
  if ($scriptMatch.Success) {
    $scriptBody = $scriptMatch.Groups[1].Value
  }

  $content = @"
<section class="section-card">
  <p class="meta-line">10 random beginner questions from a reusable question pool.</p>
  <div class="quiz-container">
    <div id="quiz"></div>
    <div class="controls">
      <button id="submit" class="btn">Submit Quiz</button>
      <button id="refresh" class="btn btn-secondary">Refresh Questions</button>
      <div class="spacer"></div>
      <p class="meta-line">Refresh to practice different combinations.</p>
    </div>
    <div id="results"></div>
  </div>
</section>
<script>
$scriptBody
</script>
"@

  return [pscustomobject]@{
    SourceFile = "./Tut 08 Physics Quiz RBCT.html"
    FileName = "tut-08-physics-quiz-rbct.html"
    TargetPage = "site/pages/tut-08-physics-quiz-rbct.html"
    NavTitle = "Tut 08 Physics Quiz"
    Category = "Assessments"
    NavOrder = $NavOrder
    PageTitle = $title
    ContentHtml = $content
    MediaAssets = "none"
    Confidence = "0.98"
    Risks = "Script behavior preserved, but quiz UI was restyled to shared components."
    RawCounts = [pscustomobject]@{
      Paragraphs = 1
      Lists = 0
      Tables = 0
      Images = 0
      Links = 0
      Gyazo = 0
      YouTube = 0
      Panopto = 0
    }
  }
}

function Test-EmbedOutsideCollapsed {
  param([string]$Html)
  $pattern = "<details\b[^>]*>|</details>|<iframe\b[^>]*>"
  $tagMatches = [regex]::Matches($Html, $pattern, "IgnoreCase")
  $depth = 0

  foreach ($m in $tagMatches) {
    $tag = $m.Value
    if ($tag -match "^<details\b") {
      $depth++
      continue
    }

    if ($tag -match "^</details") {
      if ($depth -gt 0) { $depth-- }
      continue
    }

    if ($tag -match "^<iframe\b") {
      if ($tag -match "content-frame") {
        continue
      }

      if ($depth -eq 0) {
        return $true
      }
    }
  }

  return $false
}

function Write-ValidationReport {
  param(
    [string]$SiteDirectory,
    [string]$OutputPath
  )

  $files = Get-ChildItem -Path $SiteDirectory -Recurse -Filter *.html

  $inlineStyleViolations = New-Object System.Collections.Generic.List[string]
  $styleBlockViolations = New-Object System.Collections.Generic.List[string]
  $missingSharedStylesheet = New-Object System.Collections.Generic.List[string]
  $missingContainer = New-Object System.Collections.Generic.List[string]
  $detailsOpenViolations = New-Object System.Collections.Generic.List[string]
  $embedOutsideDetails = New-Object System.Collections.Generic.List[string]

  foreach ($file in $files) {
    $raw = Get-Content -Path $file.FullName -Raw
    $relative = Resolve-Path -Relative $file.FullName

    if ($raw -match "<[^>]+\sstyle\s*=") {
      $inlineStyleViolations.Add($relative)
    }

    if ($raw -match "<style\b") {
      $styleBlockViolations.Add($relative)
    }

    $expected = if ($file.FullName -like "*\site\pages\*") { "../assets/css/site.css" } else { "assets/css/site.css" }
    if ($raw -notmatch [regex]::Escape($expected)) {
      $missingSharedStylesheet.Add($relative)
    }

    if ($file.FullName -like "*\site\pages\*") {
      if ($raw -notmatch "content-page") {
        $missingContainer.Add($relative)
      }
    } else {
      if ($raw -notmatch "site-shell") {
        $missingContainer.Add($relative)
      }
    }

    if ($raw -match "<details[^>]*\sopen\b") {
      $detailsOpenViolations.Add($relative)
    }

    if (Test-EmbedOutsideCollapsed -Html $raw) {
      $embedOutsideDetails.Add($relative)
    }
  }

  $lines = New-Object System.Collections.Generic.List[string]
  $lines.Add("# Validation Report")
  $lines.Add("")
  $lines.Add("Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")")
  $lines.Add("")
  $lines.Add("## Compliance Summary")
  $lines.Add("")
  $lines.Add("| Check | Violations |")
  $lines.Add("|---|---:|")
  $lines.Add("| Pages containing inline style attributes | $($inlineStyleViolations.Count) |")
  $lines.Add("| Pages containing style blocks | $($styleBlockViolations.Count) |")
  $lines.Add("| Pages missing shared stylesheet link | $($missingSharedStylesheet.Count) |")
  $lines.Add("| Pages missing shared layout container | $($missingContainer.Count) |")
  $lines.Add("| Details sections with open enabled | $($detailsOpenViolations.Count) |")
  $lines.Add("| Embed blocks outside collapsed sections | $($embedOutsideDetails.Count) |")
  $lines.Add("")

  $detailSets = @(
    @{ Name = "Inline style attribute violations"; Items = $inlineStyleViolations },
    @{ Name = "Per-page style block violations"; Items = $styleBlockViolations },
    @{ Name = "Missing shared stylesheet link"; Items = $missingSharedStylesheet },
    @{ Name = "Missing shared layout container"; Items = $missingContainer },
    @{ Name = "Details open by default"; Items = $detailsOpenViolations },
    @{ Name = "Embeds outside collapsed details"; Items = $embedOutsideDetails }
  )

  foreach ($set in $detailSets) {
    $lines.Add("## $($set.Name)")
    if ($set.Items.Count -eq 0) {
      $lines.Add("")
      $lines.Add("None.")
      $lines.Add("")
      continue
    }

    $lines.Add("")
    foreach ($item in $set.Items) {
      $lines.Add("- $item")
    }
    $lines.Add("")
  }

  Set-Content -Path $OutputPath -Value ($lines -join "`n") -Encoding UTF8
}

$docxFiles = Get-ChildItem -Path $repoRoot -Recurse -File -Filter *.docx |
  Sort-Object -Property FullName

$pages = New-Object System.Collections.Generic.List[object]
$order = 1
foreach ($doc in $docxFiles) {
  $pages.Add((Parse-Docx -File $doc -NavOrder $order))
  $order++
}

$quizPath = Join-Path $repoRoot "Tut 08 Physics Quiz RBCT.html"
if (Test-Path $quizPath) {
  $pages.Add((Parse-QuizPage -QuizPath $quizPath -NavOrder $order))
}

$navForShell = Build-NavHtml -Pages $pages

foreach ($page in $pages) {
  $content = [string]$page.ContentHtml
  $html = Build-ContentPage `
    -Title ("3DIMD | " + [string]$page.PageTitle) `
    -PageTitle ([string]$page.PageTitle) `
    -ContentHtml $content `
    -StylesheetPath "../assets/css/site.css"

  $path = Join-Path $pagesRoot ([string]$page.FileName)
  Set-Content -Path $path -Value $html -Encoding UTF8
}

$homeLinks = New-Object System.Collections.Generic.List[string]
$homeLinks.Add('<section class="section-card">')
$homeLinks.Add('<h2>Site Migration Output</h2>')
$homeLinks.Add('<p>This site is generated from source DOCX and existing HTML materials into a normalized static structure with shared styles and semantic components.</p>')
$homeLinks.Add('</section>')

$homeLinks.Add('<section class="section-card">')
$homeLinks.Add('<h2>Sitemap</h2>')

$grouped = $pages | Group-Object -Property Category
foreach ($group in $grouped) {
  $homeLinks.Add("<h3>$(Escape-Html $group.Name)</h3>")
  $homeLinks.Add("<ul>")
  foreach ($item in ($group.Group | Sort-Object -Property NavOrder)) {
    $safeName = Escape-Html $item.NavTitle
    $safeHref = Escape-Html ("pages/" + $item.FileName)
    $homeLinks.Add(('<li><a href="{0}" data-page="{0}" data-label="{1}">{1}</a></li>' -f $safeHref, $safeName))
  }
  $homeLinks.Add("</ul>")
}

$homeLinks.Add('</section>')

$homeHtml = Build-ShellPage `
  -Title "3DIMD Course Site" `
  -NavHtml $navForShell `
  -HomeHtml ($homeLinks -join "`n") `
  -StylesheetPath "assets/css/site.css" `
  -ScriptPath "assets/js/site.js"

Set-Content -Path (Join-Path $siteRoot "index.html") -Value $homeHtml -Encoding UTF8

$inventoryLines = New-Object System.Collections.Generic.List[string]
$inventoryLines.Add("# Migration Plan")
$inventoryLines.Add("")
$inventoryLines.Add("## Workflow")
$inventoryLines.Add("")
$inventoryLines.Add("1. Discover all source files and classify them by audience (students, lecturers, assessment).")
$inventoryLines.Add("2. Convert DOCX sources into semantic HTML blocks with shared component classes.")
$inventoryLines.Add("3. Normalize links, Gyazo references, and video embeds into common media components.")
$inventoryLines.Add("4. Generate one persistent shell page and lightweight content pages with shared stylesheet.")
$inventoryLines.Add("5. Run validation checks and publish a compliance report.")
$inventoryLines.Add("")
$inventoryLines.Add("## Information Architecture")
$inventoryLines.Add("")
$inventoryLines.Add("- Home: module overview and sitemap")
$inventoryLines.Add("- Students: tutorial pages sourced from student DOCX files")
$inventoryLines.Add("- Lecturers: lecturer guidance pages sourced from lecturer DOCX files")
$inventoryLines.Add("- Assessments: migrated quiz page")
$inventoryLines.Add("")
$inventoryLines.Add("## Naming Conventions")
$inventoryLines.Add("")
$inventoryLines.Add("- Pages: lowercase kebab-case filename derived from source title, stored in site/pages")
$inventoryLines.Add("- Media assets: site/assets/media/<page-slug>/<original-file>")
$inventoryLines.Add("- Shared assets: site/assets/css/site.css and site/assets/js/site.js")
$inventoryLines.Add("- Section classes: section-card, note, accordion, embed-card, image-figure, link-card")
$inventoryLines.Add("")
$inventoryLines.Add("## Shared Component Classes")
$inventoryLines.Add("")
$inventoryLines.Add("- Container/layout: module-header, site-shell, nav-rail, content-shell, content-frame, content-area")
$inventoryLines.Add("- Note/callout: note, note--important, note--tip")
$inventoryLines.Add("- Section card: section-card")
$inventoryLines.Add("- Accordion: accordion, accordion-body")
$inventoryLines.Add("- Video embed: video-embed")
$inventoryLines.Add("- Panopto embed: panopto-embed")
$inventoryLines.Add("- Image figure and caption: image-figure, image-caption")
$inventoryLines.Add("- Link card and media list: link-card, media-list")
$inventoryLines.Add("")
$inventoryLines.Add("## Content Inventory")
$inventoryLines.Add("")
$inventoryLines.Add("| Source file | Target page | Media assets needed | Parsing confidence | Risks / manual review notes |")
$inventoryLines.Add("|---|---|---|---:|---|")

foreach ($page in ($pages | Sort-Object -Property NavOrder)) {
  $source = ([string]$page.SourceFile).Replace("|", "\\|")
  $target = ([string]$page.TargetPage).Replace("|", "\\|")
  $media = ([string]$page.MediaAssets).Replace("|", "\\|")
  $confidence = [string]$page.Confidence
  $risks = ([string]$page.Risks).Replace("|", "\\|")
  $inventoryLines.Add("| $source | $target | $media | $confidence | $risks |")
}

$inventoryLines.Add("")
$inventoryLines.Add("## Automated Parsing Metrics")
$inventoryLines.Add("")
$inventoryLines.Add("| Source file | Paragraphs | Lists | Tables | Images | Links | Gyazo | YouTube | Panopto |")
$inventoryLines.Add("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

foreach ($page in ($pages | Sort-Object -Property NavOrder)) {
  $c = $page.RawCounts
  $inventoryLines.Add("| $($page.SourceFile) | $($c.Paragraphs) | $($c.Lists) | $($c.Tables) | $($c.Images) | $($c.Links) | $($c.Gyazo) | $($c.YouTube) | $($c.Panopto) |")
}

Set-Content -Path (Join-Path $docsRoot "migration-plan.md") -Value ($inventoryLines -join "`n") -Encoding UTF8

$authoringGuide = @"
# Authoring Guide

## Goal

Keep all future additions normalized, semantic, and compatible with the shared style system.

## Required Structure

1. Use the shared persistent shell page and shared stylesheet only.
2. Place content inside section-card blocks.
3. Use semantic tags only: h1-h3, p, ul, ol, figure, details/summary, iframe, section, nav, main.
4. Keep all video iframes inside collapsed details sections (no open attribute).

## Allowed Components

- Notes: note, note--important, note--tip
- Accordions: accordion with summary and accordion-body
- Embeds: video-embed for YouTube, panopto-embed for Panopto
- Media links: media-list and link-card
- Images: image-figure with image-caption

## Banned Patterns

- Inline style attributes
- Per-page style blocks
- Word-export markup and class names
- Layout deviations from the shared shell/content page templates

## Media Handling Rules

1. YouTube links: convert to an embed iframe in a collapsed video details section.
2. Panopto links: convert to an embed iframe in a collapsed video details section.
3. Other media links: use link-card entries in a media-list.
4. Gyazo links: use preview image when possible, with a clickable fallback link.

## QA Checklist

1. No style="..." attributes in generated page HTML.
2. No style blocks in page HTML.
3. Shared stylesheet linked correctly.
4. site-shell on index and content-page class on tutorial pages.
5. No details open by default.
6. No iframe outside details.
"@

Set-Content -Path (Join-Path $docsRoot "authoring-guide.md") -Value $authoringGuide -Encoding UTF8

Write-ValidationReport -SiteDirectory $siteRoot -OutputPath (Join-Path $reportsRoot "validation-report.md")

Write-Host "Migration complete. Generated site, plan, authoring guide, and validation report."
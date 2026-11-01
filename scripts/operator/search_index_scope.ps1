<#
.SYNOPSIS
  Keep Windows Search (SearchIndexer) out of the MTS work trees and agent state folders. Card nuc-defender-cpu.
.DESCRIPTION
  Every sync.py start creates a git worktree under C:\Users\<user>\IdeaProjects (7-8k files plus .git). That folder is
  inside the default C:\Users index scope, so SearchIndexer re-crawls each new tree: measured 15-19 CPU-s per ~7k files
  (0 s for the same copy outside the index). The catalog had grown to 5.2 GB. This adds EXCLUDE scope rules, so nothing
  under those folders is indexed, and (with -Reset) rebuilds the catalog. Real-time Defender is not touched.
  Needs an elevated shell (it re-launches itself, one UAC prompt). Idempotent.

  .\search_index_scope.ps1            add the exclusion rules, rebuild the catalog
  .\search_index_scope.ps1 -Check     list the rules and whether each folder is in the crawl scope, change nothing
  .\search_index_scope.ps1 -Remove    take the rules back out (index scope returns to the Windows default)
  .\search_index_scope.ps1 -NoReset   add the rules but keep the old 5 GB catalog
#>
[CmdletBinding()]
param([switch]$Check, [switch]$Remove, [switch]$NoReset)

$ErrorActionPreference = 'Stop'
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"")
    foreach ($n in 'Check', 'Remove', 'NoReset') { if ((Get-Variable $n).Value) { $argList += "-$n" } }
    Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList $argList -Verb RunAs -Wait
    return
}

$logDir = 'F:\MTS\scratch'
if (-not (Test-Path $logDir)) { $logDir = $env:TEMP }
try { Start-Transcript -Path (Join-Path $logDir 'search_index_scope.log') -Force | Out-Null } catch { }

$up = $env:USERPROFILE
$folders = @(
    "$up\IdeaProjects\",
    "$up\.claude\", "$up\.gemini\", "$up\.codex\", "$up\.cache\", "$up\.m2\", "$up\.gradle\", "$up\.vscode\"
)

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
[ComImport, Guid("AB310581-AC80-11D1-8DF3-00C04FB6EF69"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface ISearchManager {
    void GetIndexerVersionStr([MarshalAs(UnmanagedType.LPWStr)] out string s);
    void GetIndexerVersion(out uint hi, out uint lo);
    void GetParameter([MarshalAs(UnmanagedType.LPWStr)] string n, out IntPtr v);
    void SetParameter([MarshalAs(UnmanagedType.LPWStr)] string n, IntPtr v);
    void get_ProxyName([MarshalAs(UnmanagedType.LPWStr)] out string s);
    void get_BypassList([MarshalAs(UnmanagedType.LPWStr)] out string s);
    void SetProxy(int a, int b, [MarshalAs(UnmanagedType.LPWStr)] string c, [MarshalAs(UnmanagedType.LPWStr)] string d);
    void GetCatalog([MarshalAs(UnmanagedType.LPWStr)] string name, [MarshalAs(UnmanagedType.Interface)] out ISearchCatalogManager cat);
}
[ComImport, Guid("AB310581-AC80-11D1-8DF3-00C04FB6EF50"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface ISearchCatalogManager {
    void get_Name([MarshalAs(UnmanagedType.LPWStr)] out string s);
    void GetParameter([MarshalAs(UnmanagedType.LPWStr)] string n, out IntPtr v);
    void SetParameter([MarshalAs(UnmanagedType.LPWStr)] string n, IntPtr v);
    void GetCatalogStatus(out int status, out int phase);
    void Reset();
    void Reindex();
    void ReindexMatchingURLs([MarshalAs(UnmanagedType.LPWStr)] string p, int reason);
    void ReindexSearchRoot([MarshalAs(UnmanagedType.LPWStr)] string p);
    void put_ConnectTimeout(uint v);
    void get_ConnectTimeout(out uint v);
    void put_DataTimeout(uint v);
    void get_DataTimeout(out uint v);
    void NumberOfItems(out int n);
    void NumberOfItemsToIndex(out int a, out int b, out int c);
    void URLBeingIndexed([MarshalAs(UnmanagedType.LPWStr)] out string s);
    void GetURLIndexingState([MarshalAs(UnmanagedType.LPWStr)] string u, out int st);
    void GetPersistentItemsChangedSink([MarshalAs(UnmanagedType.Interface)] out object o);
    void RegisterViewForNotification([MarshalAs(UnmanagedType.LPWStr)] string a, IntPtr b, out uint c);
    void GetItemsChangedSink(IntPtr a, ref Guid b, out IntPtr c, out IntPtr d, out uint e);
    void UnregisterViewForNotification(uint c);
    void SetExtensionClusion([MarshalAs(UnmanagedType.LPWStr)] string e, int f);
    void EnumerateExcludedExtensions(out IntPtr o);
    void GetQueryHelper(out IntPtr o);
    void put_DiacriticSensitivity(int v);
    void get_DiacriticSensitivity(out int v);
    void GetCrawlScopeManager([MarshalAs(UnmanagedType.Interface)] out ISearchCrawlScopeManager m);
}
[ComImport, Guid("AB310581-AC80-11D1-8DF3-00C04FB6EF55"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface ISearchCrawlScopeManager {
    void AddDefaultScopeRule([MarshalAs(UnmanagedType.LPWStr)] string u, int include, uint follow);
    void AddRoot(IntPtr r);
    void RemoveRoot([MarshalAs(UnmanagedType.LPWStr)] string u);
    void EnumerateRoots(out IntPtr o);
    void AddHierarchicalScope([MarshalAs(UnmanagedType.LPWStr)] string u, int include, int defaultv, int overrideChildren);
    void AddUserScopeRule([MarshalAs(UnmanagedType.LPWStr)] string u, int include, int overrideChildren, uint follow);
    void RemoveScopeRule([MarshalAs(UnmanagedType.LPWStr)] string u);
    void EnumerateScopeRules(out IntPtr o);
    void HasParentScopeRule([MarshalAs(UnmanagedType.LPWStr)] string u, out int b);
    void HasChildScopeRule([MarshalAs(UnmanagedType.LPWStr)] string u, out int b);
    void IncludedInCrawlScope([MarshalAs(UnmanagedType.LPWStr)] string u, out int b);
    void IncludedInCrawlScopeEx([MarshalAs(UnmanagedType.LPWStr)] string u, out int b, out int reason);
    void RevertToDefaultScopes();
    void SaveAll();
}
public static class SearchApi {
    static ISearchCatalogManager cat;
    static ISearchCrawlScopeManager scope;
    public static void Open() {
        ISearchManager m = (ISearchManager)Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("7D096C5F-AC08-4F1F-BEB7-5C22C517CE39")));
        m.GetCatalog("SystemIndex", out cat);
        cat.GetCrawlScopeManager(out scope);
    }
    public static bool InScope(string url) { int b; scope.IncludedInCrawlScope(url, out b); return b != 0; }
    public static void Exclude(string url) { scope.AddUserScopeRule(url, 0, 1, 0); }
    public static void RemoveRule(string url) { scope.RemoveScopeRule(url); }
    public static void Save() { scope.SaveAll(); }
    public static int Items() { int n; cat.NumberOfItems(out n); return n; }
    public static void Rebuild() { cat.Reset(); }
}
'@

# backup of the current rule set (registry copy), for the undo
$regKey = 'HKLM:\SOFTWARE\Microsoft\Windows Search\CrawlScopeManager\Windows\SystemIndex\WorkingSetRules'
$backup = Join-Path $logDir 'search_scope_before.txt'
if (-not (Test-Path $backup)) {
    Get-ChildItem $regKey | ForEach-Object { $r = Get-ItemProperty $_.PSPath; '{0} default={1} include={2}' -f $r.URL, $r.Default, $r.Include } | Set-Content $backup
    Write-Host "backup of the previous rules: $backup"
}

[SearchApi]::Open()
function InScope($path) { [SearchApi]::InScope('file:///' + $path) }

foreach ($f in $folders) {
    if (-not (Test-Path $f)) { continue }
    $url = 'file:///' + $f
    $was = InScope $f
    if ($Check) { Write-Host ("{0,-60} in crawl scope: {1}" -f $f, $was); continue }
    if ($Remove) {
        try { [SearchApi]::RemoveRule($url); Write-Host "removed rule  $f" } catch { Write-Host "no rule       $f" }
    } elseif ($was) {
        [SearchApi]::Exclude($url)
        Write-Host "excluded      $f"
    } else {
        Write-Host "already out   $f"
    }
}
if (-not $Check) { [SearchApi]::Save() }

if (-not $Check -and -not $Remove -and -not $NoReset) {
    Write-Host ("rebuilding the catalog ({0} items before)" -f [SearchApi]::Items())
    [SearchApi]::Rebuild()
}
Write-Host 'done'
try { Stop-Transcript | Out-Null } catch { }

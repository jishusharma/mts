# concurrency.ps1 - cap concurrent handled requests.
# Above cap, agent replies 429 (with a reason) and closes. Commands run as parallel child processes (v0.7.0).

$script:MaxConcurrent = 8
$script:ConnSem = [System.Threading.SemaphoreSlim]::new($script:MaxConcurrent, $script:MaxConcurrent)

function Test-ConnectionSlot {
    return $script:ConnSem.Wait(0)
}

function Release-ConnectionSlot {
    try { $script:ConnSem.Release() } catch {}
}
param([string]$AppName = "ipburger-demo-joy")

# Array lokasi random untuk rotasi
$locations = @("au", "us", "ca", "uk", "de", "fr", "nl", "sg")

function Get-Credential {
    $cred = heroku config:get IPB_SOCKS5 --app $AppName 2>$null
    if ($LASTEXITCODE -eq 0 -and $cred -and $cred.Trim() -ne "") {
        return $cred.Trim()
    }
    return $null
}

# Fungsi untuk menguji koneksi HTTP ke website Growtopia
function Test-GrowtopiaHTTP {
    param($Proxy)
    
    if (-not $Proxy -or $Proxy.Trim() -eq "") {
        Write-Host "[WARNING] Proxy credential kosong" -ForegroundColor Yellow
        return "ERROR"
    }
    
    try {
        Write-Host "[INFO] Testing HTTP connection to Growtopia website..." -ForegroundColor Cyan
        
        # Extract proxy credentials and address from URL
        if ($Proxy -match "socks5h?://([^:]+):([^@]+)@([^:]+):([0-9]+)") {
            $proxyUser = $Matches[1]
            $proxyPass = $Matches[2]
            $proxyHost = $Matches[3]
            $proxyPort = $Matches[4]
            
            # Format proxy dalam format ip:port:username:password untuk kebutuhan masa depan
            $formattedProxy = "${proxyHost}:${proxyPort}:${proxyUser}:${proxyPass}"
            
            # Menggunakan curl.exe dari Windows untuk test koneksi
            # Pastikan menggunakan curl.exe bawaan Windows, bukan alias PowerShell
            $curlPath = "C:\Windows\System32\curl.exe"
            
            if (-not (Test-Path $curlPath)) {
                Write-Host "[WARNING] curl.exe tidak ditemukan di $curlPath, mencoba menggunakan curl dari PATH" -ForegroundColor Yellow
                $curlPath = "curl.exe"
            }
            
            # Gunakan curl dengan parameter socks5 yang benar
            $curlCommand = "& `"$curlPath`" -s -o nul -w '%{http_code}' --connect-timeout 15 "
            $curlCommand += "--proxy-user `"$proxyUser`:$proxyPass`" "
            $curlCommand += "--proxy `"socks5://$proxyHost`:$proxyPort`" "
            $curlCommand += "https://growtopiagame.com/"
            
            Write-Host "[INFO] Connecting with curl..." -ForegroundColor Cyan
            $response = Invoke-Expression $curlCommand 2>$null
            
            if ($LASTEXITCODE -eq 0 -and $response -match "^\d+$") {
                Write-Host "[SUCCESS] HTTP Response received: $response" -ForegroundColor Green
                return $response.ToString()
            } else {
                Write-Host "[ERROR] HTTP Request failed with curl" -ForegroundColor Red
                
                # Fallback ke metode alternatif menggunakan PowerShell dan file .NET
                Write-Host "[INFO] Trying alternative HTTP method..." -ForegroundColor Yellow
                
                # Buat file C# untuk menggunakan SOCKS5 proxy
                $tempDir = [System.IO.Path]::GetTempPath()
                $csFile = Join-Path $tempDir "ProxyTest.cs"
                $exeFile = Join-Path $tempDir "ProxyTest.exe"
                
                $csCode = @"
                using System;
                using System.Net;
                using System.Net.Http;
                using System.Threading.Tasks;
                
                class ProxyTest {
                    static int Main(string[] args) {
                        try {
                            string proxyHost = "$proxyHost";
                            int proxyPort = $proxyPort;
                            string proxyUser = "$proxyUser";
                            string proxyPass = "$proxyPass";
                            
                            // Konfigurasi proxy menggunakan WebRequest
                            WebRequest.DefaultWebProxy = new WebProxy("socks5://" + proxyHost + ":" + proxyPort);
                            WebRequest.DefaultWebProxy.Credentials = new NetworkCredential(proxyUser, proxyPass);
                            
                            // Buat request ke Growtopia
                            var request = WebRequest.Create("https://growtopiagame.com/");
                            request.Proxy = WebRequest.DefaultWebProxy;
                            request.Timeout = 15000; // 15 detik
                            
                            // Dapatkan response
                            using (var response = request.GetResponse() as HttpWebResponse) {
                                Console.WriteLine((int)response.StatusCode);
                                return 0;
                            }
                        } catch (WebException ex) {
                            if (ex.Response != null) {
                                var response = ex.Response as HttpWebResponse;
                                Console.WriteLine((int)response.StatusCode);
                                return 0;
                            }
                            Console.WriteLine("ERROR");
                            return 1;
                        } catch (Exception) {
                            Console.WriteLine("ERROR");
                            return 1;
                        }
                    }
                }
"@
                
                # Tulis file C#
                $csCode | Out-File -FilePath $csFile -Encoding utf8
                
                # Compile dan jalankan
                $compileCommand = "& 'C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe' /nologo /out:'$exeFile' '$csFile'"
                Invoke-Expression $compileCommand | Out-Null
                
                if (Test-Path $exeFile) {
                    $response = & $exeFile
                    
                    # Bersihkan file temporary
                    Remove-Item -Path $csFile -Force -ErrorAction SilentlyContinue
                    Remove-Item -Path $exeFile -Force -ErrorAction SilentlyContinue
                    
                    if ($response -match "^\d+$") {
                        Write-Host "[SUCCESS] Alternative HTTP method response: $response" -ForegroundColor Green
                        return $response.ToString()
                    }
                }
                
                return "ERROR"
            }
        } else {
            Write-Host "[ERROR] Invalid proxy format: $Proxy" -ForegroundColor Red
            return "ERROR"
        }
    } catch {
        Write-Host "[ERROR] Unexpected Error in HTTP test: $($_.Exception.Message)" -ForegroundColor Red
        return "ERROR"
    }
}

# Fungsi untuk menguji koneksi Socks5
function Test-Socks5 {
    param($Proxy)
    
    if (-not $Proxy -or $Proxy.Trim() -eq "") {
        Write-Host "[WARNING] Proxy credential kosong" -ForegroundColor Yellow
        return "ERROR"
    }
    
    try {
        Write-Host "[INFO] Testing Socks5 connection..." -ForegroundColor Cyan
        
        # Extract proxy credentials and address from URL
        if ($Proxy -match "socks5h?://([^:]+):([^@]+)@([^:]+):([0-9]+)") {
            $proxyUser = $Matches[1]
            $proxyPass = $Matches[2]
            $proxyHost = $Matches[3]
            $proxyPort = $Matches[4]
            
            # Menggunakan curl untuk test koneksi Socks5 ke google.com (reliable test)
            $curlPath = "C:\Windows\System32\curl.exe"
            
            if (-not (Test-Path $curlPath)) {
                Write-Host "[WARNING] curl.exe tidak ditemukan di $curlPath, mencoba menggunakan curl dari PATH" -ForegroundColor Yellow
                $curlPath = "curl.exe"
            }
            
            # Gunakan curl dengan parameter socks5 yang benar
            $curlCommand = "& `"$curlPath`" -s -o nul -w '%{http_code}' --connect-timeout 10 "
            $curlCommand += "--proxy-user `"$proxyUser`:$proxyPass`" "
            $curlCommand += "--proxy `"socks5://$proxyHost`:$proxyPort`" "
            $curlCommand += "https://www.google.com/"
            
            Write-Host "[INFO] Testing Socks5 with curl..." -ForegroundColor Cyan
            $response = Invoke-Expression $curlCommand 2>$null
            
            if ($LASTEXITCODE -eq 0 -and $response -match "^\d+$") {
                Write-Host "[SUCCESS] Socks5 working! Response: $response" -ForegroundColor Green
                return "OK"
            } else {
                Write-Host "[ERROR] Socks5 test failed" -ForegroundColor Red
                return "ERROR"
            }
        } else {
            Write-Host "[ERROR] Invalid proxy format for Socks5 test: $Proxy" -ForegroundColor Red
            return "ERROR"
        }
    } catch {
        Write-Host "[ERROR] Unexpected Error in Socks5 test: $($_.Exception.Message)" -ForegroundColor Red
        return "ERROR"
    }
}

# Fungsi untuk menguji koneksi ke server game Growtopia (GT)
function Test-GrowtopiaGameServer {
    param($Proxy)
    
    if (-not $Proxy -or $Proxy.Trim() -eq "") {
        Write-Host "[WARNING] Proxy credential kosong" -ForegroundColor Yellow
        return "ERROR"
    }
    
    try {
        Write-Host "[INFO] Testing connection to Growtopia game server..." -ForegroundColor Cyan
        
        # Extract proxy credentials and address from URL
        if ($Proxy -match "socks5h?://([^:]+):([^@]+)@([^:]+):([0-9]+)") {
            $proxyUser = $Matches[1]
            $proxyPass = $Matches[2]
            $proxyHost = $Matches[3]
            $proxyPort = $Matches[4]
            
            # Cek apakah curl tersedia
            $curlAvailable = $false
            try {
                $curlCheck = Get-Command curl -ErrorAction SilentlyContinue
                if ($curlCheck) { $curlAvailable = $true }
            } catch {
                $curlAvailable = $false
            }
            
            if (-not $curlAvailable) {
                Write-Host "[WARNING] curl tidak tersedia, mencoba alternatif..." -ForegroundColor Yellow
            }
            
            # Metode 1: Test koneksi TCP sederhana menggunakan Test-NetConnection
            try {
                Write-Host "[INFO] Testing TCP connection to login.growtopiagame.com:17091..." -ForegroundColor Cyan
                
                # Gunakan Test-NetConnection untuk test koneksi TCP
                $testResult = Test-NetConnection -ComputerName "login.growtopiagame.com" -Port 17091 -WarningAction SilentlyContinue
                
                if ($testResult.TcpTestSucceeded) {
                    Write-Host "[SUCCESS] TCP connection successful!" -ForegroundColor Green
                    return "OK"
                }
            } catch {
                Write-Host "[WARNING] TCP test failed, mencoba metode lain..." -ForegroundColor Yellow
            }
            
            # Metode 2: Test menggunakan curl dengan format yang benar
            if ($curlAvailable) {
                try {
                    Write-Host "[INFO] Testing with curl..." -ForegroundColor Cyan
                    
                    # Build curl command dengan benar
                    $curlArgs = @(
                        "--socks5", "$proxyHost`:$proxyPort",
                        "--proxy-user", "$proxyUser`:$proxyPass",
                        "--connect-timeout", "10",
                        "--max-time", "15",
                        "-s", "-v",
                        "https://login.growtopiagame.com:17091"
                    )
                    
                    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
                    $processInfo.FileName = "curl"
                    $processInfo.Arguments = $curlArgs -join " "
                    $processInfo.RedirectStandardOutput = $true
                    $processInfo.RedirectStandardError = $true
                    $processInfo.UseShellExecute = $false
                    $processInfo.CreateNoWindow = $true
                    
                    $process = New-Object System.Diagnostics.Process
                    $process.StartInfo = $processInfo
                    $process.Start() | Out-Null
                    $process.WaitForExit(15000) | Out-Null
                    
                    if ($process.ExitCode -eq 0) {
                        Write-Host "[SUCCESS] Connected to Growtopia server via curl!" -ForegroundColor Green
                        return "OK"
                    }
                } catch {
                    Write-Host "[WARNING] Curl test failed: $($_.Exception.Message)" -ForegroundColor Yellow
                }
            }
            
            # Metode 3: Test koneksi menggunakan PowerShell WebClient
            try {
                Write-Host "[INFO] Testing with WebClient..." -ForegroundColor Cyan
                
                # Buat WebClient dengan proxy
                $webClient = New-Object System.Net.WebClient
                $proxyUri = New-Object System.Uri("http://$proxyHost`:$proxyPort")
                $webProxy = New-Object System.Net.WebProxy($proxyUri, $true)
                $webProxy.Credentials = New-Object System.Net.NetworkCredential($proxyUser, $proxyPass)
                $webClient.Proxy = $webProxy
                
                # Test koneksi ke server_data.php sebagai alternatif
                $response = $webClient.DownloadString("https://www.growtopiagame.com/server_data.php")
                
                if ($response -and $response.Length -gt 0) {
                    Write-Host "[SUCCESS] WebClient connection successful!" -ForegroundColor Green
                    return "OK"
                }
            } catch {
                Write-Host "[WARNING] WebClient test failed: $($_.Exception.Message)" -ForegroundColor Yellow
            }
            
            # Metode 4: Test koneksi ke growtopia1.com:17091
            try {
                Write-Host "[INFO] Testing connection to growtopia1.com:17091..." -ForegroundColor Cyan
                
                $testResult = Test-NetConnection -ComputerName "growtopia1.com" -Port 17091 -WarningAction SilentlyContinue
                
                if ($testResult.TcpTestSucceeded) {
                    Write-Host "[SUCCESS] Connected to growtopia1.com!" -ForegroundColor Green
                    return "OK"
                }
            } catch {
                Write-Host "[WARNING] growtopia1.com test failed: $($_.Exception.Message)" -ForegroundColor Yellow
            }
            
            Write-Host "[ERROR] Failed to connect to Growtopia game server" -ForegroundColor Red
            return "ERROR"
            
        } else {
            Write-Host "[ERROR] Invalid proxy format for GT server test: $Proxy" -ForegroundColor Red
            return "ERROR"
        }
    } catch {
        Write-Host "[ERROR] Unexpected Error in GT server test: $($_.Exception.Message)" -ForegroundColor Red
        return "ERROR"
    }
}

# Fungsi utama untuk menguji semua koneksi
function Test-Growtopia {
    param($Proxy)
    
    if (-not $Proxy -or $Proxy.Trim() -eq "") {
        Write-Host "[WARNING] Proxy credential kosong" -ForegroundColor Yellow
        return "ERROR"
    }
    
    try {
        Write-Host "[INFO] Testing all Growtopia connections..." -ForegroundColor Cyan
        
        # Test HTTP connection to Growtopia website
        $httpResult = Test-GrowtopiaHTTP $Proxy
        
        # Test Socks5 connection
        $socks5Result = Test-Socks5 $Proxy
        
        # Test Growtopia game server connection
        $gtResult = Test-GrowtopiaGameServer $Proxy
        
        # Display results
        Write-Host ""
        Write-Host "[RESULTS] Connection Test Results:" -ForegroundColor Magenta
        Write-Host "HTTP: $httpResult" -ForegroundColor $(if ($httpResult -eq "200") { "Green" } else { "Red" })
        Write-Host "Socks5: $socks5Result" -ForegroundColor $(if ($socks5Result -eq "OK") { "Green" } else { "Red" })
        Write-Host "GT Server: $gtResult" -ForegroundColor $(if ($gtResult -eq "OK") { "Green" } else { "Red" })
        
        # Return HTTP result for backward compatibility
        if ($httpResult -eq "200" -and $socks5Result -eq "OK" -and $gtResult -eq "OK") {
            Write-Host "[SUCCESS] All tests passed! This proxy is fully compatible with Growtopia!" -ForegroundColor Green
            return "200"
        } else {
            if ($httpResult -eq "200") {
                Write-Host "[PARTIAL] HTTP test passed but other tests failed" -ForegroundColor Yellow
                return $httpResult
            } else {
                return "ERROR"
            }
        }
    } catch {
        Write-Host "[ERROR] Unexpected Error in tests: $($_.Exception.Message)" -ForegroundColor Red
        return "ERROR"
    }
}

function Rotate-IP {
    # Pilih lokasi random
    $randomLocation = Get-Random -InputObject $locations
    Write-Host ""
    Write-Host "[INFO] Rotating IP... (New location: $randomLocation)" -ForegroundColor Yellow
    
    # Destroy addon yang ada
    Write-Host "[INFO] Destroying current IPBurger addon..." -ForegroundColor Yellow
    $destroyResult = heroku addons:destroy ipburger --app $AppName --confirm $AppName 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] Warning during destroy: $destroyResult" -ForegroundColor Yellow
    }
    
    # Tunggu destroy selesai
    Write-Host "[INFO] Waiting for destroy to complete..." -ForegroundColor Yellow
    Start-Sleep 8
    
    # Create addon baru dengan lokasi random
    Write-Host "[INFO] Creating new IPBurger addon in $randomLocation..." -ForegroundColor Yellow
    $createResult = heroku addons:create ipburger --app $AppName --location=$randomLocation 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Error creating addon: $createResult" -ForegroundColor Red
        Write-Host "[INFO] Waiting longer before retry..." -ForegroundColor Yellow
        Start-Sleep 15
        return $false
    }
    
    # Tunggu sampai credential tersedia
    Write-Host "[INFO] Waiting for new proxy credentials..." -ForegroundColor Yellow
    $maxWait = 30 # maksimal 30 detik
    $waitTime = 0
    
    do {
        Start-Sleep 2
        $waitTime += 2
        $cred = Get-Credential
        Write-Host "." -NoNewline -ForegroundColor Gray
        
        if ($waitTime -ge $maxWait) {
            Write-Host ""
            Write-Host "[ERROR] Timeout waiting for credentials" -ForegroundColor Red
            return $false
        }
    } while (-not $cred)
    
    Write-Host ""
    Write-Host "[SUCCESS] New proxy ready: $cred" -ForegroundColor Green
    return $true
}

function Write-Banner {
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host " GROWTOPIA PROXY TESTER v2.0" -ForegroundColor White
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "App: $AppName" -ForegroundColor Gray
    Write-Host "Target: https://growtopiagame.com/" -ForegroundColor Gray
    Write-Host "=================================" -ForegroundColor Cyan
}

function Check-Prerequisites {
    # Check if Heroku CLI is installed
    try {
        $herokuVersion = heroku --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Heroku CLI not found. Please install Heroku CLI first." -ForegroundColor Red
            return $false
        }
        
        Write-Host "[INFO] Heroku CLI found: $herokuVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[ERROR] Error checking Heroku CLI: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Banner

# Check prerequisites first
if (-not (Check-Prerequisites)) {
    Write-Host "[ERROR] Prerequisites not met. Please install required tools." -ForegroundColor Red
    exit 1
}

$attempt = 1
$maxAttempts = 10 # Batas maksimal attempt untuk menghindari infinite loop

while ($attempt -le $maxAttempts) {
    Write-Host ""
    Write-Host "[INFO] Attempt #$attempt" -ForegroundColor White
    
    # Get current proxy
    $proxy = Get-Credential
    
    if (-not $proxy) {
        Write-Host "[ERROR] No proxy credential found. Creating new addon..." -ForegroundColor Red
        if (-not (Rotate-IP)) {
            Write-Host "[ERROR] Failed to create new proxy. Exiting..." -ForegroundColor Red
            exit 1
        }
        continue
    }
    
    Write-Host "[INFO] Current proxy: $proxy" -ForegroundColor Cyan
    
    # Test proxy
    $code = Test-Growtopia $proxy
    Write-Host "[INFO] Test result: $code" -ForegroundColor Magenta
    
    if ($code -eq "200") {
        Write-Host ""
        Write-Host "[SUCCESS] SUCCESS! Proxy is working!" -ForegroundColor Green
        Write-Host "[SUCCESS] LIVE proxy: $proxy" -ForegroundColor Green
        
        # Extract proxy credentials and address from URL
        if ($proxy -match "socks5h?://([^:]+):([^@]+)@([^:]+):([0-9]+)") {
            $proxyUser = $Matches[1]
            $proxyPass = $Matches[2]
            $proxyHost = $Matches[3]
            $proxyPort = $Matches[4]
            
            # Format proxy dalam format ip:port:username:password untuk kebutuhan masa depan
            $formattedProxy = "${proxyHost}:${proxyPort}:${proxyUser}:${proxyPass}"
            
            # Save working proxy to file with timestamp
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $proxyEntry = "$timestamp - $formattedProxy"
            
            # Cek apakah file sudah ada dan tidak kosong
            if (Test-Path "working_proxies.txt" -PathType Leaf) {
                $existingContent = Get-Content -Path "working_proxies.txt" -Raw -ErrorAction SilentlyContinue
                if ($existingContent) {
                    # File ada dan tidak kosong, tambahkan baris baru
                    $newContent = $existingContent.TrimEnd() + "`r`n$proxyEntry"
                } else {
                    # File ada tapi kosong
                    $newContent = $proxyEntry
                }
            } else {
                # File tidak ada
                $newContent = $proxyEntry
            }
            
            # Tulis konten baru ke file
            Set-Content -Path "working_proxies.txt" -Value $newContent -Encoding utf8
        } else {
            # Fallback jika format tidak sesuai
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $proxyEntry = "$timestamp - $proxy"
            
            # Cek apakah file sudah ada dan tidak kosong
            if (Test-Path "working_proxies.txt" -PathType Leaf) {
                $existingContent = Get-Content -Path "working_proxies.txt" -Raw -ErrorAction SilentlyContinue
                if ($existingContent) {
                    # File ada dan tidak kosong, tambahkan baris baru
                    $newContent = $existingContent.TrimEnd() + "`r`n$proxyEntry"
                } else {
                    # File ada tapi kosong
                    $newContent = $proxyEntry
                }
            } else {
                # File tidak ada
                $newContent = $proxyEntry
            }
            
            # Tulis konten baru ke file
            Set-Content -Path "working_proxies.txt" -Value $newContent -Encoding utf8
        }
        
        Write-Host "[SUCCESS] Proxy saved to working_proxies.txt" -ForegroundColor Green
        Write-Host ""
        Write-Host "[SUCCESS] Ready to use for Growtopia!" -ForegroundColor Green
        break
        
    } elseif ($code -eq "403") {
        Write-Host "[ERROR] Proxy blocked by Growtopia (403 Forbidden)" -ForegroundColor Red
        
    } else {
        Write-Host "[ERROR] Proxy not working (Code: $code)" -ForegroundColor Red
    }
    
    # Rotate IP for next attempt
    if ($attempt -lt $maxAttempts) {
        if (-not (Rotate-IP)) {
            Write-Host "[ERROR] Failed to rotate IP. Waiting before retry..." -ForegroundColor Red
            Start-Sleep 10
        }
    }
    
    $attempt++
}

if ($attempt -gt $maxAttempts) {
    Write-Host ""
    Write-Host "[ERROR] Reached maximum attempts ($maxAttempts). No working proxy found." -ForegroundColor Red
    Write-Host "[WARNING] Consider trying again later or checking your Heroku setup." -ForegroundColor Yellow
    exit 1
}
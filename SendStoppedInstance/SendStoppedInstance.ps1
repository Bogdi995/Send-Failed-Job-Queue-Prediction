param (
    [string] $ServerInstanceName
)

function Get-LogFilePath {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)] [System.Object] $SettingsFile
    )

    process {
        $logFileName = "$(Get-Date -Format "yyyy-MM-dd")_logfile.log"
        $outputDir = $SettingsFile.paths.logFileOutputDir

        return Join-Path $outputDir $logFileName
    }
}

function Write-LogMessage() {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)] [string] $Message,
        [Parameter(Mandatory=$true)] [string] $LogFilePath
    )

    process {
        $timeStamp = Get-Date -Format "[dd/MM/yyyy HH:mm:ss:fff tt]"
        if(!(Test-Path "$LogFilePath")){
            New-Item -Type File -Path "$LogFilePath" -Force
        }
        
        Add-content -Path $logFilePath -Value "$timeStamp $Message `n" -Encoding UTF8
    }
}

function Get-NAVServerInstanceDetails {
    [CmdletBinding()]
    param (
        [Parameter(ValueFromPipeline=$true, ValueFromPipelineByPropertyName=$true)] $ServerInstance,
        [Parameter(Mandatory=$true)] [string] $LogFilePath
    )

    process {
        try {
            $ServerInstance | Get-NAVServerInstance | ForEach-Object {
                $serverConfig = New-Object PSObject
                
                foreach ($attribute in $_.Attributes) {
                   if ($attribute.Name -in "State", "ServiceAccount") {
                       $serverConfig | Add-Member -MemberType NoteProperty -Name $attribute.Name -Value $attribute.Value -Force
                   }
                }
                
                foreach ($node in ($_ | Get-NavServerConfiguration -AsXml).configuration.appSettings.add) {
                   if ($node.key -in "DatabaseServer", "DatabaseName", "ServerInstance") {
                       $serverConfig | Add-Member -MemberType NoteProperty -Name $node.key -Value $node.value -Force
                   }
                }
            }
        }
        catch {
            Write-LogMessage $_.Exception.Message -LogFilePath $LogFilePath
            throw $_
        }
                
        return $serverConfig
     }
}

function Get-EmailAdresses {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)] [System.Object] $SettingsFile,
        [Parameter(Mandatory=$true)] [string] $LogFilePath
    )

    process {
        try {
            $sqlConnection = New-Object System.Data.SqlClient.SqlConnection
            $sqlConnection.ConnectionString = $SettingsFile.connectionStrings.bcDatabase
            
            $sqlConnection.Open()

            $sqlCommand = New-Object System.Data.SqlClient.SqlCommand
            $sqlCommand.Connection = $sqlConnection
            
            $query = "SELECT [To], [Cc1], [Cc2], [Cc3] FROM [Job Queue Setup`$16750a2c-1c1e-4805-95ac-3f5bb3ba2872]";
            $sqlCommand.CommandText = $query;
            $dataAdapter = New-Object System.Data.SqlClient.SqlDataAdapter $sqlCommand
            $dataSet = New-Object System.Data.DataSet
            $dataAdapter.Fill($dataSet) | Out-Null
            $emailAddresses = $dataSet.Tables

            $sqlConnection.Close()

            return $emailAddresses
        }
        catch {
            Write-LogMessage $_.Exception.Message -LogFilePath $LogFilePath   
            return
        }
    }
}

function Get-CcList {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)] $EmailAdresses
    )

    process {
        $ccList = New-Object -TypeName "System.Collections.ArrayList"

        if($EmailAdresses[0].Cc1 -ne "") {
            [void]$ccList.Add($EmailAdresses[0].Cc1)
        }
           
        if($EmailAdresses[0].Cc2 -ne "") {
            [void]$ccList.Add($EmailAdresses[0].Cc2)
        } 
        
        if($EmailAdresses[0].Cc3 -ne "") {
            [void]$ccList.Add($EmailAdresses[0].Cc3)
        }

        return $ccList
    }
}

function Send-StoppedServerInstance() {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)] [string] $GivenServerInstance       
    )

    process {
        $scriptDirectory = $PSScriptRoot
        $settingsFilePath = Join-Path -Path $scriptDirectory -ChildPath "settings.json"
        if(Test-Path $settingsFilePath -PathType Leaf){
            $settingsFile = Get-Content $settingsFilePath | ConvertFrom-Json
        }

        Set-ExecutionPolicy unrestricted -Force
        Import-Module $SettingsFile.paths.navAdminTool

        $sendEmailAPI = $SettingsFile.urls.sendEmailAPI
        $logFilePath = Get-LogFilePath -SettingsFile $settingsFile 
        $serverInstanceDetails = Get-NAVServerInstanceDetails $GivenServerInstance -LogFilePath $logFilePath
        $emailAdresses = Get-EmailAdresses -SettingsFile $settingsFile -LogFilePath $logFilePath
        $ccList = Get-CcList $emailAdresses

        $headers = @{
            "Content-Type" = "application/json"
        }

        $body = @"
        {
            "To": "$($emailAdresses[0].To)",
            "Cc": $(ConvertTo-Json @($ccList)),
            "ServerInstance": "$($serverInstanceDetails.ServerInstance)",
            "State": "$($serverInstanceDetails.State)",
            "ServiceAccount": $($serverInstanceDetails.ServiceAccount | ConvertTo-Json),
            "DatabaseServer": "$($serverInstanceDetails.DatabaseServer)",
            "DatabaseName": "$($serverInstanceDetails.DatabaseName)"
        }
"@

        try {
            $sendStoppedInstance = Invoke-WebRequest -Method 'Post' -Uri $sendEmailAPI -Body ($body) -Headers $headers -UseBasicParsing
        }
        catch {
            Write-LogMessage $_.Exception.Message -LogFilePath $logFilePath   
            return
        }

        if($sendStoppedInstance.StatusCode -ne 200){
            Write-LogMessage $sendStoppedInstance.Content.ToString() -LogFilePath $logFilePath
        }
    }
}

Send-StoppedServerInstance "BC230"
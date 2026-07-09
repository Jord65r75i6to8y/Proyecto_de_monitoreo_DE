# Script generado por chatGPT con el objetivo de limitar 
# la ram de un proceso y sus hijos en windows
# Me cago en windows, obvio que no iba a tener
# algo semejante a cgroups

param(
    [int]$MemoryLimitMB = 3600,

    [string]$SteamPath = "C:\Program Files (x86)\Steam\steam.exe"
)

Add-Type @"
using System;
using System.Runtime.InteropServices;



public class JobObject
{
    [StructLayout(LayoutKind.Sequential)]
    public struct JOBOBJECT_BASIC_LIMIT_INFORMATION
    {
        public long PerProcessUserTimeLimit;
        public long PerJobUserTimeLimit;
        public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize;
        public UIntPtr MaximumWorkingSetSize;
        public uint ActiveProcessLimit;
        public long Affinity;
        public uint PriorityClass;
        public uint SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct IO_COUNTERS
    {
        public ulong ReadOperationCount;
        public ulong WriteOperationCount;
        public ulong OtherOperationCount;
        public ulong ReadTransferCount;
        public ulong WriteTransferCount;
        public ulong OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    {
        public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
        public IO_COUNTERS IoInfo;
        public UIntPtr ProcessMemoryLimit;
        public UIntPtr JobMemoryLimit;
        public UIntPtr PeakProcessMemoryUsed;
        public UIntPtr PeakJobMemoryUsed;
    }

    public enum JOBOBJECTINFOCLASS
    {
        ExtendedLimitInformation = 9
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr CreateJobObject(
        IntPtr lpJobAttributes,
        string lpName
    );

    [DllImport("kernel32.dll")]
    public static extern bool SetInformationJobObject(
        IntPtr hJob,
        JOBOBJECTINFOCLASS infoClass,
        IntPtr lpJobObjectInfo,
        uint cbJobObjectInfoLength
    );

    [DllImport("kernel32.dll")]
    public static extern bool AssignProcessToJobObject(
        IntPtr hJob,
        IntPtr hProcess
    );
}
"@




# ==========================
# Crear Job
# ==========================

$job = [JobObject]::CreateJobObject(
    [IntPtr]::Zero,
    "SteamMemoryLimit"
)

$info = New-Object JobObject+JOBOBJECT_EXTENDED_LIMIT_INFORMATION

# Flag para límite de memoria del Job
$JOB_OBJECT_LIMIT_JOB_MEMORY = 0x2000

$info.BasicLimitInformation.LimitFlags =
    $JOB_OBJECT_LIMIT_JOB_MEMORY

[UInt64]$bytes = [UInt64]$MemoryLimitMB * 1024 * 1024

$info.JobMemoryLimit =
    [UIntPtr]$bytes


$size = [Runtime.InteropServices.Marshal]::SizeOf($info)

$ptr = [Runtime.InteropServices.Marshal]::AllocHGlobal($size)

[Runtime.InteropServices.Marshal]::StructureToPtr(
    $info,
    $ptr,
    $false
)


[JobObject]::SetInformationJobObject(
    $job,
    [JobObject+JOBOBJECTINFOCLASS]::ExtendedLimitInformation,
    $ptr,
    $size
)


# ==========================
# Lanzar Steam
# ==========================

$process = Start-Process `
    -FilePath $SteamPath `
    -PassThru


Write-Host "Steam iniciado PID:" $process.Id
Write-Host "Asignando Job Object..."


$result = [JobObject]::AssignProcessToJobObject(
    $job,
    $process.Handle
)


if ($result)
{
    Write-Host "Limite aplicado correctamente:"
    Write-Host "$MemoryLimitMB MB para Steam y procesos hijos"
}
else
{
    Write-Host "Error asignando proceso al Job"
}
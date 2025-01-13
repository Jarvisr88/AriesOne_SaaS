namespace DMEWorks.Database
{
    using System;
    using System.Diagnostics;
    using System.IO;

    public static class Odbcad32
    {
        public static void Start()
        {
            string str = !Environment.Is64BitOperatingSystem ? Environment.GetFolderPath(Environment.SpecialFolder.System) : Environment.GetFolderPath(Environment.SpecialFolder.SystemX86);
            string path = Path.Combine(str, "odbcad32.exe");
            if (!File.Exists(path))
            {
                throw new FileNotFoundException("", path);
            }
            ProcessStartInfo startInfo = new ProcessStartInfo(path);
            startInfo.UseShellExecute = true;
            Process.Start(startInfo);
        }
    }
}


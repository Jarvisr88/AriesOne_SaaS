namespace DMEWorks.Reports
{
    using DMEWorks.Core;
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Xml;
    using System.Xml.Serialization;

    public class DataSourceReports
    {
        private readonly string _customFileName;
        private readonly string _defaultFileName;
        private Dictionary<string, Pair> _dictionary;
        private Report[] _reports;

        public DataSourceReports(string customFileName, string defaultFileName)
        {
            this._customFileName = customFileName;
            this._defaultFileName = defaultFileName;
        }

        public void DeleteByFilename(params string[] filenames)
        {
            int num = 0;
            Dictionary<string, Pair> dictionary = this.Dictionary;
            foreach (string str in filenames)
            {
                Pair pair;
                if (dictionary.TryGetValue(str, out pair))
                {
                    if (pair.DefaultReport == null)
                    {
                        if (pair.CustomReport != null)
                        {
                            dictionary.Remove(str);
                            num++;
                        }
                    }
                    else if ((pair.CustomReport == null) || pair.CustomReport.IsDeleted)
                    {
                        CustomReport customReport = new CustomReport();
                        customReport.FileName = pair.DefaultReport.FileName;
                        customReport.IsDeleted = true;
                        dictionary[str] = new Pair(customReport, pair.DefaultReport);
                        num++;
                    }
                }
            }
            if (0 < num)
            {
                this.SaveCustomReports();
                this._reports = null;
            }
        }

        private static T[] LoadArray<T>(string filename)
        {
            try
            {
                using (TextReader reader = new StreamReader(filename, Encoding.UTF8))
                {
                    T[] localArray = new XmlSerializer(typeof(T[])).Deserialize(reader) as T[];
                    if (localArray != null)
                    {
                        return localArray;
                    }
                }
            }
            catch
            {
            }
            return new T[0];
        }

        public void ReplaceWith(params Report[] reports)
        {
            Report report;
            Pair pair;
            int num = 0;
            Dictionary<string, Pair> dictionary = this.Dictionary;
            Report[] reportArray = reports;
            int index = 0;
            goto TR_000F;
        TR_0003:
            index++;
            goto TR_000F;
        TR_0004:
            dictionary[report.FileName] = pair;
            num++;
            goto TR_0003;
        TR_000F:
            while (true)
            {
                if (index >= reportArray.Length)
                {
                    if (0 < num)
                    {
                        this.SaveCustomReports();
                        this._reports = null;
                    }
                    return;
                }
                report = reportArray[index];
                if (!dictionary.TryGetValue(report.FileName, out pair))
                {
                    pair = new Pair(report.CreateCustomReport(), null);
                    goto TR_0004;
                }
                else if (pair.CustomReport != null)
                {
                    if (pair.CustomReport.IsDeleted || !report.Equals(pair.CustomReport))
                    {
                        break;
                    }
                }
                else if ((pair.DefaultReport == null) || !report.Equals(pair.DefaultReport))
                {
                    break;
                }
                goto TR_0003;
            }
            if (report.Equals(pair.DefaultReport))
            {
                pair = new Pair(null, pair.DefaultReport);
            }
            else
            {
                pair = new Pair(report.CreateCustomReport(), pair.DefaultReport);
            }
            goto TR_0004;
        }

        private static void SaveArray<T>(string filename, T[] array)
        {
            XmlWriterSettings settings1 = new XmlWriterSettings();
            settings1.OmitXmlDeclaration = true;
            settings1.Indent = true;
            settings1.CloseOutput = true;
            settings1.Encoding = Encoding.UTF8;
            XmlWriterSettings settings = settings1;
            using (XmlWriter writer = XmlWriter.Create(filename, settings))
            {
                new XmlSerializer(typeof(T[])).Serialize(writer, array);
            }
        }

        private void SaveCustomReports()
        {
            Func<KeyValuePair<string, Pair>, CustomReport> selector = <>c.<>9__15_0;
            if (<>c.<>9__15_0 == null)
            {
                Func<KeyValuePair<string, Pair>, CustomReport> local1 = <>c.<>9__15_0;
                selector = <>c.<>9__15_0 = p => p.Value.CustomReport;
            }
            Func<CustomReport, bool> predicate = <>c.<>9__15_1;
            if (<>c.<>9__15_1 == null)
            {
                Func<CustomReport, bool> local2 = <>c.<>9__15_1;
                predicate = <>c.<>9__15_1 = r => r != null;
            }
            Func<CustomReport, string> keySelector = <>c.<>9__15_2;
            if (<>c.<>9__15_2 == null)
            {
                Func<CustomReport, string> local3 = <>c.<>9__15_2;
                keySelector = <>c.<>9__15_2 = r => r.FileName;
            }
            CustomReport[] array = this.Dictionary.Select<KeyValuePair<string, Pair>, CustomReport>(selector).Where<CustomReport>(predicate).OrderBy<CustomReport, string>(keySelector, SqlStringComparer.Default).ToArray<CustomReport>();
            SaveArray<CustomReport>(this._customFileName, array);
        }

        public IEnumerable<Report> Select()
        {
            if (this._reports == null)
            {
                Func<KeyValuePair<string, Pair>, Report> selector = <>c.<>9__14_0;
                if (<>c.<>9__14_0 == null)
                {
                    Func<KeyValuePair<string, Pair>, Report> local1 = <>c.<>9__14_0;
                    selector = <>c.<>9__14_0 = p => p.Value.CreateReport();
                }
                Func<Report, bool> predicate = <>c.<>9__14_1;
                if (<>c.<>9__14_1 == null)
                {
                    Func<Report, bool> local2 = <>c.<>9__14_1;
                    predicate = <>c.<>9__14_1 = r => r != null;
                }
                this._reports = this.Dictionary.Select<KeyValuePair<string, Pair>, Report>(selector).Where<Report>(predicate).ToArray<Report>();
            }
            return this._reports;
        }

        public string CustomFileName =>
            this._customFileName;

        public string DefaultFileName =>
            this._defaultFileName;

        private Dictionary<string, Pair> Dictionary
        {
            get
            {
                if (this._dictionary == null)
                {
                    Dictionary<string, Pair> dictionary = new Dictionary<string, Pair>(SqlStringComparer.Default);
                    DefaultReport[] reportArray = LoadArray<DefaultReport>(this._defaultFileName);
                    int index = 0;
                    while (true)
                    {
                        if (index >= reportArray.Length)
                        {
                            CustomReport[] reportArray2 = LoadArray<CustomReport>(this._customFileName);
                            index = 0;
                            while (true)
                            {
                                Pair pair;
                                if (index >= reportArray2.Length)
                                {
                                    this._dictionary = dictionary;
                                    break;
                                }
                                CustomReport customReport = reportArray2[index];
                                if (dictionary.TryGetValue(customReport.FileName, out pair))
                                {
                                    pair = new Pair(customReport, pair.DefaultReport);
                                }
                                else
                                {
                                    pair = new Pair(customReport, null);
                                }
                                dictionary[customReport.FileName] = pair;
                                index++;
                            }
                            break;
                        }
                        DefaultReport defaultReport = reportArray[index];
                        dictionary[defaultReport.FileName] = new Pair(null, defaultReport);
                        index++;
                    }
                }
                return this._dictionary;
            }
        }

        [Serializable, CompilerGenerated]
        private sealed class <>c
        {
            public static readonly DataSourceReports.<>c <>9 = new DataSourceReports.<>c();
            public static Func<KeyValuePair<string, DataSourceReports.Pair>, Report> <>9__14_0;
            public static Func<Report, bool> <>9__14_1;
            public static Func<KeyValuePair<string, DataSourceReports.Pair>, CustomReport> <>9__15_0;
            public static Func<CustomReport, bool> <>9__15_1;
            public static Func<CustomReport, string> <>9__15_2;

            internal CustomReport <SaveCustomReports>b__15_0(KeyValuePair<string, DataSourceReports.Pair> p) => 
                p.Value.CustomReport;

            internal bool <SaveCustomReports>b__15_1(CustomReport r) => 
                r != null;

            internal string <SaveCustomReports>b__15_2(CustomReport r) => 
                r.FileName;

            internal Report <Select>b__14_0(KeyValuePair<string, DataSourceReports.Pair> p) => 
                p.Value.CreateReport();

            internal bool <Select>b__14_1(Report r) => 
                r != null;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct Pair
        {
            public readonly DMEWorks.Reports.CustomReport CustomReport;
            public readonly DMEWorks.Reports.DefaultReport DefaultReport;
            public Pair(DMEWorks.Reports.CustomReport customReport, DMEWorks.Reports.DefaultReport defaultReport)
            {
                this.CustomReport = customReport;
                this.DefaultReport = defaultReport;
            }

            public Report CreateReport()
            {
                if (this.CustomReport == null)
                {
                    if (this.DefaultReport == null)
                    {
                        return null;
                    }
                    Report report2 = new Report();
                    report2.Category = this.DefaultReport.Category;
                    report2.FileName = this.DefaultReport.FileName;
                    report2.IsSystem = this.DefaultReport.IsSystem;
                    report2.Name = this.DefaultReport.Name;
                    return report2;
                }
                if (this.CustomReport.IsDeleted)
                {
                    return null;
                }
                Report report1 = new Report();
                report1.Category = this.CustomReport.Category;
                report1.FileName = this.CustomReport.FileName;
                report1.IsSystem = (this.DefaultReport != null) && this.DefaultReport.IsSystem;
                Report local1 = report1;
                local1.Name = this.CustomReport.Name;
                return local1;
            }
        }
    }
}


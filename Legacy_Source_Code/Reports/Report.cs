namespace DMEWorks.Reports
{
    using DMEWorks.Core;
    using System;
    using System.Runtime.CompilerServices;

    public class Report
    {
        internal CustomReport CreateCustomReport()
        {
            CustomReport report1 = new CustomReport();
            report1.Category = this.Category;
            report1.FileName = this.FileName;
            report1.IsDeleted = false;
            report1.Name = this.Name;
            return report1;
        }

        public bool Equals(CustomReport other) => 
            (other != null) && (SqlString.Equals(this.Category, other.Category) && (SqlString.Equals(this.FileName, other.FileName) && SqlString.Equals(this.Name, other.Name)));

        public bool Equals(DefaultReport other) => 
            (other != null) && (SqlString.Equals(this.Category, other.Category) && (SqlString.Equals(this.FileName, other.FileName) && SqlString.Equals(this.Name, other.Name)));

        public string FileName { get; set; }

        public bool IsSystem { get; set; }

        public string Name { get; set; }

        public string Category { get; set; }
    }
}


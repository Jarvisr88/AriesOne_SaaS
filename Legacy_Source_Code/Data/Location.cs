namespace DMEWorks.Data
{
    using System;
    using System.Runtime.CompilerServices;

    public class Location
    {
        public int ID { get; set; }

        public string Name { get; set; }

        public int? WarehouseID { get; set; }

        public int? POSTypeID { get; set; }

        public int? TaxRateID { get; set; }
    }
}


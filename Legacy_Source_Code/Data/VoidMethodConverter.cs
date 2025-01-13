namespace DMEWorks.Data
{
    using System;
    using System.Runtime.InteropServices;

    internal class VoidMethodConverter : Converter<VoidMethod>
    {
        public const string Replacement = "Replacement";
        public const string Void = "Void";

        public override string ToString(VoidMethod value) => 
            (value == VoidMethod.Replacement) ? "Replacement" : ((value == VoidMethod.Void) ? "Void" : "");

        public override bool TryParse(string value, out VoidMethod result)
        {
            if ("Replacement".Equals(value, StringComparison.OrdinalIgnoreCase))
            {
                result = VoidMethod.Replacement;
            }
            else
            {
                if (!"Void".Equals(value, StringComparison.OrdinalIgnoreCase))
                {
                    result = VoidMethod.Replacement;
                    return false;
                }
                result = VoidMethod.Void;
            }
            return true;
        }
    }
}


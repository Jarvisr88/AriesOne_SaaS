namespace DMEWorks.Properties
{
    using System;
    using System.CodeDom.Compiler;
    using System.ComponentModel;
    using System.Diagnostics;
    using System.Drawing;
    using System.Globalization;
    using System.Resources;
    using System.Runtime.CompilerServices;

    [GeneratedCode("System.Resources.Tools.StronglyTypedResourceBuilder", "16.0.0.0"), DebuggerNonUserCode, CompilerGenerated]
    internal class Resources
    {
        private static System.Resources.ResourceManager resourceMan;
        private static CultureInfo resourceCulture;

        internal Resources()
        {
        }

        [EditorBrowsable(EditorBrowsableState.Advanced)]
        internal static System.Resources.ResourceManager ResourceManager
        {
            get
            {
                resourceMan ??= new System.Resources.ResourceManager("DMEWorks.Properties.Resources", typeof(Resources).Assembly);
                return resourceMan;
            }
        }

        [EditorBrowsable(EditorBrowsableState.Advanced)]
        internal static CultureInfo Culture
        {
            get => 
                resourceCulture;
            set => 
                resourceCulture = value;
        }

        internal static Bitmap Checked =>
            (Bitmap) ResourceManager.GetObject("Checked", resourceCulture);

        internal static Bitmap Indeterminate =>
            (Bitmap) ResourceManager.GetObject("Indeterminate", resourceCulture);

        internal static Bitmap Reload =>
            (Bitmap) ResourceManager.GetObject("Reload", resourceCulture);

        internal static Bitmap Reload2 =>
            (Bitmap) ResourceManager.GetObject("Reload2", resourceCulture);

        internal static Bitmap Unchecked =>
            (Bitmap) ResourceManager.GetObject("Unchecked", resourceCulture);
    }
}


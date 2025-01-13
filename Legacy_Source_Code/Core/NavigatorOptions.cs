namespace DMEWorks.Core
{
    using System;
    using System.Runtime.CompilerServices;

    public sealed class NavigatorOptions : NavigatorOptionsBase
    {
        public EventHandler<FillSourceEventArgs> FillSource { get; set; }
    }
}


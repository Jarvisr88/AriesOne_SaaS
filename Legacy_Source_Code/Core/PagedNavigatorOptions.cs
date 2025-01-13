namespace DMEWorks.Core
{
    using System;
    using System.Runtime.CompilerServices;

    public sealed class PagedNavigatorOptions : NavigatorOptionsBase
    {
        public EventHandler<PagedFillSourceEventArgs> FillSource { get; set; }
    }
}


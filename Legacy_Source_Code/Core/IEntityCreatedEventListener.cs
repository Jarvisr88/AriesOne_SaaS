namespace DMEWorks.Core
{
    using System;
    using System.Runtime.CompilerServices;

    public interface IEntityCreatedEventListener
    {
        event EventHandler Unhook;

        void Handle(object sender, EntityCreatedEventArgs args);
    }
}


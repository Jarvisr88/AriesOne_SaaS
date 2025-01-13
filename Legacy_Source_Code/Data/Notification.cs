namespace DMEWorks.Data
{
    using System;
    using System.Runtime.CompilerServices;

    public class Notification
    {
        public Notification(int id, string type, string args, DateTime time)
        {
            this.<Id>k__BackingField = id;
            this.<Type>k__BackingField = type;
            this.<Args>k__BackingField = args;
            this.<Time>k__BackingField = time;
        }

        public int Id { get; }

        public string Type { get; }

        public string Args { get; }

        public DateTime Time { get; }
    }
}


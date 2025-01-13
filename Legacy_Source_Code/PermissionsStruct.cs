namespace DMEWorks
{
    using System;
    using System.Runtime.InteropServices;

    [StructLayout(LayoutKind.Sequential)]
    public struct PermissionsStruct
    {
        public readonly bool Allow_ADD_EDIT;
        public readonly bool Allow_DELETE;
        public readonly bool Allow_VIEW;
        public readonly bool Allow_PROCESS;
        public static readonly PermissionsStruct Empty;
        public static readonly PermissionsStruct All;
        public PermissionsStruct(bool ADD_EDIT, bool DELETE, bool VIEW, bool PROCESS)
        {
            this.Allow_ADD_EDIT = ADD_EDIT;
            this.Allow_DELETE = DELETE;
            this.Allow_VIEW = VIEW;
            this.Allow_PROCESS = PROCESS;
        }

        static PermissionsStruct()
        {
            Empty = new PermissionsStruct(false, false, false, false);
            All = new PermissionsStruct(true, true, true, true);
        }
    }
}


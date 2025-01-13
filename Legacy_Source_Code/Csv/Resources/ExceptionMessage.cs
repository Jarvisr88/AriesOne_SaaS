namespace DMEWorks.Csv.Resources
{
    using System;
    using System.CodeDom.Compiler;
    using System.ComponentModel;
    using System.Diagnostics;
    using System.Globalization;
    using System.Resources;
    using System.Runtime.CompilerServices;

    [GeneratedCode("System.Resources.Tools.StronglyTypedResourceBuilder", "16.0.0.0"), DebuggerNonUserCode, CompilerGenerated]
    internal class ExceptionMessage
    {
        private static System.Resources.ResourceManager resourceMan;
        private static CultureInfo resourceCulture;

        internal ExceptionMessage()
        {
        }

        [EditorBrowsable(EditorBrowsableState.Advanced)]
        internal static System.Resources.ResourceManager ResourceManager
        {
            get
            {
                resourceMan ??= new System.Resources.ResourceManager("DMEWorks.Csv.Resources.ExceptionMessage", typeof(ExceptionMessage).Assembly);
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

        internal static string BufferSizeTooSmall =>
            ResourceManager.GetString("BufferSizeTooSmall", resourceCulture);

        internal static string CannotMovePreviousRecordInForwardOnly =>
            ResourceManager.GetString("CannotMovePreviousRecordInForwardOnly", resourceCulture);

        internal static string CannotReadRecordAtIndex =>
            ResourceManager.GetString("CannotReadRecordAtIndex", resourceCulture);

        internal static string EnumerationFinishedOrNotStarted =>
            ResourceManager.GetString("EnumerationFinishedOrNotStarted", resourceCulture);

        internal static string EnumerationVersionCheckFailed =>
            ResourceManager.GetString("EnumerationVersionCheckFailed", resourceCulture);

        internal static string FieldHeaderNotFound =>
            ResourceManager.GetString("FieldHeaderNotFound", resourceCulture);

        internal static string FieldIndexOutOfRange =>
            ResourceManager.GetString("FieldIndexOutOfRange", resourceCulture);

        internal static string MalformedCsvException =>
            ResourceManager.GetString("MalformedCsvException", resourceCulture);

        internal static string MissingFieldActionNotSupported =>
            ResourceManager.GetString("MissingFieldActionNotSupported", resourceCulture);

        internal static string NoCurrentRecord =>
            ResourceManager.GetString("NoCurrentRecord", resourceCulture);

        internal static string NoHeaders =>
            ResourceManager.GetString("NoHeaders", resourceCulture);

        internal static string NotEnoughSpaceInArray =>
            ResourceManager.GetString("NotEnoughSpaceInArray", resourceCulture);

        internal static string ParseErrorActionInvalidInsideParseErrorEvent =>
            ResourceManager.GetString("ParseErrorActionInvalidInsideParseErrorEvent", resourceCulture);

        internal static string ParseErrorActionNotSupported =>
            ResourceManager.GetString("ParseErrorActionNotSupported", resourceCulture);

        internal static string ReaderClosed =>
            ResourceManager.GetString("ReaderClosed", resourceCulture);

        internal static string RecordIndexLessThanZero =>
            ResourceManager.GetString("RecordIndexLessThanZero", resourceCulture);
    }
}


namespace SODA.Utilities
{
    using System;
    using System.IO;
    using System.Net;
    using System.Runtime.CompilerServices;

    internal static class WebExceptionExtensions
    {
        internal static string UnwrapExceptionMessage(this WebException webException)
        {
            string message = string.Empty;
            if (webException != null)
            {
                message = webException.Message;
                if (webException.Response != null)
                {
                    using (StreamReader reader = new StreamReader(webException.Response.GetResponseStream()))
                    {
                        message = reader.ReadToEnd();
                    }
                }
            }
            return message;
        }
    }
}


namespace Images.Service
{
    using System;

    public sealed class TemplateException : Exception
    {
        public TemplateException()
        {
        }

        public TemplateException(string message) : base(message)
        {
        }

        public TemplateException(string message, Exception innerException) : base(message, innerException)
        {
        }

        public static string GetMessage(Exception ex) => 
            !(ex is TemplateException) ? ex.ToString() : ((ex.InnerException != null) ? ex.InnerException.ToString() : ex.Message);
    }
}


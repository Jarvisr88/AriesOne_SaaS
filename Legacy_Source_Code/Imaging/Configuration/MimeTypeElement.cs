namespace DMEWorks.Imaging.Configuration
{
    using System;
    using System.Configuration;

    public sealed class MimeTypeElement : ConfigurationElement
    {
        private static ConfigurationPropertyCollection _properties = new ConfigurationPropertyCollection();
        private static readonly ConfigurationProperty _propMimetype = new ConfigurationProperty("mimetype", typeof(string), "", ConfigurationPropertyOptions.IsKey | ConfigurationPropertyOptions.IsRequired);
        private static readonly ConfigurationProperty _propDescription = new ConfigurationProperty("description", typeof(string), "", ConfigurationPropertyOptions.None);

        static MimeTypeElement()
        {
            _properties.Add(_propMimetype);
            _properties.Add(_propDescription);
        }

        public string Mimetype =>
            (string) base[_propMimetype];

        public string Description =>
            (string) base[_propDescription];

        protected override ConfigurationPropertyCollection Properties =>
            _properties;
    }
}


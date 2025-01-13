namespace DMEWorks.Imaging.Configuration
{
    using System;
    using System.Configuration;

    public sealed class MimeTypesSection : ConfigurationSection
    {
        private static readonly ConfigurationProperty _propMimetypes = new ConfigurationProperty(null, typeof(MimeTypeElementCollection), null, ConfigurationPropertyOptions.IsDefaultCollection);
        private static ConfigurationPropertyCollection _properties = new ConfigurationPropertyCollection();

        static MimeTypesSection()
        {
            _properties.Add(_propMimetypes);
        }

        protected override object GetRuntimeObject()
        {
            this.SetReadOnly();
            return this;
        }

        public MimeTypeElementCollection Mimetypes =>
            (MimeTypeElementCollection) base[_propMimetypes];

        protected override ConfigurationPropertyCollection Properties =>
            _properties;
    }
}


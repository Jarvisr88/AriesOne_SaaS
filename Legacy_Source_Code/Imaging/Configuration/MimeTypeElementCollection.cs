namespace DMEWorks.Imaging.Configuration
{
    using System;
    using System.Configuration;
    using System.Reflection;

    [ConfigurationCollection(typeof(MimeTypeElement))]
    public sealed class MimeTypeElementCollection : ConfigurationElementCollection
    {
        private static ConfigurationPropertyCollection _properties = new ConfigurationPropertyCollection();

        public MimeTypeElementCollection() : base(StringComparer.OrdinalIgnoreCase)
        {
        }

        protected override void BaseAdd(int index, ConfigurationElement element)
        {
            if (index == -1)
            {
                base.BaseAdd(element, false);
            }
            else
            {
                base.BaseAdd(index, element);
            }
        }

        protected override ConfigurationElement CreateNewElement() => 
            new MimeTypeElement();

        protected override object GetElementKey(ConfigurationElement element) => 
            ((MimeTypeElement) element).Mimetype;

        public string GetMimeTypeDescription(string mimetype)
        {
            if (string.IsNullOrEmpty(mimetype))
            {
                return "";
            }
            MimeTypeElement element = this[mimetype];
            return ((element != null) ? element.Description : "");
        }

        protected override string ElementName =>
            "mimetype";

        public override ConfigurationElementCollectionType CollectionType =>
            ConfigurationElementCollectionType.BasicMap;

        protected override bool ThrowOnDuplicate =>
            false;

        public MimeTypeElement this[string name] =>
            (MimeTypeElement) base.BaseGet(name);

        public MimeTypeElement this[int index] =>
            (MimeTypeElement) base.BaseGet(index);

        protected override ConfigurationPropertyCollection Properties =>
            _properties;
    }
}


namespace SODA.Models
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.Serialization;

    [DataContract]
    public class WebsiteUrlColumn
    {
        private string url;

        public WebsiteUrlColumn()
        {
        }

        public WebsiteUrlColumn(string url, string description)
        {
            this.Url = url;
            this.Description = description;
        }

        public WebsiteUrlColumn(Uri uri, string description) : this(uri.ToString(), description)
        {
        }

        [DataMember(Name="description")]
        public string Description { get; set; }

        [DataMember(Name="url")]
        public string Url
        {
            get => 
                this.url;
            set => 
                this.url = string.IsNullOrEmpty(value) ? string.Empty : Uri.EscapeUriString(value);
        }
    }
}


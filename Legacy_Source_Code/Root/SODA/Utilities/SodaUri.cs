namespace SODA.Utilities
{
    using SODA;
    using System;
    using System.Runtime.InteropServices;
    using System.Text.RegularExpressions;

    public class SodaUri
    {
        private static readonly Regex httpPrefix = new Regex(@"^http:\/\/(.+)", RegexOptions.Compiled | RegexOptions.IgnoreCase);
        private static readonly Regex httpsPrefix = new Regex(@"^https:\/\/", RegexOptions.Compiled | RegexOptions.IgnoreCase);

        internal static string enforceHttps(string socrataHost)
        {
            if (httpPrefix.IsMatch(socrataHost))
            {
                socrataHost = httpPrefix.Match(socrataHost).Groups[1].Value;
            }
            if (!httpsPrefix.IsMatch(socrataHost))
            {
                socrataHost = $"https://{socrataHost}";
            }
            return socrataHost;
        }

        public static Uri ForCategoryPage(string socrataHost, string category)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (string.IsNullOrEmpty(category))
            {
                throw new ArgumentException("category", "Must provide a category name.");
            }
            return new Uri($"{metadataUrl(socrataHost, null).Replace("views", "categories")}/{Uri.EscapeDataString(category)}");
        }

        public static Uri ForMetadata(string socrataHost, string resourceId)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            return new Uri(metadataUrl(socrataHost, resourceId));
        }

        public static Uri ForMetadataList(string socrataHost, int page)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (page <= 0)
            {
                throw new ArgumentOutOfRangeException("page", "Resouce metadata catalogs begin on page 1.");
            }
            return new Uri($"{metadataUrl(socrataHost, null)}?page={page}");
        }

        public static Uri ForQuery(string socrataHost, string resourceId, SoqlQuery soqlQuery)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if (soqlQuery == null)
            {
                throw new ArgumentNullException("soqlQuery", "Must provide a valid SoqlQuery object");
            }
            string str = metadataUrl(socrataHost, resourceId).Replace("views", "resource");
            return new Uri(Uri.EscapeUriString($"{str}?{soqlQuery.ToString()}"));
        }

        public static Uri ForResourceAboutPage(string socrataHost, string resourceId)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            return new Uri(metadataUrl(socrataHost, resourceId).Replace("views", "-/-") + "/about");
        }

        public static Uri ForResourceAPI(string socrataHost, string resourceId, string rowId = null)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            string str = metadataUrl(socrataHost, resourceId).Replace("views", "resource");
            if (!string.IsNullOrEmpty(rowId))
            {
                str = $"{str}/{rowId}";
            }
            return new Uri(str);
        }

        public static Uri ForResourceAPIPage(string socrataHost, string resourceId)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            string str = httpsPrefix.Replace(httpPrefix.Replace(socrataHost, ""), "");
            return new Uri($"http://dev.socrata.com/foundry/#/{str}/{resourceId}");
        }

        public static Uri ForResourcePage(string socrataHost, string resourceId)
        {
            if (string.IsNullOrEmpty(socrataHost))
            {
                throw new ArgumentException("socrataHost", "Must provide a Socrata host to target.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            return new Uri(metadataUrl(socrataHost, resourceId).Replace("views", "-/-"));
        }

        private static string metadataUrl(string socrataHost, string resourceId = null)
        {
            string str = enforceHttps(socrataHost);
            string str2 = $"{str}/views";
            if (!string.IsNullOrEmpty(resourceId))
            {
                str2 = $"{str2}/{resourceId}";
            }
            return str2;
        }
    }
}


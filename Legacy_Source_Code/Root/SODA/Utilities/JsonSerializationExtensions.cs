namespace SODA.Utilities
{
    using Newtonsoft.Json;
    using System;
    using System.Runtime.CompilerServices;

    public static class JsonSerializationExtensions
    {
        public static string ToJsonString(this object target) => 
            (target == null) ? null : JsonConvert.SerializeObject(target);
    }
}


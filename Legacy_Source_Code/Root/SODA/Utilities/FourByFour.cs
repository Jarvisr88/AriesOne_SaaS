namespace SODA.Utilities
{
    using System;
    using System.Text.RegularExpressions;

    public class FourByFour
    {
        private static Regex fourByFourRegex = new Regex("^[a-z0-9]{4}-[a-z0-9]{4}$", RegexOptions.Compiled | RegexOptions.IgnoreCase);

        public static bool IsNotValid(string testFourByFour) => 
            !IsValid(testFourByFour);

        public static bool IsValid(string testFourByFour) => 
            !string.IsNullOrEmpty(testFourByFour) && fourByFourRegex.IsMatch(testFourByFour);
    }
}


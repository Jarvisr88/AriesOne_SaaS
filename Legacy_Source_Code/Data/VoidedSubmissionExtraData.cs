namespace DMEWorks.Data
{
    using DMEWorks.Data.Serialization;
    using System;
    using System.ComponentModel;

    public class VoidedSubmissionExtraData
    {
        private DMEWorks.Data.VoidMethod? _VoidMethod;
        private string _ClaimNumber;

        public VoidedSubmissionExtraData()
        {
        }

        private VoidedSubmissionExtraData(Pairs pairs)
        {
            if (pairs != null)
            {
                foreach (Pair pair in pairs.Elements)
                {
                    Keyword keyword;
                    try
                    {
                        keyword = (Keyword) Enum.Parse(typeof(Keyword), pair.Name, true);
                    }
                    catch
                    {
                        continue;
                    }
                    if (keyword == Keyword.VoidMethod)
                    {
                        pair.Value.PutInto<DMEWorks.Data.VoidMethod>(ref this._VoidMethod);
                    }
                    else if (keyword == Keyword.ClaimNumber)
                    {
                        pair.Value.PutInto(ref this._ClaimNumber);
                    }
                }
            }
        }

        public static VoidedSubmissionExtraData Parse(string value)
        {
            Pairs pairs = null;
            try
            {
                pairs = Pairs.XmlDeserialize(value);
            }
            catch
            {
            }
            return new VoidedSubmissionExtraData(pairs);
        }

        public override string ToString()
        {
            Pairs pairs = new Pairs();
            pairs.Append<DMEWorks.Data.VoidMethod>(Keyword.VoidMethod, this._VoidMethod);
            pairs.Append(Keyword.ClaimNumber, this._ClaimNumber);
            return Pairs.XmlSerialize(pairs);
        }

        [Category("General")]
        public DMEWorks.Data.VoidMethod? VoidMethod
        {
            get => 
                this._VoidMethod;
            set => 
                this._VoidMethod = value;
        }

        [Category("General")]
        public string ClaimNumber
        {
            get => 
                this._ClaimNumber;
            set => 
                this._ClaimNumber = value;
        }

        private enum Keyword
        {
            VoidMethod,
            ClaimNumber
        }
    }
}


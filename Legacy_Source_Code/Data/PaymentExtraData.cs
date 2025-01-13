namespace DMEWorks.Data
{
    using DMEWorks.Data.Serialization;
    using System;
    using System.ComponentModel;

    public class PaymentExtraData
    {
        private decimal? _Allowable;
        private decimal? _AmountLeft;
        private decimal? _Billable;
        private DateTime? _CheckBirthDate;
        private DateTime? _CheckDate;
        private string _CheckDriverLicense;
        private string _CheckNumber;
        private decimal? _Coins;
        private decimal? _ContractualWriteoff;
        private DateTime? _CreditCardExpirationDate;
        private string _CreditCardNumber;
        private decimal? _Deductible;
        private string _ClaimControlNumber;
        private decimal? _Paid;
        private DMEWorks.Data.PaymentMethod? _PaymentMethod;
        private Guid? _PostingGuid;
        private decimal? _Sequestration;

        public PaymentExtraData()
        {
        }

        private PaymentExtraData(Pairs pairs)
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
                    switch (keyword)
                    {
                        case Keyword.Allowable:
                            pair.Value.PutInto<decimal>(ref this._Allowable);
                            break;

                        case Keyword.AmountLeft:
                            pair.Value.PutInto<decimal>(ref this._AmountLeft);
                            break;

                        case Keyword.Billable:
                            pair.Value.PutInto<decimal>(ref this._Billable);
                            break;

                        case Keyword.CheckBirthDate:
                            pair.Value.PutInto<DateTime>(ref this._CheckBirthDate);
                            break;

                        case Keyword.CheckDate:
                            pair.Value.PutInto<DateTime>(ref this._CheckDate);
                            break;

                        case Keyword.CheckDriverLicense:
                            pair.Value.PutInto(ref this._CheckDriverLicense);
                            break;

                        case Keyword.CheckNumber:
                            pair.Value.PutInto(ref this._CheckNumber);
                            break;

                        case Keyword.ClaimControlNumber:
                            pair.Value.PutInto(ref this._ClaimControlNumber);
                            break;

                        case Keyword.Coins:
                            pair.Value.PutInto<decimal>(ref this._Coins);
                            break;

                        case Keyword.ContractualWriteoff:
                            pair.Value.PutInto<decimal>(ref this._ContractualWriteoff);
                            break;

                        case Keyword.CreditCardExpirationDate:
                            pair.Value.PutInto<DateTime>(ref this._CreditCardExpirationDate);
                            break;

                        case Keyword.CreditCardNumber:
                            pair.Value.PutInto(ref this._CreditCardNumber);
                            break;

                        case Keyword.Deductible:
                            pair.Value.PutInto<decimal>(ref this._Deductible);
                            break;

                        case Keyword.Paid:
                            pair.Value.PutInto<decimal>(ref this._Paid);
                            break;

                        case Keyword.PaymentMethod:
                            pair.Value.PutInto<DMEWorks.Data.PaymentMethod>(ref this._PaymentMethod);
                            break;

                        case Keyword.PostingGuid:
                            pair.Value.PutInto<Guid>(ref this._PostingGuid);
                            break;

                        case Keyword.Sequestration:
                            pair.Value.PutInto<decimal>(ref this._Sequestration);
                            break;

                        default:
                            break;
                    }
                }
            }
        }

        public static PaymentExtraData Parse(string value)
        {
            Pairs pairs = null;
            try
            {
                pairs = Pairs.XmlDeserialize(value);
            }
            catch
            {
            }
            return new PaymentExtraData(pairs);
        }

        public static PaymentExtraData ParsePlain(string value) => 
            new PaymentExtraData(Pairs.PlainDeserialize(value));

        public override string ToString()
        {
            Pairs pairs = new Pairs();
            pairs.Append<decimal>(Keyword.Allowable, this._Allowable);
            pairs.Append<decimal>(Keyword.AmountLeft, this._AmountLeft);
            pairs.Append<decimal>(Keyword.Billable, this._Billable);
            pairs.Append<DateTime>(Keyword.CheckBirthDate, this._CheckBirthDate);
            pairs.Append<DateTime>(Keyword.CheckDate, this._CheckDate);
            pairs.Append(Keyword.CheckDriverLicense, this._CheckDriverLicense);
            pairs.Append(Keyword.CheckNumber, this._CheckNumber);
            pairs.Append(Keyword.ClaimControlNumber, this._ClaimControlNumber);
            pairs.Append<decimal>(Keyword.Coins, this._Coins);
            pairs.Append<decimal>(Keyword.ContractualWriteoff, this._ContractualWriteoff);
            pairs.Append<DateTime>(Keyword.CreditCardExpirationDate, this._CreditCardExpirationDate);
            pairs.Append(Keyword.CreditCardNumber, this._CreditCardNumber);
            pairs.Append<decimal>(Keyword.Deductible, this._Deductible);
            pairs.Append<decimal>(Keyword.Paid, this._Paid);
            pairs.Append<DMEWorks.Data.PaymentMethod>(Keyword.PaymentMethod, this._PaymentMethod);
            pairs.Append<Guid>(Keyword.PostingGuid, this._PostingGuid);
            pairs.Append<decimal>(Keyword.Sequestration, this._Sequestration);
            return Pairs.XmlSerialize(pairs);
        }

        [Category("Amounts")]
        public decimal? Allowable
        {
            get => 
                this._Allowable;
            set => 
                this._Allowable = value;
        }

        [Category("Amounts")]
        public decimal? Billable
        {
            get => 
                this._Billable;
            set => 
                this._Billable = value;
        }

        [Category("Amounts")]
        public decimal? AmountLeft
        {
            get => 
                this._AmountLeft;
            set => 
                this._AmountLeft = value;
        }

        [Category("Amounts")]
        public decimal? Coins
        {
            get => 
                this._Coins;
            set => 
                this._Coins = value;
        }

        [Category("Amounts")]
        public decimal? ContractualWriteoff
        {
            get => 
                this._ContractualWriteoff;
            set => 
                this._ContractualWriteoff = value;
        }

        [Category("Amounts")]
        public decimal? Deductible
        {
            get => 
                this._Deductible;
            set => 
                this._Deductible = value;
        }

        [Category("Amounts")]
        public decimal? Paid
        {
            get => 
                this._Paid;
            set => 
                this._Paid = value;
        }

        [Category("Amounts")]
        public decimal? Sequestration
        {
            get => 
                this._Sequestration;
            set => 
                this._Sequestration = value;
        }

        [Category("Check")]
        public DateTime? CheckBirthDate
        {
            get => 
                this._CheckBirthDate;
            set => 
                this._CheckBirthDate = value;
        }

        [Category("Check")]
        public DateTime? CheckDate
        {
            get => 
                this._CheckDate;
            set => 
                this._CheckDate = value;
        }

        [Category("Check")]
        public string CheckDriverLicense
        {
            get => 
                this._CheckDriverLicense;
            set => 
                this._CheckDriverLicense = value;
        }

        [Category("Check")]
        public string CheckNumber
        {
            get => 
                this._CheckNumber;
            set => 
                this._CheckNumber = value;
        }

        [Category("CreditCard")]
        public DateTime? CreditCardExpirationDate
        {
            get => 
                this._CreditCardExpirationDate;
            set => 
                this._CreditCardExpirationDate = value;
        }

        [Category("CreditCard")]
        public string CreditCardNumber
        {
            get => 
                this._CreditCardNumber;
            set => 
                this._CreditCardNumber = value;
        }

        [Description("Claim Control Number")]
        public string ClaimControlNumber
        {
            get => 
                this._ClaimControlNumber;
            set => 
                this._ClaimControlNumber = value;
        }

        public DMEWorks.Data.PaymentMethod? PaymentMethod
        {
            get => 
                this._PaymentMethod;
            set => 
                this._PaymentMethod = value;
        }

        [Description("Posting Guid")]
        public Guid? PostingGuid
        {
            get => 
                this._PostingGuid;
            set => 
                this._PostingGuid = value;
        }

        private enum Keyword
        {
            Allowable,
            AmountLeft,
            Billable,
            CheckBirthDate,
            CheckDate,
            CheckDriverLicense,
            CheckNumber,
            ClaimControlNumber,
            Coins,
            ContractualWriteoff,
            CreditCardExpirationDate,
            CreditCardNumber,
            Deductible,
            Paid,
            PaymentMethod,
            PostingGuid,
            Sequestration
        }
    }
}


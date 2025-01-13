namespace DMEWorks.Core
{
    using System;
    using System.Reflection;

    [AttributeUsage(AttributeTargets.Class)]
    public sealed class ButtonsAttribute : Attribute
    {
        private const int Flag_Clone = 1;
        private const int Flag_Close = 2;
        private const int Flag_Delete = 4;
        private const int Flag_Missing = 8;
        private const int Flag_New = 0x10;
        private const int Flag_Reload = 0x20;
        public static readonly ButtonsAttribute Default = new ButtonsAttribute();
        private int _data;

        public ButtonsAttribute()
        {
            this[1] = false;
            this[2] = true;
            this[4] = true;
            this[8] = false;
            this[0x10] = true;
            this[0x20] = false;
        }

        private bool this[int bit]
        {
            get => 
                (this._data & bit) == bit;
            set
            {
                if (value)
                {
                    this._data |= bit;
                }
                else
                {
                    this._data &= ~bit;
                }
            }
        }

        public bool ButtonClone
        {
            get => 
                this[1];
            set => 
                this[1] = value;
        }

        public bool ButtonClose
        {
            get => 
                this[2];
            set => 
                this[2] = value;
        }

        public bool ButtonDelete
        {
            get => 
                this[4];
            set => 
                this[4] = value;
        }

        public bool ButtonNew
        {
            get => 
                this[0x10];
            set => 
                this[0x10] = value;
        }

        public bool ButtonMissing
        {
            get => 
                this[8];
            set => 
                this[8] = value;
        }

        public bool ButtonReload
        {
            get => 
                this[0x20];
            set => 
                this[0x20] = value;
        }
    }
}


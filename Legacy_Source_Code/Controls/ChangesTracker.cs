namespace DMEWorks.Controls
{
    using DMEWorks.Forms;
    using Infragistics.Win.UltraWinEditors;
    using System;
    using System.Windows.Forms;

    public class ChangesTracker
    {
        private readonly EventHandler m_handler;
        private readonly ErrorProvider m_provider;

        public ChangesTracker(EventHandler handler) : this(handler, null)
        {
        }

        public ChangesTracker(EventHandler handler, ErrorProvider provider)
        {
            if (handler == null)
            {
                EventHandler local1 = handler;
                throw new ArgumentNullException("handler");
            }
            this.m_handler = handler;
            this.m_provider = provider;
        }

        private void AttachTracker(Control control)
        {
            if ((control != null) && (this.m_provider != null))
            {
                this.m_provider.SetError(control, "IsTracking");
                this.m_provider.SetIconAlignment(control, ErrorIconAlignment.TopLeft);
                this.m_provider.SetIconPadding(control, -16);
            }
        }

        private void HandleControlChanged(object sender, EventArgs args)
        {
            this.m_handler(sender, args);
        }

        public void Subscribe(ControlAddress control)
        {
            if (control != null)
            {
                this.Subscribe(control.txtZip);
                this.Subscribe(control.txtState);
                this.Subscribe(control.txtCity);
                this.Subscribe(control.txtAddress2);
                this.Subscribe(control.txtAddress1);
            }
        }

        public void Subscribe(ControlName control)
        {
            if (control != null)
            {
                this.Subscribe(control.cmbCourtesy);
                this.Subscribe(control.txtFirstName);
                this.Subscribe(control.txtLastName);
                this.Subscribe(control.txtMiddleName);
                this.Subscribe(control.txtSuffix);
            }
        }

        public void Subscribe(Combobox control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.SelectedIndexChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(ExtendedDropdown control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.TextChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(NumericBox control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.ValueChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(UltraDateTimeEditor control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.ValueChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(CheckBox control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.CheckedChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(ComboBox control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.TextChanged += new EventHandler(this.HandleControlChanged);
                control.SelectedIndexChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(NumericUpDown control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.ValueChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(RadioButton control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.CheckedChanged += new EventHandler(this.HandleControlChanged);
            }
        }

        public void Subscribe(TextBox control)
        {
            if (control != null)
            {
                this.AttachTracker(control);
                control.TextChanged += new EventHandler(this.HandleControlChanged);
            }
        }
    }
}


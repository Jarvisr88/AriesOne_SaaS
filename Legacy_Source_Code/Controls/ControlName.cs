namespace DMEWorks.Controls
{
    using System;
    using System.ComponentModel;
    using System.Drawing;
    using System.Windows.Forms;

    public class ControlName : UserControl
    {
        private IContainer components;
        public TextBox txtSuffix;
        public Label lblSuffix;
        public ComboBox cmbCourtesy;
        public Label lblCourtesy;
        public TextBox txtLastName;
        public Label lblLastName;
        public TextBox txtMiddleName;
        public TextBox txtFirstName;
        public Label lblMiddleName;
        public Label lblFirstName;

        public ControlName()
        {
            this.InitializeComponent();
            this.txtFirstName.TextChanged += new EventHandler(this.HandleTextChanged);
            this.txtMiddleName.TextChanged += new EventHandler(this.HandleTextChanged);
            this.txtLastName.TextChanged += new EventHandler(this.HandleTextChanged);
            this.txtSuffix.TextChanged += new EventHandler(this.HandleTextChanged);
            this.cmbCourtesy.TextChanged += new EventHandler(this.HandleTextChanged);
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void HandleTextChanged(object sender, EventArgs args)
        {
            this.OnTextChanged(args);
        }

        private void InitializeComponent()
        {
            this.txtSuffix = new TextBox();
            this.lblSuffix = new Label();
            this.cmbCourtesy = new ComboBox();
            this.lblCourtesy = new Label();
            this.txtLastName = new TextBox();
            this.lblLastName = new Label();
            this.txtMiddleName = new TextBox();
            this.txtFirstName = new TextBox();
            this.lblMiddleName = new Label();
            this.lblFirstName = new Label();
            base.SuspendLayout();
            this.txtSuffix.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.txtSuffix.Location = new Point(0x158, 0x18);
            this.txtSuffix.MaxLength = 4;
            this.txtSuffix.Name = "txtSuffix";
            this.txtSuffix.Size = new Size(0x40, 20);
            this.txtSuffix.TabIndex = 9;
            this.lblSuffix.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.lblSuffix.Location = new Point(0x128, 0x18);
            this.lblSuffix.Name = "lblSuffix";
            this.lblSuffix.Size = new Size(40, 0x15);
            this.lblSuffix.TabIndex = 8;
            this.lblSuffix.Text = "Suffix";
            this.lblSuffix.TextAlign = ContentAlignment.MiddleRight;
            this.cmbCourtesy.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            object[] items = new object[] { "Mr.", "Mrs.", "Miss", "Dr.", "Rev." };
            this.cmbCourtesy.Items.AddRange(items);
            this.cmbCourtesy.Location = new Point(0x158, 0);
            this.cmbCourtesy.Name = "cmbCourtesy";
            this.cmbCourtesy.RightToLeft = RightToLeft.No;
            this.cmbCourtesy.Size = new Size(0x40, 0x15);
            this.cmbCourtesy.TabIndex = 3;
            this.lblCourtesy.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.lblCourtesy.Location = new Point(240, 0);
            this.lblCourtesy.Name = "lblCourtesy";
            this.lblCourtesy.Size = new Size(0x60, 0x15);
            this.lblCourtesy.TabIndex = 2;
            this.lblCourtesy.Text = "Courtesy";
            this.lblCourtesy.TextAlign = ContentAlignment.MiddleRight;
            this.txtLastName.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.txtLastName.Location = new Point(40, 0);
            this.txtLastName.Name = "txtLastName";
            this.txtLastName.Size = new Size(200, 20);
            this.txtLastName.TabIndex = 1;
            this.lblLastName.Location = new Point(0, 0);
            this.lblLastName.Name = "lblLastName";
            this.lblLastName.Size = new Size(0x20, 0x15);
            this.lblLastName.TabIndex = 0;
            this.lblLastName.Text = "Last";
            this.lblLastName.TextAlign = ContentAlignment.MiddleRight;
            this.txtMiddleName.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.txtMiddleName.Location = new Point(0x110, 0x18);
            this.txtMiddleName.MaxLength = 1;
            this.txtMiddleName.Name = "txtMiddleName";
            this.txtMiddleName.Size = new Size(0x18, 20);
            this.txtMiddleName.TabIndex = 7;
            this.txtFirstName.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.txtFirstName.Location = new Point(40, 0x18);
            this.txtFirstName.Name = "txtFirstName";
            this.txtFirstName.Size = new Size(200, 20);
            this.txtFirstName.TabIndex = 5;
            this.lblMiddleName.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.lblMiddleName.Location = new Point(240, 0x18);
            this.lblMiddleName.Name = "lblMiddleName";
            this.lblMiddleName.Size = new Size(0x18, 0x16);
            this.lblMiddleName.TabIndex = 6;
            this.lblMiddleName.Text = "MI";
            this.lblMiddleName.TextAlign = ContentAlignment.MiddleRight;
            this.lblFirstName.Location = new Point(0, 0x18);
            this.lblFirstName.Name = "lblFirstName";
            this.lblFirstName.Size = new Size(0x20, 0x15);
            this.lblFirstName.TabIndex = 4;
            this.lblFirstName.Text = "First";
            this.lblFirstName.TextAlign = ContentAlignment.MiddleRight;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.Controls.Add(this.txtSuffix);
            base.Controls.Add(this.lblSuffix);
            base.Controls.Add(this.cmbCourtesy);
            base.Controls.Add(this.lblCourtesy);
            base.Controls.Add(this.txtLastName);
            base.Controls.Add(this.lblLastName);
            base.Controls.Add(this.txtMiddleName);
            base.Controls.Add(this.txtFirstName);
            base.Controls.Add(this.lblMiddleName);
            base.Controls.Add(this.lblFirstName);
            base.Name = "ControlName";
            base.Size = new Size(0x198, 0x30);
            base.ResumeLayout(false);
            base.PerformLayout();
        }
    }
}


namespace DMEWorks.PriceUtilities
{
    using System;
    using System.ComponentModel;
    using System.Drawing;
    using System.Windows.Forms;

    public class FormUpdateParameters : Form
    {
        private IContainer components;
        private Button btnOK;
        private Label lblPercent;
        private NumericUpDown nudPercent;
        private Button btnCancel;

        public FormUpdateParameters()
        {
            this.InitializeComponent();
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            base.DialogResult = DialogResult.Cancel;
            base.Close();
        }

        private void btnOK_Click(object sender, EventArgs e)
        {
            base.DialogResult = DialogResult.OK;
            base.Close();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.btnOK = new Button();
            this.lblPercent = new Label();
            this.nudPercent = new NumericUpDown();
            this.btnCancel = new Button();
            this.nudPercent.BeginInit();
            base.SuspendLayout();
            this.btnOK.Location = new Point(0x40, 0x60);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new Size(0x4b, 0x17);
            this.btnOK.TabIndex = 2;
            this.btnOK.Text = "OK";
            this.btnOK.UseVisualStyleBackColor = true;
            this.btnOK.Click += new EventHandler(this.btnOK_Click);
            this.lblPercent.Location = new Point(8, 8);
            this.lblPercent.Name = "lblPercent";
            this.lblPercent.Size = new Size(0x108, 40);
            this.lblPercent.TabIndex = 0;
            this.lblPercent.Text = "Please select percentage for update. You may use negative value for decreasing price.\r\n";
            this.nudPercent.DecimalPlaces = 2;
            this.nudPercent.Location = new Point(0x10, 0x38);
            int[] bits = new int[4];
            bits[0] = 0x63;
            bits[3] = -2147483648;
            this.nudPercent.Minimum = new decimal(bits);
            this.nudPercent.Name = "nudPercent";
            this.nudPercent.Size = new Size(0x58, 20);
            this.nudPercent.TabIndex = 1;
            this.btnCancel.DialogResult = DialogResult.Cancel;
            this.btnCancel.Location = new Point(0x90, 0x60);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new Size(0x4b, 0x17);
            this.btnCancel.TabIndex = 3;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new EventHandler(this.btnCancel_Click);
            base.AcceptButton = this.btnOK;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.CancelButton = this.btnCancel;
            base.ClientSize = new Size(0x11a, 0x87);
            base.Controls.Add(this.btnCancel);
            base.Controls.Add(this.nudPercent);
            base.Controls.Add(this.lblPercent);
            base.Controls.Add(this.btnOK);
            base.FormBorderStyle = FormBorderStyle.FixedSingle;
            base.MaximizeBox = false;
            base.Name = "FormUpdateParameters";
            base.ShowIcon = false;
            base.StartPosition = FormStartPosition.CenterScreen;
            this.Text = "Update Entire Price List";
            this.nudPercent.EndInit();
            base.ResumeLayout(false);
        }

        public decimal Percent
        {
            get => 
                this.nudPercent.Value;
            set => 
                this.nudPercent.Value = value;
        }
    }
}


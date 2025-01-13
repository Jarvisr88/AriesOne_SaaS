namespace DMEWorks.Misc
{
    using DMEWorks.Data;
    using System;
    using System.ComponentModel;
    using System.Drawing;
    using System.Windows.Forms;

    public class DialogVoidSubmission : Form
    {
        private IContainer components;
        private RadioButton rbAction_Void;
        private RadioButton rbAction_Replacement;
        private Label lblClaimNumber;
        private TextBox txtClaimNumber;
        private Label lblVoidMethod;
        private Button btnOK;
        private Button btnCancel;

        public DialogVoidSubmission()
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
            if (this.IsValid())
            {
                base.DialogResult = DialogResult.OK;
                base.Close();
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void EnableButton()
        {
            this.btnOK.Enabled = this.IsValid();
        }

        private void InitializeComponent()
        {
            this.rbAction_Void = new RadioButton();
            this.rbAction_Replacement = new RadioButton();
            this.lblClaimNumber = new Label();
            this.txtClaimNumber = new TextBox();
            this.lblVoidMethod = new Label();
            this.btnOK = new Button();
            this.btnCancel = new Button();
            base.SuspendLayout();
            this.rbAction_Void.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.rbAction_Void.Location = new Point(0x18, 0x38);
            this.rbAction_Void.Name = "rbAction_Void";
            this.rbAction_Void.Size = new Size(0xe8, 0x15);
            this.rbAction_Void.TabIndex = 2;
            this.rbAction_Void.TabStop = true;
            this.rbAction_Void.Text = "Void";
            this.rbAction_Void.UseVisualStyleBackColor = true;
            this.rbAction_Void.Click += new EventHandler(this.rbAction_Click);
            this.rbAction_Replacement.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.rbAction_Replacement.Location = new Point(0x18, 0x20);
            this.rbAction_Replacement.Name = "rbAction_Replacement";
            this.rbAction_Replacement.Size = new Size(0xe8, 0x15);
            this.rbAction_Replacement.TabIndex = 1;
            this.rbAction_Replacement.TabStop = true;
            this.rbAction_Replacement.Text = "Replacement";
            this.rbAction_Replacement.UseVisualStyleBackColor = true;
            this.rbAction_Replacement.Click += new EventHandler(this.rbAction_Click);
            this.lblClaimNumber.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.lblClaimNumber.Location = new Point(8, 0x58);
            this.lblClaimNumber.Name = "lblClaimNumber";
            this.lblClaimNumber.Size = new Size(0x108, 0x15);
            this.lblClaimNumber.TabIndex = 3;
            this.lblClaimNumber.Text = "Claim Number";
            this.txtClaimNumber.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.txtClaimNumber.Location = new Point(0x18, 0x70);
            this.txtClaimNumber.Name = "txtClaimNumber";
            this.txtClaimNumber.Size = new Size(0xe8, 20);
            this.txtClaimNumber.TabIndex = 4;
            this.txtClaimNumber.TextChanged += new EventHandler(this.txtClaimNumber_TextChanged);
            this.lblVoidMethod.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.lblVoidMethod.Location = new Point(8, 8);
            this.lblVoidMethod.Name = "lblVoidMethod";
            this.lblVoidMethod.Size = new Size(0x100, 0x15);
            this.lblVoidMethod.TabIndex = 0;
            this.lblVoidMethod.Text = "Action";
            this.btnOK.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.btnOK.Location = new Point(0x70, 0x90);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new Size(0x4b, 0x19);
            this.btnOK.TabIndex = 5;
            this.btnOK.Text = "OK";
            this.btnOK.UseVisualStyleBackColor = true;
            this.btnOK.Click += new EventHandler(this.btnOK_Click);
            this.btnCancel.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.btnCancel.DialogResult = DialogResult.Cancel;
            this.btnCancel.Location = new Point(0xc0, 0x90);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new Size(0x4b, 0x19);
            this.btnCancel.TabIndex = 6;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new EventHandler(this.btnCancel_Click);
            base.AcceptButton = this.btnOK;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.CancelButton = this.btnCancel;
            base.ClientSize = new Size(0x114, 0xb1);
            base.Controls.Add(this.btnCancel);
            base.Controls.Add(this.btnOK);
            base.Controls.Add(this.rbAction_Void);
            base.Controls.Add(this.lblVoidMethod);
            base.Controls.Add(this.rbAction_Replacement);
            base.Controls.Add(this.txtClaimNumber);
            base.Controls.Add(this.lblClaimNumber);
            base.FormBorderStyle = FormBorderStyle.FixedSingle;
            base.Name = "DialogVoidSubmission";
            this.Text = "Correct Submission";
            base.ResumeLayout(false);
            base.PerformLayout();
        }

        private bool IsValid() => 
            (this.rbAction_Replacement.Checked || this.rbAction_Void.Checked) & !string.IsNullOrWhiteSpace(this.txtClaimNumber.Text);

        private void rbAction_Click(object sender, EventArgs e)
        {
            this.EnableButton();
        }

        private void txtClaimNumber_TextChanged(object sender, EventArgs e)
        {
            this.EnableButton();
        }

        public DMEWorks.Data.VoidMethod VoidMethod
        {
            get
            {
                if (this.rbAction_Replacement.Checked)
                {
                    return DMEWorks.Data.VoidMethod.Replacement;
                }
                if (!this.rbAction_Void.Checked)
                {
                    throw new InvalidOperationException();
                }
                return DMEWorks.Data.VoidMethod.Void;
            }
        }

        public string ClaimNumber =>
            (this.txtClaimNumber.Text ?? string.Empty).Trim();
    }
}


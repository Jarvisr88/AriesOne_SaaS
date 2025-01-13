namespace DMEWorks.PriceUtilities
{
    using Devart.Data.MySql;
    using DMEWorks;
    using DMEWorks.Forms;
    using System;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.Windows.Forms;

    public class FormSelectPricelist : DmeForm
    {
        private IContainer components;
        private Label lblPricelist;
        private ComboBox cmbPriceList;
        private Button btnOK;
        private Button btnCancel;

        public FormSelectPricelist()
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
            if (this.cmbPriceList.SelectedValue is int)
            {
                base.DialogResult = DialogResult.OK;
                base.Close();
            }
        }

        private void cmbPriceList_SelectedIndexChanged(object sender, EventArgs e)
        {
            this.btnOK.Enabled = this.cmbPriceList.SelectedValue is int;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void FormSelectPricelist_Load(object sender, EventArgs e)
        {
            try
            {
                DataTable dataTable = new DataTable("tbl_pricecode");
                dataTable.Columns.Add("ID", typeof(int));
                dataTable.Columns.Add("Name", typeof(string));
                DataRow row = dataTable.NewRow();
                dataTable.Rows.Add(row);
                row.AcceptChanges();
                using (MySqlDataAdapter adapter = new MySqlDataAdapter("", Globals.ConnectionString))
                {
                    adapter.SelectCommand.CommandText = "SELECT ID, Name FROM tbl_pricecode ORDER BY Name";
                    adapter.AcceptChangesDuringFill = true;
                    adapter.Fill(dataTable);
                }
                this.cmbPriceList.DataSource = dataTable.DefaultView;
                this.cmbPriceList.DisplayMember = "Name";
                this.cmbPriceList.ValueMember = "ID";
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private void InitializeComponent()
        {
            this.lblPricelist = new Label();
            this.cmbPriceList = new ComboBox();
            this.btnOK = new Button();
            this.btnCancel = new Button();
            base.SuspendLayout();
            this.lblPricelist.Location = new Point(8, 8);
            this.lblPricelist.Name = "lblPricelist";
            this.lblPricelist.Size = new Size(280, 0x20);
            this.lblPricelist.TabIndex = 0;
            this.lblPricelist.Text = "Select price list for editing";
            this.cmbPriceList.Location = new Point(8, 0x30);
            this.cmbPriceList.Name = "cmbPriceList";
            this.cmbPriceList.Size = new Size(0x110, 0x15);
            this.cmbPriceList.TabIndex = 1;
            this.cmbPriceList.SelectedIndexChanged += new EventHandler(this.cmbPriceList_SelectedIndexChanged);
            this.btnOK.Enabled = false;
            this.btnOK.Location = new Point(0x48, 0x98);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new Size(0x4b, 0x17);
            this.btnOK.TabIndex = 2;
            this.btnOK.Text = "OK";
            this.btnOK.UseVisualStyleBackColor = true;
            this.btnOK.Click += new EventHandler(this.btnOK_Click);
            this.btnCancel.DialogResult = DialogResult.Cancel;
            this.btnCancel.Location = new Point(0x98, 0x98);
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
            base.ClientSize = new Size(0x124, 0xc6);
            base.Controls.Add(this.btnCancel);
            base.Controls.Add(this.btnOK);
            base.Controls.Add(this.cmbPriceList);
            base.Controls.Add(this.lblPricelist);
            base.Name = "FormSelectPricelist";
            this.Text = "FormSelectPricelist";
            base.Load += new EventHandler(this.FormSelectPricelist_Load);
            base.ResumeLayout(false);
        }

        public object PriceCodeID
        {
            get => 
                this.cmbPriceList.SelectedValue;
            set => 
                this.cmbPriceList.SelectedValue = value;
        }
    }
}


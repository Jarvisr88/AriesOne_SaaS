namespace DMEWorks.PriceUtilities
{
    using Devart.Data.MySql;
    using DMEWorks;
    using DMEWorks.Forms;
    using DMEWorks.Properties;
    using System;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.Windows.Forms;

    public class FormPriceListEditor : DmeForm
    {
        private readonly TablePriceList F_Table;
        private bool _updateExistingOrders;
        private IContainer components;
        private DataGridView grid;
        private ToolStrip toolStrip1;
        private ToolStripButton tsbtnUpdateExistingOrders;
        private ToolStripButton tsbtnSave;
        private ToolStripButton tsbtnUpdateList;
        private DataGridViewTextBoxColumn dgcBillingCode;
        private DataGridViewTextBoxColumn dgcRent_AllowablePrice;
        private DataGridViewTextBoxColumn dgcRent_BillablePrice;
        private DataGridViewTextBoxColumn dgcSale_AllowablePrice;
        private DataGridViewTextBoxColumn dgcSale_BillablePrice;
        private ToolStripComboBox tscmbPriceList;
        private ToolStripSeparator toolStripSeparator3;
        private ToolStripSeparator toolStripSeparator1;
        private ToolStripSeparator toolStripSeparator2;

        public FormPriceListEditor()
        {
            this.InitializeComponent();
            this.F_Table = new TablePriceList("tbl_pricelist");
            this.F_Table.DefaultView.AllowDelete = false;
            this.F_Table.DefaultView.AllowEdit = true;
            this.F_Table.DefaultView.AllowNew = false;
            this.grid.AutoGenerateColumns = false;
            this.grid.DataSource = this.F_Table.DefaultView;
        }

        private static void ClearTable(TablePriceList table)
        {
            table.Rows.Clear();
            table.AcceptChanges();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void FillGrid(object PriceCodeID)
        {
            this.grid.DataSource = null;
            try
            {
                ClearTable(this.F_Table);
                if (PriceCodeID is int)
                {
                    LoadTable(this.F_Table, Globals.ConnectionString, (int) PriceCodeID);
                }
            }
            finally
            {
                this.grid.DataSource = this.F_Table.DefaultView;
            }
        }

        private void InitializeComponent()
        {
            DataGridViewCellStyle style = new DataGridViewCellStyle();
            DataGridViewCellStyle style2 = new DataGridViewCellStyle();
            DataGridViewCellStyle style3 = new DataGridViewCellStyle();
            DataGridViewCellStyle style4 = new DataGridViewCellStyle();
            DataGridViewCellStyle style5 = new DataGridViewCellStyle();
            ComponentResourceManager manager = new ComponentResourceManager(typeof(FormPriceListEditor));
            this.grid = new DataGridView();
            this.dgcBillingCode = new DataGridViewTextBoxColumn();
            this.dgcRent_AllowablePrice = new DataGridViewTextBoxColumn();
            this.dgcRent_BillablePrice = new DataGridViewTextBoxColumn();
            this.dgcSale_AllowablePrice = new DataGridViewTextBoxColumn();
            this.dgcSale_BillablePrice = new DataGridViewTextBoxColumn();
            this.toolStrip1 = new ToolStrip();
            this.tscmbPriceList = new ToolStripComboBox();
            this.tsbtnUpdateExistingOrders = new ToolStripButton();
            this.tsbtnSave = new ToolStripButton();
            this.tsbtnUpdateList = new ToolStripButton();
            this.toolStripSeparator1 = new ToolStripSeparator();
            this.toolStripSeparator2 = new ToolStripSeparator();
            this.toolStripSeparator3 = new ToolStripSeparator();
            ((ISupportInitialize) this.grid).BeginInit();
            this.toolStrip1.SuspendLayout();
            base.SuspendLayout();
            this.grid.AllowUserToAddRows = false;
            this.grid.AllowUserToDeleteRows = false;
            this.grid.AllowUserToResizeColumns = false;
            this.grid.AllowUserToResizeRows = false;
            this.grid.BackgroundColor = SystemColors.ControlDark;
            this.grid.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing;
            DataGridViewColumn[] dataGridViewColumns = new DataGridViewColumn[] { this.dgcBillingCode, this.dgcRent_AllowablePrice, this.dgcRent_BillablePrice, this.dgcSale_AllowablePrice, this.dgcSale_BillablePrice };
            this.grid.Columns.AddRange(dataGridViewColumns);
            this.grid.Dock = DockStyle.Fill;
            this.grid.Location = new Point(0, 0x19);
            this.grid.MultiSelect = false;
            this.grid.Name = "grid";
            this.grid.RowHeadersWidth = 0x20;
            this.grid.Size = new Size(0x252, 400);
            this.grid.TabIndex = 1;
            this.dgcBillingCode.DataPropertyName = "BillingCode";
            style.Alignment = DataGridViewContentAlignment.MiddleLeft;
            this.dgcBillingCode.DefaultCellStyle = style;
            this.dgcBillingCode.Frozen = true;
            this.dgcBillingCode.HeaderText = "Billing Code";
            this.dgcBillingCode.Name = "dgcBillingCode";
            this.dgcRent_AllowablePrice.DataPropertyName = "Rent_AllowablePrice";
            style2.Alignment = DataGridViewContentAlignment.MiddleRight;
            style2.Format = "N2";
            style2.NullValue = null;
            this.dgcRent_AllowablePrice.DefaultCellStyle = style2;
            this.dgcRent_AllowablePrice.HeaderText = "Rent Allowable";
            this.dgcRent_AllowablePrice.Name = "dgcRent_AllowablePrice";
            this.dgcRent_BillablePrice.DataPropertyName = "Rent_BillablePrice";
            style3.Alignment = DataGridViewContentAlignment.MiddleRight;
            style3.Format = "N2";
            style3.NullValue = null;
            this.dgcRent_BillablePrice.DefaultCellStyle = style3;
            this.dgcRent_BillablePrice.HeaderText = "Rent Billable";
            this.dgcRent_BillablePrice.Name = "dgcRent_BillablePrice";
            this.dgcSale_AllowablePrice.DataPropertyName = "Sale_AllowablePrice";
            style4.Alignment = DataGridViewContentAlignment.MiddleRight;
            style4.Format = "N2";
            style4.NullValue = null;
            this.dgcSale_AllowablePrice.DefaultCellStyle = style4;
            this.dgcSale_AllowablePrice.HeaderText = "Sale Allowable";
            this.dgcSale_AllowablePrice.Name = "dgcSale_AllowablePrice";
            this.dgcSale_BillablePrice.DataPropertyName = "Sale_BillablePrice";
            style5.Alignment = DataGridViewContentAlignment.MiddleRight;
            style5.Format = "N2";
            style5.NullValue = null;
            this.dgcSale_BillablePrice.DefaultCellStyle = style5;
            this.dgcSale_BillablePrice.HeaderText = "Sale Billable";
            this.dgcSale_BillablePrice.Name = "dgcSale_BillablePrice";
            ToolStripItem[] toolStripItems = new ToolStripItem[] { this.tscmbPriceList, this.toolStripSeparator3, this.tsbtnUpdateExistingOrders, this.toolStripSeparator1, this.tsbtnUpdateList, this.toolStripSeparator2, this.tsbtnSave };
            this.toolStrip1.Items.AddRange(toolStripItems);
            this.toolStrip1.Location = new Point(0, 0);
            this.toolStrip1.Name = "toolStrip1";
            this.toolStrip1.Size = new Size(0x252, 0x19);
            this.toolStrip1.TabIndex = 0;
            this.toolStrip1.Text = "toolStrip1";
            this.tscmbPriceList.Name = "tscmbPriceList";
            this.tscmbPriceList.Size = new Size(0x79, 0x19);
            this.tscmbPriceList.SelectedIndexChanged += new EventHandler(this.tscmbPriceList_SelectedIndexChanged);
            this.tsbtnUpdateExistingOrders.Image = Resources.Unchecked;
            this.tsbtnUpdateExistingOrders.ImageTransparentColor = Color.Magenta;
            this.tsbtnUpdateExistingOrders.Name = "tsbtnUpdateExistingOrders";
            this.tsbtnUpdateExistingOrders.Size = new Size(0x8a, 0x16);
            this.tsbtnUpdateExistingOrders.Text = "Update Existing Orders";
            this.tsbtnUpdateExistingOrders.Click += new EventHandler(this.tsbtnUpdateExistingOrders_Click);
            this.tsbtnSave.DisplayStyle = ToolStripItemDisplayStyle.Text;
            this.tsbtnSave.Image = (Image) manager.GetObject("tsbtnSave.Image");
            this.tsbtnSave.ImageTransparentColor = Color.Magenta;
            this.tsbtnSave.Name = "tsbtnSave";
            this.tsbtnSave.Size = new Size(0x23, 0x16);
            this.tsbtnSave.Text = "Save";
            this.tsbtnSave.Click += new EventHandler(this.tsbtnSave_Click);
            this.tsbtnUpdateList.DisplayStyle = ToolStripItemDisplayStyle.Text;
            this.tsbtnUpdateList.Image = (Image) manager.GetObject("tsbtnUpdateList.Image");
            this.tsbtnUpdateList.ImageTransparentColor = Color.Magenta;
            this.tsbtnUpdateList.Name = "tsbtnUpdateList";
            this.tsbtnUpdateList.Size = new Size(0x41, 0x16);
            this.tsbtnUpdateList.Text = "Update List";
            this.tsbtnUpdateList.Click += new EventHandler(this.tsbtnUpdateList_Click);
            this.toolStripSeparator1.Name = "toolStripSeparator1";
            this.toolStripSeparator1.Size = new Size(6, 0x19);
            this.toolStripSeparator2.Name = "toolStripSeparator2";
            this.toolStripSeparator2.Size = new Size(6, 0x19);
            this.toolStripSeparator3.Name = "toolStripSeparator3";
            this.toolStripSeparator3.Size = new Size(6, 0x19);
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.ClientSize = new Size(0x252, 0x1a9);
            base.Controls.Add(this.grid);
            base.Controls.Add(this.toolStrip1);
            base.Name = "FormPriceListEditor";
            base.ShowIcon = false;
            this.Text = "Update Entire Price List";
            base.Load += new EventHandler(this.mainForm_Load);
            ((ISupportInitialize) this.grid).EndInit();
            this.toolStrip1.ResumeLayout(false);
            this.toolStrip1.PerformLayout();
            base.ResumeLayout(false);
            base.PerformLayout();
        }

        private static void LoadTable(TablePriceList table, string connectionString, int priceCodeID)
        {
            using (MySqlDataAdapter adapter = new MySqlDataAdapter("", connectionString))
            {
                adapter.SelectCommand.CommandText = "SELECT\n  BillingCode,\n  MIN(Rent_AllowablePrice) as Rent_AllowablePrice,\n  MIN(Rent_BillablePrice ) as Rent_BillablePrice,\n  MIN(Sale_AllowablePrice) as Sale_AllowablePrice,\n  MIN(Sale_BillablePrice ) as Sale_BillablePrice\nFROM tbl_pricecode_item\nWHERE (PriceCodeID = :PriceCodeID)\n  AND (IFNULL(BillingCode, '') != '')\nGROUP BY BillingCode\n";
                adapter.SelectCommand.Parameters.Add("PriceCodeID", MySqlType.Int).Value = priceCodeID;
                adapter.AcceptChangesDuringFill = true;
                adapter.Fill(table);
            }
        }

        private void mainForm_Load(object sender, EventArgs e)
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
                this.tscmbPriceList.ComboBox.DataSource = dataTable.DefaultView;
                this.tscmbPriceList.ComboBox.DisplayMember = "Name";
                this.tscmbPriceList.ComboBox.ValueMember = "ID";
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private static void SaveTable(TablePriceList table, string connectionString, int priceCodeID, bool updateOrders)
        {
            using (MySqlConnection connection = new MySqlConnection(connectionString))
            {
                connection.Open();
                MySqlTransaction transaction = connection.BeginTransaction();
                try
                {
                    Guid guid = Guid.NewGuid();
                    using (MySqlCommand command = new MySqlCommand("", connection, transaction))
                    {
                        command.Parameters.Clear();
                        command.CommandText = $"CREATE TEMPORARY TABLE `{guid}` (
  `BillingCode` varchar(50) NOT NULL PRIMARY KEY,
  `Rent_AllowablePrice` decimal(18,2) NOT NULL,
  `Rent_BillablePrice`  decimal(18,2) NOT NULL,
  `Sale_AllowablePrice` decimal(18,2) NOT NULL,
  `Sale_BillablePrice`  decimal(18,2) NOT NULL)";
                        command.ExecuteNonQuery();
                        using (MySqlCommand command2 = new MySqlCommand("", connection, transaction))
                        {
                            command2.CommandText = $"INSERT INTO `{guid}` (`BillingCode`, `Rent_AllowablePrice`, `Rent_BillablePrice`, `Sale_AllowablePrice`, `Sale_BillablePrice`)
VALUES (:BillingCode, :Rent_AllowablePrice, :Rent_BillablePrice, :Sale_AllowablePrice, :Sale_BillablePrice)";
                            MySqlParameter parameter = command2.Parameters.Add("BillingCode", MySqlType.VarChar, 50);
                            MySqlParameter parameter2 = command2.Parameters.Add("Rent_AllowablePrice", MySqlType.Decimal);
                            MySqlParameter parameter3 = command2.Parameters.Add("Rent_BillablePrice", MySqlType.Decimal);
                            MySqlParameter parameter4 = command2.Parameters.Add("Sale_AllowablePrice", MySqlType.Decimal);
                            MySqlParameter parameter5 = command2.Parameters.Add("Sale_BillablePrice", MySqlType.Decimal);
                            foreach (DataRow row in table.Select("", "", DataViewRowState.ModifiedCurrent))
                            {
                                parameter.Value = row[table.Col_BillingCode];
                                parameter2.Value = row[table.Col_Rent_AllowablePrice];
                                parameter3.Value = row[table.Col_Rent_BillablePrice];
                                parameter4.Value = row[table.Col_Sale_AllowablePrice];
                                parameter5.Value = row[table.Col_Sale_BillablePrice];
                                command2.ExecuteNonQuery();
                            }
                        }
                        command.Parameters.Clear();
                        command.CommandText = string.Format("UPDATE tbl_pricecode_item\n       INNER JOIN `{0}` ON tbl_pricecode_item.BillingCode = `{0}`.BillingCode\nSET\n   tbl_pricecode_item.Rent_AllowablePrice = `{0}`.Rent_AllowablePrice  ,tbl_pricecode_item.Rent_BillablePrice  = `{0}`.Rent_BillablePrice\n  ,tbl_pricecode_item.Sale_AllowablePrice = `{0}`.Sale_AllowablePrice\n  ,tbl_pricecode_item.Sale_BillablePrice  = `{0}`.Sale_BillablePrice\nWHERE tbl_pricecode_item.PriceCodeID = :pricecodeid\n", guid);
                        command.Parameters.Add("pricecodeid", MySqlType.Int).Value = priceCodeID;
                        command.ExecuteNonQuery();
                        if (updateOrders)
                        {
                            command.Parameters.Clear();
                            command.CommandText = string.Format("UPDATE tbl_orderdetails\n       INNER JOIN tbl_order ON tbl_orderdetails.OrderID = tbl_order.ID\n                           AND tbl_orderdetails.CustomerID = tbl_order.CustomerID\n       INNER JOIN tbl_pricecode_item ON tbl_orderdetails.InventoryItemID = tbl_pricecode_item.InventoryItemID\n                                    AND tbl_orderdetails.PriceCodeID = tbl_pricecode_item.PriceCodeID\n       INNER JOIN `{0}` ON tbl_pricecode_item.BillingCode = `{0}`.BillingCode\nSET tbl_orderdetails.AllowablePrice =\n  CASE tbl_orderdetails.SaleRentType\n       WHEN 'Medicare Oxygen Rental' THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Monthly Rental'         THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Capped Rental'          THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Parental Capped Rental' THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Rent to Purchase'       THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'One Time Sale'          THEN tbl_pricecode_item.Sale_AllowablePrice\n       WHEN 'Re-occurring Sale'      THEN tbl_pricecode_item.Sale_AllowablePrice\n       ELSE NULL END,\n    tbl_orderdetails.BillablePrice =\n  CASE tbl_orderdetails.SaleRentType\n       WHEN 'Medicare Oxygen Rental' THEN tbl_pricecode_item.Rent_BillablePrice\n       WHEN 'Monthly Rental'         THEN tbl_pricecode_item.Rent_BillablePrice\n       WHEN 'Capped Rental'          THEN tbl_pricecode_item.Rent_BillablePrice\n       WHEN 'Parental Capped Rental' THEN tbl_pricecode_item.Rent_BillablePrice\n       WHEN 'Rent to Purchase'       THEN tbl_pricecode_item.Rent_BillablePrice\n       WHEN 'One Time Sale'          THEN tbl_pricecode_item.Sale_BillablePrice\n       WHEN 'Re-occurring Sale'      THEN tbl_pricecode_item.Sale_BillablePrice\n       ELSE NULL END\nWHERE tbl_orderdetails.SaleRentType IN ('Medicare Oxygen Rental', 'Monthly Rental', 'Capped Rental', 'Parental Capped Rental', 'Rent to Purchase', 'One Time Sale', 'Re-occurring Sale')\n--  AND tbl_order.State = 'New'\n  AND tbl_orderdetails.State = 'New'\n  AND tbl_pricecode_item.PriceCodeID = :pricecodeid\n", guid);
                            command.Parameters.Add("pricecodeid", MySqlType.Int).Value = priceCodeID;
                            command.ExecuteNonQuery();
                        }
                    }
                    transaction.Commit();
                }
                catch (Exception exception)
                {
                    transaction.Rollback();
                    throw new Exception("Transaction was rolled back", exception);
                }
            }
        }

        private void tsbtnSave_Click(object sender, EventArgs e)
        {
            try
            {
                object selectedValue = this.tscmbPriceList.ComboBox.SelectedValue;
                if (selectedValue is int)
                {
                    SaveTable(this.F_Table, Globals.ConnectionString, (int) selectedValue, this.UpdateExistingOrders);
                    LoadTable(this.F_Table, Globals.ConnectionString, (int) selectedValue);
                    MessageBox.Show("Price level was successfully updated.", this.Text, MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
                }
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private void tsbtnUpdateExistingOrders_Click(object sender, EventArgs e)
        {
            try
            {
                this.UpdateExistingOrders = !this.UpdateExistingOrders;
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private void tsbtnUpdateList_Click(object sender, EventArgs e)
        {
            try
            {
                using (FormUpdateParameters parameters = new FormUpdateParameters())
                {
                    if (parameters.ShowDialog() == DialogResult.OK)
                    {
                        Prices columns = Prices.Sale_BillablePrice | Prices.Sale_AllowablePrice | Prices.Rent_BillablePrice | Prices.Rent_AllowablePrice;
                        this.grid.DataSource = null;
                        try
                        {
                            UpdateTable(this.F_Table, 1M + (parameters.Percent / 100M), columns);
                        }
                        finally
                        {
                            this.grid.DataSource = this.F_Table.DefaultView;
                        }
                    }
                }
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private void tscmbPriceList_SelectedIndexChanged(object sender, EventArgs e)
        {
            try
            {
                this.FillGrid(this.tscmbPriceList.ComboBox.SelectedValue);
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private static void UpdateTable(TablePriceList table, decimal multiplier, Prices columns)
        {
            if (table == null)
            {
                throw new ArgumentNullException("table");
            }
            foreach (DataRow row in table.Select("", "", DataViewRowState.CurrentRows))
            {
                switch ((columns & Prices.Rent_AllowablePrice))
                {
                    case ((columns & Prices.Rent_AllowablePrice) == Prices.Rent_AllowablePrice):
                    {
                        object obj2 = row[table.Col_Rent_AllowablePrice];
                        if (obj2 is decimal)
                        {
                            row[table.Col_Rent_AllowablePrice] = Math.Round((decimal) (multiplier * ((decimal) obj2)), 2, MidpointRounding.ToEven);
                        }
                        break;
                    }
                }
                if ((columns & Prices.Rent_BillablePrice) == Prices.Rent_BillablePrice)
                {
                    object obj3 = row[table.Col_Rent_BillablePrice];
                    if (obj3 is decimal)
                    {
                        row[table.Col_Rent_BillablePrice] = Math.Round((decimal) (multiplier * ((decimal) obj3)), 2, MidpointRounding.ToEven);
                    }
                }
                if ((columns & Prices.Sale_AllowablePrice) == Prices.Sale_AllowablePrice)
                {
                    object obj4 = row[table.Col_Sale_AllowablePrice];
                    if (obj4 is decimal)
                    {
                        row[table.Col_Sale_AllowablePrice] = Math.Round((decimal) (multiplier * ((decimal) obj4)), 2, MidpointRounding.ToEven);
                    }
                }
                if ((columns & Prices.Sale_BillablePrice) == Prices.Sale_BillablePrice)
                {
                    object obj5 = row[table.Col_Sale_BillablePrice];
                    if (obj5 is decimal)
                    {
                        row[table.Col_Sale_BillablePrice] = Math.Round((decimal) (multiplier * ((decimal) obj5)), 2, MidpointRounding.ToEven);
                    }
                }
            }
        }

        private bool UpdateExistingOrders
        {
            get => 
                this._updateExistingOrders;
            set
            {
                if (this._updateExistingOrders != value)
                {
                    this._updateExistingOrders = value;
                    if (this._updateExistingOrders)
                    {
                        this.tsbtnUpdateExistingOrders.Image = Resources.Checked;
                    }
                    else
                    {
                        this.tsbtnUpdateExistingOrders.Image = Resources.Unchecked;
                    }
                }
            }
        }

        private enum Prices
        {
            Rent_AllowablePrice = 1,
            Rent_BillablePrice = 2,
            Sale_AllowablePrice = 4,
            Sale_BillablePrice = 8
        }

        private class TablePriceList : DataTable
        {
            private DataColumn _col_BillingCode;
            private DataColumn _col_Rent_AllowablePrice;
            private DataColumn _col_Rent_BillablePrice;
            private DataColumn _col_Sale_AllowablePrice;
            private DataColumn _col_Sale_BillablePrice;

            public TablePriceList() : this("")
            {
            }

            public TablePriceList(string TableName) : base(TableName)
            {
                this.InitializeClass();
                this.Initialize();
            }

            public override DataTable Clone()
            {
                DataTable table1 = base.Clone();
                ((FormPriceListEditor.TablePriceList) table1).Initialize();
                return table1;
            }

            protected virtual void Initialize()
            {
                this._col_BillingCode = base.Columns["BillingCode"];
                this._col_Rent_AllowablePrice = base.Columns["Rent_AllowablePrice"];
                this._col_Rent_BillablePrice = base.Columns["Rent_BillablePrice"];
                this._col_Sale_AllowablePrice = base.Columns["Sale_AllowablePrice"];
                this._col_Sale_BillablePrice = base.Columns["Sale_BillablePrice"];
            }

            protected virtual void InitializeClass()
            {
                this._col_BillingCode = base.Columns.Add("BillingCode", typeof(string));
                this._col_Rent_AllowablePrice = base.Columns.Add("Rent_AllowablePrice", typeof(decimal));
                this._col_Rent_BillablePrice = base.Columns.Add("Rent_BillablePrice", typeof(decimal));
                this._col_Sale_AllowablePrice = base.Columns.Add("Sale_AllowablePrice", typeof(decimal));
                this._col_Sale_BillablePrice = base.Columns.Add("Sale_BillablePrice", typeof(decimal));
            }

            public DataColumn Col_BillingCode =>
                this._col_BillingCode;

            public DataColumn Col_Rent_AllowablePrice =>
                this._col_Rent_AllowablePrice;

            public DataColumn Col_Rent_BillablePrice =>
                this._col_Rent_BillablePrice;

            public DataColumn Col_Sale_AllowablePrice =>
                this._col_Sale_AllowablePrice;

            public DataColumn Col_Sale_BillablePrice =>
                this._col_Sale_BillablePrice;
        }
    }
}


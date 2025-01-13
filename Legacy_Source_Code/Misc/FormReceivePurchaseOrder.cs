namespace DMEWorks.Misc
{
    using Devart.Data.MySql;
    using DMEWorks;
    using DMEWorks.Core;
    using DMEWorks.Forms;
    using System;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.Windows.Forms;

    public class FormReceivePurchaseOrder : DmeForm
    {
        private readonly int purchaseOrderID;
        private Snapshot prev;
        private const string CrLf = "\r\n";
        private IContainer components;
        private Panel panel1;
        private TextBox txtBarcode;
        private Label lblBarcode;
        private FilteredGrid filteredGrid1;
        private Timer timer1;
        private Button btnOK;
        private Button btnCancel;

        public FormReceivePurchaseOrder(int purchaseOrderID)
        {
            this.purchaseOrderID = purchaseOrderID;
            this.InitializeComponent();
            base.KeyPreview = true;
            base.ActiveControl = this.txtBarcode;
            this.InitializeGrid(this.filteredGrid1.Appearance);
        }

        private void appearance_DataError(object sender, GridDataErrorEventArgs e)
        {
            this.ShowException(e.Exception);
            e.ThrowException = false;
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            base.DialogResult = DialogResult.Cancel;
            base.Close();
        }

        private void btnOK_Click(object sender, EventArgs e)
        {
            try
            {
                this.SaveItems();
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
                return;
            }
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

        private void FormReceivePurchaseOrder_Activated(object sender, EventArgs e)
        {
            if (!this.txtBarcode.Focused)
            {
                this.txtBarcode.Focus();
            }
        }

        private void FormReceivePurchaseOrder_KeyPress(object sender, KeyPressEventArgs e)
        {
        }

        private void FormReceivePurchaseOrder_Load(object sender, EventArgs e)
        {
            try
            {
                this.LoadItems();
                this.timer1.Enabled = true;
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private DataRow GetRowByBarcode(string code)
        {
            TableDetails tableSource = this.filteredGrid1.GetTableSource<TableDetails>();
            if (tableSource != null)
            {
                foreach (DataRow row in tableSource.Select())
                {
                    char[] trimChars = new char[] { ' ' };
                    string b = NullableConvert.ToString(row[tableSource.Col_Barcode]).Trim(trimChars);
                    if (string.Equals(code, b, StringComparison.InvariantCultureIgnoreCase))
                    {
                        return row;
                    }
                }
            }
            return null;
        }

        private void IncrementQuantity(DataRow row)
        {
            if (row != null)
            {
                TableDetails table = row.Table as TableDetails;
                if (table != null)
                {
                    try
                    {
                        row[table.Col_Quantity] = NullableConvert.ToInt32(row[table.Col_Quantity], 0) + 1;
                    }
                    catch (Exception exception)
                    {
                        this.ShowException(exception);
                    }
                }
            }
        }

        private void InitializeComponent()
        {
            this.components = new Container();
            this.panel1 = new Panel();
            this.btnOK = new Button();
            this.btnCancel = new Button();
            this.txtBarcode = new TextBox();
            this.lblBarcode = new Label();
            this.timer1 = new Timer(this.components);
            this.filteredGrid1 = new FilteredGrid();
            this.panel1.SuspendLayout();
            base.SuspendLayout();
            this.panel1.Controls.Add(this.btnOK);
            this.panel1.Controls.Add(this.btnCancel);
            this.panel1.Controls.Add(this.txtBarcode);
            this.panel1.Controls.Add(this.lblBarcode);
            this.panel1.Dock = DockStyle.Bottom;
            this.panel1.Location = new Point(0, 0x1a0);
            this.panel1.Name = "panel1";
            this.panel1.Size = new Size(0x278, 0x25);
            this.panel1.TabIndex = 3;
            this.btnOK.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.btnOK.Location = new Point(0x1d8, 8);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new Size(0x4b, 0x17);
            this.btnOK.TabIndex = 2;
            this.btnOK.Text = "OK";
            this.btnOK.UseVisualStyleBackColor = true;
            this.btnOK.Click += new EventHandler(this.btnOK_Click);
            this.btnCancel.Anchor = AnchorStyles.Right | AnchorStyles.Top;
            this.btnCancel.Location = new Point(0x228, 8);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new Size(0x4b, 0x17);
            this.btnCancel.TabIndex = 3;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new EventHandler(this.btnCancel_Click);
            this.txtBarcode.Location = new Point(0x48, 8);
            this.txtBarcode.Name = "txtBarcode";
            this.txtBarcode.Size = new Size(0xe0, 20);
            this.txtBarcode.TabIndex = 1;
            this.lblBarcode.Location = new Point(8, 8);
            this.lblBarcode.Name = "lblBarcode";
            this.lblBarcode.Size = new Size(0x38, 0x15);
            this.lblBarcode.TabIndex = 0;
            this.lblBarcode.Text = "Barcode :";
            this.lblBarcode.TextAlign = ContentAlignment.MiddleLeft;
            this.timer1.Tick += new EventHandler(this.timer1_Tick);
            this.filteredGrid1.Dock = DockStyle.Fill;
            this.filteredGrid1.Location = new Point(0, 0);
            this.filteredGrid1.Name = "filteredGrid1";
            this.filteredGrid1.Size = new Size(0x278, 0x1a0);
            this.filteredGrid1.TabIndex = 0;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.ClientSize = new Size(0x278, 0x1c5);
            base.Controls.Add(this.filteredGrid1);
            base.Controls.Add(this.panel1);
            base.Name = "FormReceivePurchaseOrder";
            this.Text = "Receive Purchase Order";
            base.TopMost = true;
            base.Activated += new EventHandler(this.FormReceivePurchaseOrder_Activated);
            base.Load += new EventHandler(this.FormReceivePurchaseOrder_Load);
            base.KeyPress += new KeyPressEventHandler(this.FormReceivePurchaseOrder_KeyPress);
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            base.ResumeLayout(false);
        }

        protected void InitializeGrid(FilteredGridAppearance appearance)
        {
            appearance.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.None;
            appearance.RowHeadersWidth = 30;
            appearance.RowTemplate.Height = 20;
            appearance.AutoGenerateColumns = false;
            appearance.AllowEdit = true;
            appearance.AllowNew = false;
            appearance.MultiSelect = false;
            appearance.Columns.Clear();
            appearance.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            appearance.EditMode = DataGridViewEditMode.EditOnEnter;
            appearance.ShowCellErrors = true;
            appearance.ShowRowErrors = true;
            appearance.AddTextColumn("Barcode", "Barcode", 80);
            appearance.AddTextColumn("ItemName", "Inventory Item", 400);
            appearance.DataError += new EventHandler<GridDataErrorEventArgs>(this.appearance_DataError);
            DataGridViewTextBoxColumn column1 = appearance.AddTextColumn("Quantity", "Quantity", 60);
            column1.DefaultCellStyle = appearance.IntegerStyle();
            column1.DefaultCellStyle.BackColor = Color.LightSteelBlue;
            column1.ReadOnly = false;
        }

        private void LoadItems()
        {
            TableDetails dataTable = new TableDetails();
            using (MySqlDataAdapter adapter = new MySqlDataAdapter("", Globals.ConnectionString))
            {
                adapter.SelectCommand.CommandText = "SELECT\r\n  pod.ID      as DetailsID\r\n, inv.ID      as ItemID\r\n, inv.Name    as ItemName\r\n, inv.Barcode as Barcode\r\n, 0           as Quantity\r\n, pod.Ordered - pod.Received as Remaining\r\nFROM tbl_purchaseorderdetails as pod\r\n     INNER JOIN tbl_inventoryitem as inv ON pod.InventoryItemID = inv.ID\r\nWHERE pod.PurchaseOrderID = :PurchaseOrderID\r\n  AND IFNULL(inv.Barcode, '') != ''\r\nORDER BY inv.Name\r\n";
                adapter.SelectCommand.Parameters.Add("PurchaseOrderID", MySqlType.Int).Value = this.purchaseOrderID;
                adapter.Fill(dataTable);
            }
            this.filteredGrid1.GridSource = dataTable.ToGridSource();
        }

        private void SaveItems()
        {
            TableDetails tableSource = this.filteredGrid1.GetTableSource<TableDetails>();
            if (tableSource != null)
            {
                using (MySqlConnection connection = new MySqlConnection(Globals.ConnectionString))
                {
                    connection.Open();
                    MySqlTransaction transaction = connection.BeginTransaction();
                    try
                    {
                        using (MySqlCommand command = new MySqlCommand("", connection, transaction))
                        {
                            command.CommandText = "UPDATE tbl_purchaseorderdetails\r\nSET BackOrder = Ordered - Received - :Quantity\r\n  , Received = Received + :Quantity\r\n  , DateReceived = NOW()\r\nWHERE PurchaseOrderID = :PurchaseOrderID\r\n  AND ID = :DetailsID\r\n  AND 0 <= Ordered - Received - :Quantity\r\n  AND 0 < :Quantity\r\n";
                            command.Parameters.Add("PurchaseOrderID", MySqlType.Int).Value = this.purchaseOrderID;
                            command.Parameters.Add("DetailsID", MySqlType.Int);
                            command.Parameters.Add("Quantity", MySqlType.Int);
                            foreach (DataRow row in tableSource.Select("0 < Quantity"))
                            {
                                command.Parameters["DetailsID"].Value = row[tableSource.Col_DetailsID];
                                command.Parameters["Quantity"].Value = row[tableSource.Col_Quantity];
                                if (command.ExecuteNonQuery() == 0)
                                {
                                    throw new UserNotifyException("Value were not posted");
                                }
                            }
                        }
                        using (MySqlCommand command2 = new MySqlCommand("", connection, transaction))
                        {
                            command2.CommandText = $"CALL inventory_transaction_po_refresh({this.purchaseOrderID}, 'Ordered')";
                            command2.ExecuteNonQuery();
                            command2.CommandText = $"CALL inventory_transaction_po_refresh({this.purchaseOrderID}, 'Received')";
                            command2.ExecuteNonQuery();
                            command2.CommandText = $"CALL inventory_transaction_po_refresh({this.purchaseOrderID}, 'BackOrdered')";
                            command2.ExecuteNonQuery();
                            command2.CommandText = $"CALL inventory_po_refresh({this.purchaseOrderID})";
                            command2.ExecuteNonQuery();
                            command2.CommandText = $"CALL PurchaseOrder_UpdateTotals({this.purchaseOrderID})";
                            command2.ExecuteNonQuery();
                        }
                        transaction.Commit();
                    }
                    catch (Exception)
                    {
                        transaction.Rollback();
                        throw;
                    }
                }
            }
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            string str = (this.txtBarcode.Text ?? "").Trim();
            if (string.IsNullOrEmpty(str))
            {
                this.prev = null;
            }
            else if ((this.prev == null) || !string.Equals(str, this.prev.Text, StringComparison.InvariantCulture))
            {
                this.prev = new Snapshot(str);
            }
            else if (this.prev.Time < Snapshot.Now.AddMilliseconds(-750.0))
            {
                DataRow row = this.GetRowByBarcode(str);
                if (row != null)
                {
                    this.txtBarcode.Text = "";
                    this.txtBarcode.Focus();
                    this.prev = null;
                    this.IncrementQuantity(row);
                    this.filteredGrid1.SetCurrentRow(r => ReferenceEquals(r.GetDataRow(), row));
                }
            }
        }

        private class Snapshot
        {
            public readonly string Text;
            public readonly DateTime Time;

            public Snapshot(string text)
            {
                this.Text = text;
                this.Time = Now;
            }

            public static DateTime Now =>
                DateTime.Now;
        }

        public class TableDetails : DataTable
        {
            public DataColumn Col_DetailsID;
            public DataColumn Col_ItemID;
            public DataColumn Col_ItemName;
            public DataColumn Col_Barcode;
            public DataColumn Col_Quantity;
            public DataColumn Col_Remaining;

            public TableDetails()
            {
                this.CreateColumns();
                this.InitializeFields();
            }

            public TableDetails(string tableName) : base(tableName)
            {
                this.CreateColumns();
                this.InitializeFields();
            }

            public override DataTable Clone()
            {
                FormReceivePurchaseOrder.TableDetails details1 = (FormReceivePurchaseOrder.TableDetails) base.Clone();
                details1.InitializeFields();
                return details1;
            }

            private void CreateColumns()
            {
                base.Columns.Add("DetailsID", typeof(int)).ReadOnly = true;
                base.Columns.Add("ItemID", typeof(int)).ReadOnly = true;
                base.Columns.Add("ItemName", typeof(string)).ReadOnly = true;
                base.Columns.Add("Barcode", typeof(string)).ReadOnly = true;
                base.Columns.Add("Quantity", typeof(int)).ReadOnly = false;
                base.Columns.Add("Remaining", typeof(int)).ReadOnly = false;
            }

            private void InitializeFields()
            {
                this.Col_DetailsID = base.Columns["DetailsID"];
                this.Col_ItemID = base.Columns["ItemID"];
                this.Col_ItemName = base.Columns["ItemName"];
                this.Col_Barcode = base.Columns["Barcode"];
                this.Col_Quantity = base.Columns["Quantity"];
                this.Col_Remaining = base.Columns["Remaining"];
            }

            protected override void OnColumnChanging(DataColumnChangeEventArgs e)
            {
                if (ReferenceEquals(e.Column, this.Col_Quantity))
                {
                    int num = NullableConvert.ToInt32(e.ProposedValue, 0);
                    if (num < 0)
                    {
                        throw new UserNotifyException("Quantity cannot be negative");
                    }
                    int num2 = NullableConvert.ToInt32(e.Row[this.Col_Remaining], 0);
                    if (num2 < num)
                    {
                        throw new UserNotifyException("Quantity cannot be greater than remaining (" + num2.ToString() + ")");
                    }
                }
                base.OnColumnChanging(e);
            }
        }
    }
}


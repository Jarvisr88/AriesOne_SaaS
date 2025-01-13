namespace DMEWorks.PriceUtilities
{
    using Devart.Data.MySql;
    using DMEWorks;
    using DMEWorks.Csv;
    using DMEWorks.Forms;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Runtime.CompilerServices;
    using System.Text;
    using System.Windows.Forms;

    public class FormPriceUpdater : DmeForm
    {
        private static readonly CultureInfo _eng = CultureInfo.CreateSpecificCulture("en-US");
        private const int linesToSkip = 6;
        private IContainer components;
        private TextBox txtFileName;
        private Button btnChooseCVS;
        private ComboBox cmbColumnName;
        private Button btnUpdateDatabase;
        private Label label1;
        private Label label2;
        private ErrorProvider errorProvider;
        private Label lbSelect_price;
        private ComboBox cmbPriceList;
        private CheckBox chbUpdateExistingOrders;
        private Panel pnlOptions;
        private Panel pnlFileName;

        public FormPriceUpdater()
        {
            this.InitializeComponent();
        }

        private void btnChooseCVS_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog dialog = new OpenFileDialog())
            {
                dialog.Filter = "Text Files (*.txt, *.csv)|*.txt;*.csv|All Files (*.*)|*.*";
                dialog.Multiselect = false;
                if (File.Exists(this.txtFileName.Text))
                {
                    dialog.FileName = this.txtFileName.Text;
                }
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    dialog.FileName.Trim();
                    this.txtFileName.Text = dialog.FileName;
                }
            }
        }

        private void btnUpdateDatabase_Click(object sender, EventArgs e)
        {
            try
            {
                if (this.cmbColumnName.SelectedIndex < 0)
                {
                    this.errorProvider.SetError(this.cmbColumnName, "You must select state");
                }
                else
                {
                    this.errorProvider.SetError(this.cmbColumnName, "");
                }
                if (this.cmbPriceList.SelectedValue is int)
                {
                    this.errorProvider.SetError(this.cmbPriceList, "");
                }
                else
                {
                    this.errorProvider.SetError(this.cmbPriceList, "You must select price list");
                }
                StringBuilder builder = new StringBuilder("There are some errors in input data");
                if (0 >= Utilities.EnumerateErrors(this, this.errorProvider, builder))
                {
                    TablePrice table = ReadStatePrices(this.txtFileName.Text, this.cmbColumnName.Text);
                    Dictionary<string, string> dictionary = new Dictionary<string, string>(Math.Max(10, table.Rows.Count), StringComparer.InvariantCultureIgnoreCase);
                    int num2 = 0;
                    int count = table.Rows.Count;
                    while (num2 < count)
                    {
                        string str = table.Rows[num2][table.Col_BillingCode] as string;
                        if (str != null)
                        {
                            dictionary[str] = str;
                        }
                        num2++;
                    }
                    int selectedValue = (int) this.cmbPriceList.SelectedValue;
                    using (MySqlConnection connection = new MySqlConnection(Globals.ConnectionString))
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
  `rentprice` decimal(18,2) NOT NULL,
  `saleprice` decimal(18,2) NOT NULL)";
                                command.ExecuteNonQuery();
                                using (MySqlCommand command2 = new MySqlCommand("", connection, transaction))
                                {
                                    command2.CommandText = $"INSERT INTO `{guid}` (`BillingCode`, `rentprice`, `saleprice`) VALUES (:BillingCode, :RentPrice, :SalePrice)";
                                    MySqlParameter parameter = command2.Parameters.Add("BillingCode", MySqlType.VarChar, 50);
                                    MySqlParameter parameter2 = command2.Parameters.Add("RentPrice", MySqlType.Decimal);
                                    MySqlParameter parameter3 = command2.Parameters.Add("SalePrice", MySqlType.Decimal);
                                    DataView view = new DataView(table, "([Modifier2] = '') AND ([Modifier] NOT IN ('UE'))", "[BillingCode], [Modifier]", DataViewRowState.OriginalRows);
                                    DataView view2 = new DataView(table, "([Modifier2] = '') AND ([Modifier] NOT IN ('UE', 'RR', 'NU', ''))", "[BillingCode]", DataViewRowState.OriginalRows);
                                    object[] key = new object[2];
                                    foreach (string str2 in dictionary.Keys)
                                    {
                                        key[0] = str2;
                                        decimal num4 = 0M;
                                        decimal num5 = 0M;
                                        key[1] = "RR";
                                        DataRowView[] viewArray = view.FindRows(key);
                                        if (viewArray.Length != 0)
                                        {
                                            try
                                            {
                                                num4 = (decimal) viewArray[0].Row[table.Col_Price];
                                                num5 = 10M * num4;
                                            }
                                            catch
                                            {
                                            }
                                        }
                                        key[1] = "NU";
                                        viewArray = view.FindRows(key);
                                        if (viewArray.Length == 0)
                                        {
                                            key[1] = "";
                                            viewArray = view.FindRows(key);
                                            if (viewArray.Length == 0)
                                            {
                                                viewArray = view2.FindRows(str2);
                                            }
                                        }
                                        if (viewArray.Length != 0)
                                        {
                                            try
                                            {
                                                num5 = (decimal) viewArray[0].Row[table.Col_Price];
                                            }
                                            catch
                                            {
                                            }
                                        }
                                        if (0.01M <= Math.Abs(num5))
                                        {
                                            parameter.Value = str2;
                                            parameter2.Value = num4;
                                            parameter3.Value = num5;
                                            command2.ExecuteNonQuery();
                                        }
                                    }
                                }
                                command.Parameters.Clear();
                                command.CommandText = string.Format("UPDATE tbl_pricecode_item\n       INNER JOIN `{0}` ON tbl_pricecode_item.BillingCode = `{0}`.BillingCode\nSET tbl_pricecode_item.rent_allowableprice = `{0}`.rentprice,    tbl_pricecode_item.sale_allowableprice = `{0}`.saleprice\nWHERE tbl_pricecode_item.PriceCodeID = :pricecodeid\n", guid);
                                command.Parameters.Add("pricecodeid", MySqlType.Int).Value = selectedValue;
                                command.ExecuteNonQuery();
                                if (this.chbUpdateExistingOrders.Checked)
                                {
                                    command.Parameters.Clear();
                                    command.CommandText = string.Format("UPDATE tbl_orderdetails\n       INNER JOIN tbl_order ON tbl_orderdetails.OrderID = tbl_order.ID\n                           AND tbl_orderdetails.CustomerID = tbl_order.CustomerID\n       INNER JOIN tbl_pricecode_item ON tbl_orderdetails.InventoryItemID = tbl_pricecode_item.InventoryItemID\n                                    AND tbl_orderdetails.PriceCodeID = tbl_pricecode_item.PriceCodeID\n       INNER JOIN `{0}` ON tbl_pricecode_item.BillingCode = `{0}`.BillingCode\nSET tbl_orderdetails.AllowablePrice=\n  CASE tbl_orderdetails.SaleRentType\n       WHEN 'Medicare Oxygen Rental' THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Monthly Rental'         THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Capped Rental'          THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Parental Capped Rental' THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'Rent to Purchase'       THEN tbl_pricecode_item.Rent_AllowablePrice\n       WHEN 'One Time Sale'          THEN tbl_pricecode_item.Sale_AllowablePrice\n       WHEN 'Re-occurring Sale'      THEN tbl_pricecode_item.Sale_AllowablePrice\n       ELSE NULL END\nWHERE tbl_orderdetails.SaleRentType IN ('Medicare Oxygen Rental', 'Monthly Rental', 'Capped Rental', 'Parental Capped Rental', 'Rent to Purchase', 'One Time Sale', 'Re-occurring Sale')\n--  AND tbl_order.State = 'New'\n  AND tbl_orderdetails.State = 'New'\n  AND tbl_pricecode_item.PriceCodeID = :pricecodeid\n", guid);
                                    command.Parameters.Add("pricecodeid", MySqlType.Int).Value = selectedValue;
                                    command.ExecuteNonQuery();
                                }
                            }
                            transaction.Commit();
                            goto TR_000E;
                        }
                        catch (Exception exception)
                        {
                            transaction.Rollback();
                            throw new Exception("Transaction was rolled back", exception);
                        }
                    }
                }
                MessageBox.Show(builder.ToString(), "Warning", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                return;
            TR_000E:
                MessageBox.Show("Price level was successfully updated.", "Update Orders", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
                base.Close();
            }
            catch (Exception exception2)
            {
                this.ShowException(exception2);
            }
        }

        private void cmbPriceList_SelectedIndexChanged(object sender, EventArgs e)
        {
            if ((this.errorProvider.GetError(this.cmbPriceList) != "") && (0 < this.cmbPriceList.SelectedIndex))
            {
                this.errorProvider.SetError(this.cmbPriceList, "");
            }
        }

        private void cmbState_SelectedIndexChanged(object sender, EventArgs e)
        {
            if ((this.errorProvider.GetError(this.cmbColumnName) != "") && (0 < this.cmbColumnName.SelectedIndex))
            {
                this.errorProvider.SetError(this.cmbColumnName, "");
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

        private void Form1_Load(object sender, EventArgs e)
        {
            DataTable dataTable = new DataTable("tbl_pricecode");
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

        private static string[] GetColumns(string fileName)
        {
            string[] strArray2;
            using (StreamReader reader = new StreamReader(fileName))
            {
                int num = 1;
                while (true)
                {
                    if (num > 6)
                    {
                        using (IDataReader reader2 = new CsvReader(reader, true))
                        {
                            string[] strArray = new string[reader2.FieldCount];
                            int index = 0;
                            while (true)
                            {
                                if (index >= reader2.FieldCount)
                                {
                                    strArray2 = strArray;
                                    break;
                                }
                                strArray[index] = reader2.GetName(index);
                                index++;
                            }
                        }
                        break;
                    }
                    reader.ReadLine();
                    num++;
                }
            }
            return strArray2;
        }

        private void InitializeComponent()
        {
            this.components = new Container();
            this.txtFileName = new TextBox();
            this.btnChooseCVS = new Button();
            this.cmbColumnName = new ComboBox();
            this.btnUpdateDatabase = new Button();
            this.label1 = new Label();
            this.label2 = new Label();
            this.errorProvider = new ErrorProvider(this.components);
            this.lbSelect_price = new Label();
            this.cmbPriceList = new ComboBox();
            this.chbUpdateExistingOrders = new CheckBox();
            this.pnlOptions = new Panel();
            this.pnlFileName = new Panel();
            ((ISupportInitialize) this.errorProvider).BeginInit();
            this.pnlOptions.SuspendLayout();
            this.pnlFileName.SuspendLayout();
            base.SuspendLayout();
            this.errorProvider.SetIconAlignment(this.txtFileName, ErrorIconAlignment.MiddleLeft);
            this.errorProvider.SetIconPadding(this.txtFileName, -16);
            this.txtFileName.Location = new Point(8, 0x20);
            this.txtFileName.Name = "txtFileName";
            this.txtFileName.Size = new Size(0x110, 20);
            this.txtFileName.TabIndex = 1;
            this.txtFileName.TextChanged += new EventHandler(this.txtFileName_TextChanged);
            this.btnChooseCVS.Location = new Point(280, 0x20);
            this.btnChooseCVS.Name = "btnChooseCVS";
            this.btnChooseCVS.Size = new Size(0x38, 20);
            this.btnChooseCVS.TabIndex = 2;
            this.btnChooseCVS.Text = "Browse";
            this.btnChooseCVS.UseVisualStyleBackColor = true;
            this.btnChooseCVS.Click += new EventHandler(this.btnChooseCVS_Click);
            this.cmbColumnName.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbColumnName.FormattingEnabled = true;
            this.errorProvider.SetIconAlignment(this.cmbColumnName, ErrorIconAlignment.MiddleLeft);
            this.errorProvider.SetIconPadding(this.cmbColumnName, -16);
            this.cmbColumnName.Location = new Point(8, 0x20);
            this.cmbColumnName.Name = "cmbState";
            this.cmbColumnName.Size = new Size(0x55, 0x15);
            this.cmbColumnName.TabIndex = 1;
            this.cmbColumnName.SelectedIndexChanged += new EventHandler(this.cmbState_SelectedIndexChanged);
            this.btnUpdateDatabase.Location = new Point(0xd8, 0x49);
            this.btnUpdateDatabase.Name = "btnUpdateDatabase";
            this.btnUpdateDatabase.Size = new Size(0x67, 0x17);
            this.btnUpdateDatabase.TabIndex = 5;
            this.btnUpdateDatabase.Text = "Update Database";
            this.btnUpdateDatabase.UseVisualStyleBackColor = true;
            this.btnUpdateDatabase.Click += new EventHandler(this.btnUpdateDatabase_Click);
            this.label1.Location = new Point(8, 8);
            this.label1.Name = "label1";
            this.label1.Size = new Size(0x55, 0x15);
            this.label1.TabIndex = 0;
            this.label1.Text = "State";
            this.label1.TextAlign = ContentAlignment.BottomLeft;
            this.label2.Location = new Point(8, 8);
            this.label2.Name = "label2";
            this.label2.Size = new Size(0x112, 0x15);
            this.label2.TabIndex = 0;
            this.label2.Text = "Path to the CSV file";
            this.label2.TextAlign = ContentAlignment.BottomLeft;
            this.errorProvider.ContainerControl = this;
            this.lbSelect_price.Location = new Point(0x70, 8);
            this.lbSelect_price.Name = "lbSelect_price";
            this.lbSelect_price.Size = new Size(170, 0x15);
            this.lbSelect_price.TabIndex = 2;
            this.lbSelect_price.Text = "Price list";
            this.lbSelect_price.TextAlign = ContentAlignment.BottomLeft;
            this.cmbPriceList.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbPriceList.Location = new Point(0x70, 0x20);
            this.cmbPriceList.Name = "cmbPriceList";
            this.cmbPriceList.Size = new Size(170, 0x15);
            this.cmbPriceList.TabIndex = 3;
            this.cmbPriceList.SelectedIndexChanged += new EventHandler(this.cmbPriceList_SelectedIndexChanged);
            this.chbUpdateExistingOrders.Location = new Point(8, 0x49);
            this.chbUpdateExistingOrders.Name = "chbUpdateExistingOrders";
            this.chbUpdateExistingOrders.Size = new Size(0x8e, 0x15);
            this.chbUpdateExistingOrders.TabIndex = 4;
            this.chbUpdateExistingOrders.Text = "Update existing orders";
            this.chbUpdateExistingOrders.UseVisualStyleBackColor = true;
            this.pnlOptions.Controls.Add(this.label1);
            this.pnlOptions.Controls.Add(this.cmbColumnName);
            this.pnlOptions.Controls.Add(this.chbUpdateExistingOrders);
            this.pnlOptions.Controls.Add(this.btnUpdateDatabase);
            this.pnlOptions.Controls.Add(this.lbSelect_price);
            this.pnlOptions.Controls.Add(this.cmbPriceList);
            this.pnlOptions.Dock = DockStyle.Fill;
            this.pnlOptions.Location = new Point(0, 0x38);
            this.pnlOptions.Name = "pnlOptions";
            this.pnlOptions.Size = new Size(0x157, 0x6c);
            this.pnlOptions.TabIndex = 1;
            this.pnlOptions.Visible = false;
            this.pnlFileName.Controls.Add(this.txtFileName);
            this.pnlFileName.Controls.Add(this.btnChooseCVS);
            this.pnlFileName.Controls.Add(this.label2);
            this.pnlFileName.Dock = DockStyle.Top;
            this.pnlFileName.Location = new Point(0, 0);
            this.pnlFileName.Name = "pnlFileName";
            this.pnlFileName.Size = new Size(0x157, 0x38);
            this.pnlFileName.TabIndex = 0;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.ClientSize = new Size(0x157, 0xa4);
            base.Controls.Add(this.pnlOptions);
            base.Controls.Add(this.pnlFileName);
            base.FormBorderStyle = FormBorderStyle.FixedSingle;
            base.MaximizeBox = false;
            this.MinimumSize = new Size(0, 200);
            base.Name = "FormPriceUpdater";
            base.ShowIcon = false;
            base.StartPosition = FormStartPosition.CenterScreen;
            this.Text = "Update Price List";
            base.Load += new EventHandler(this.Form1_Load);
            ((ISupportInitialize) this.errorProvider).EndInit();
            this.pnlOptions.ResumeLayout(false);
            this.pnlFileName.ResumeLayout(false);
            this.pnlFileName.PerformLayout();
            base.ResumeLayout(false);
        }

        private static TablePrice ReadStatePrices(string fileName, string columnName)
        {
            TablePrice price2;
            using (StreamReader reader = new StreamReader(fileName))
            {
                int num = 1;
                while (true)
                {
                    if (num > 6)
                    {
                        using (IDataReader reader2 = new CsvReader(reader, true))
                        {
                            int num5;
                            int ordinal = reader2.GetOrdinal("HCPCS");
                            int i = reader2.GetOrdinal("Mod");
                            int num4 = reader2.GetOrdinal("Mod2");
                            try
                            {
                                num5 = reader2.GetOrdinal(columnName);
                            }
                            catch (Exception exception)
                            {
                                throw new UserNotifyException("File does not contain column '" + columnName + "'", exception);
                            }
                            TablePrice price = new TablePrice("tbl_price");
                            while (true)
                            {
                                decimal num6;
                                if (!reader2.Read())
                                {
                                    price2 = price;
                                    break;
                                }
                                string s = reader2.GetString(num5);
                                if ((s != null) && ((s.Length != 0) && decimal.TryParse(s, NumberStyles.Currency, _eng, out num6)))
                                {
                                    DataRow row = price.NewRow();
                                    string text1 = reader2.GetString(ordinal);
                                    string text4 = text1;
                                    if (text1 == null)
                                    {
                                        string local1 = text1;
                                        text4 = string.Empty;
                                    }
                                    row[price.Col_BillingCode] = text4;
                                    string text2 = reader2.GetString(i);
                                    string text5 = text2;
                                    if (text2 == null)
                                    {
                                        string local2 = text2;
                                        text5 = string.Empty;
                                    }
                                    row[price.Col_Modifier] = text5;
                                    string text3 = reader2.GetString(num4);
                                    string text6 = text3;
                                    if (text3 == null)
                                    {
                                        string local3 = text3;
                                        text6 = string.Empty;
                                    }
                                    row[price.Col_Modifier2] = text6;
                                    row[price.Col_Price] = num6;
                                    price.Rows.Add(row);
                                    row.AcceptChanges();
                                }
                            }
                        }
                        break;
                    }
                    reader.ReadLine();
                    num++;
                }
            }
            return price2;
        }

        private void txtFileName_TextChanged(object sender, EventArgs e)
        {
            string text = this.txtFileName.Text;
            bool flag = File.Exists(text);
            this.pnlOptions.Visible = flag;
            if (flag)
            {
                string[] textArray1 = new string[0x35];
                textArray1[0] = "AL";
                textArray1[1] = "AR";
                textArray1[2] = "AZ";
                textArray1[3] = "CA";
                textArray1[4] = "CO";
                textArray1[5] = "CT";
                textArray1[6] = "DC";
                textArray1[7] = "DE";
                textArray1[8] = "FL";
                textArray1[9] = "GA";
                textArray1[10] = "IA";
                textArray1[11] = "ID";
                textArray1[12] = "IL";
                textArray1[13] = "IN";
                textArray1[14] = "KS";
                textArray1[15] = "KY";
                textArray1[0x10] = "LA";
                textArray1[0x11] = "MA";
                textArray1[0x12] = "MD";
                textArray1[0x13] = "ME";
                textArray1[20] = "MI";
                textArray1[0x15] = "MN";
                textArray1[0x16] = "MO";
                textArray1[0x17] = "MS";
                textArray1[0x18] = "MT";
                textArray1[0x19] = "NC";
                textArray1[0x1a] = "ND";
                textArray1[0x1b] = "NE";
                textArray1[0x1c] = "NH";
                textArray1[0x1d] = "NJ";
                textArray1[30] = "NM";
                textArray1[0x1f] = "NV";
                textArray1[0x20] = "NY";
                textArray1[0x21] = "OH";
                textArray1[0x22] = "OK";
                textArray1[0x23] = "OR";
                textArray1[0x24] = "PA";
                textArray1[0x25] = "RI";
                textArray1[0x26] = "SC";
                textArray1[0x27] = "SD";
                textArray1[40] = "TN";
                textArray1[0x29] = "TX";
                textArray1[0x2a] = "UT";
                textArray1[0x2b] = "VA";
                textArray1[0x2c] = "VT";
                textArray1[0x2d] = "WA";
                textArray1[0x2e] = "WI";
                textArray1[0x2f] = "WV";
                textArray1[0x30] = "WY";
                textArray1[0x31] = "AK";
                textArray1[50] = "HI";
                textArray1[0x33] = "PR";
                textArray1[0x34] = "VI";
                string[] source = textArray1;
                List<string> list = new List<string>();
                string[] columns = GetColumns(text);
                int index = 0;
                while (true)
                {
                    if (index >= columns.Length)
                    {
                        list.Sort(StringComparer.OrdinalIgnoreCase);
                        this.cmbColumnName.BeginUpdate();
                        try
                        {
                            this.cmbColumnName.Items.Clear();
                            this.cmbColumnName.Items.AddRange(list.ToArray());
                        }
                        finally
                        {
                            this.cmbColumnName.EndUpdate();
                        }
                        break;
                    }
                    string column = columns[index];
                    if (source.Any<string>(st => (column != st) ? (!column.Equals(st, StringComparison.OrdinalIgnoreCase) ? ((column.Length > st.Length) ? ((column[st.Length] == ' ') ? column.StartsWith(st, StringComparison.OrdinalIgnoreCase) : false) : false) : true) : true))
                    {
                        list.Add(column);
                    }
                    index++;
                }
            }
        }

        private class Entry
        {
            public string BillingCode { get; set; }

            public string Modifier { get; set; }

            public string Modifier2 { get; set; }

            public decimal Price { get; set; }
        }

        private class TablePrice : DataTable
        {
            public DataColumn Col_BillingCode;
            public DataColumn Col_Modifier;
            public DataColumn Col_Modifier2;
            public DataColumn Col_Price;

            public TablePrice() : this("")
            {
            }

            public TablePrice(string TableName) : base(TableName)
            {
                this.InitializeClass();
                this.Initialize();
            }

            public override DataTable Clone()
            {
                DataTable table1 = base.Clone();
                ((FormPriceUpdater.TablePrice) table1).Initialize();
                return table1;
            }

            protected virtual void Initialize()
            {
                this.Col_BillingCode = base.Columns["BillingCode"];
                this.Col_Modifier = base.Columns["Modifier"];
                this.Col_Modifier2 = base.Columns["Modifier2"];
                this.Col_Price = base.Columns["Price"];
            }

            protected virtual void InitializeClass()
            {
                this.Col_BillingCode = base.Columns.Add("BillingCode", typeof(string));
                this.Col_Modifier = base.Columns.Add("Modifier", typeof(string));
                this.Col_Modifier2 = base.Columns.Add("Modifier2", typeof(string));
                this.Col_Price = base.Columns.Add("Price", typeof(decimal));
            }
        }
    }
}


namespace DMEWorks.Forms
{
    using Devart.Data.MySql;
    using DMEWorks.Data.MySql;
    using Microsoft.Win32;
    using System;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.Windows.Forms;

    public class FormLogin : DmeForm
    {
        private const string Key_LastLogin = @"Software\DME\LastLogin";
        private const string CrLf = "\r\n";
        private IContainer components;
        private ToolTip ToolTip1;
        private TextBox txtUserName;
        private TextBox txtPassword;
        private Label Label1;
        private Label lblUserName;
        private Label lblPassword;
        private Label lblServer;
        private Button btnOK;
        private Button btnCancel;
        private ComboBox cmbServer;
        private ListView lvRecords;
        private ColumnHeader chDatabase;
        private ColumnHeader chCompany;
        private Label Label2;

        public FormLogin()
        {
            this.InitializeComponent();
            this.cmbServer.Items.Clear();
            this.cmbServer.Items.AddRange(MySqlOdbcDsnInfo.GetDsns());
        }

        private void btnCancel_Click(object eventSender, EventArgs eventArgs)
        {
            base.DialogResult = DialogResult.Cancel;
        }

        private void btnOK_Click(object eventSender, EventArgs eventArgs)
        {
            if (this.cmbServer.Text.Trim() != string.Empty)
            {
                if (this.lvRecords.SelectedItems.Count > 0)
                {
                    base.DialogResult = DialogResult.OK;
                }
                else
                {
                    try
                    {
                        MySqlOdbcDsnInfo selectedItem = this.cmbServer.SelectedItem as MySqlOdbcDsnInfo;
                        if (selectedItem != null)
                        {
                            this.LoadDatabases(selectedItem.Server, this.txtUserName.Text, this.txtPassword.Text);
                            if (this.lvRecords.Items.Count > 0)
                            {
                                this.lvRecords.Items[0].Selected = true;
                            }
                            this.lvRecords.Focus();
                        }
                    }
                    catch (Exception exception)
                    {
                        this.ShowException(exception, "Load Databases");
                    }
                }
            }
        }

        private void cmbServer_TextChanged(object sender, EventArgs e)
        {
            this.lvRecords.Items.Clear();
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
            this.components = new Container();
            this.ToolTip1 = new ToolTip(this.components);
            this.txtUserName = new TextBox();
            this.btnOK = new Button();
            this.btnCancel = new Button();
            this.txtPassword = new TextBox();
            this.Label1 = new Label();
            this.lblUserName = new Label();
            this.lblPassword = new Label();
            this.lblServer = new Label();
            this.cmbServer = new ComboBox();
            this.lvRecords = new ListView();
            this.chDatabase = new ColumnHeader();
            this.chCompany = new ColumnHeader();
            this.Label2 = new Label();
            base.SuspendLayout();
            this.txtUserName.AcceptsReturn = true;
            this.txtUserName.BorderStyle = BorderStyle.FixedSingle;
            this.txtUserName.Location = new Point(80, 40);
            this.txtUserName.MaxLength = 0;
            this.txtUserName.Name = "txtUserName";
            this.txtUserName.Size = new Size(0xb0, 20);
            this.txtUserName.TabIndex = 2;
            this.txtUserName.TextChanged += new EventHandler(this.txtUserName_TextChanged);
            this.btnOK.FlatStyle = FlatStyle.Flat;
            this.btnOK.Location = new Point(0x110, 40);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new Size(0x4c, 0x1a);
            this.btnOK.TabIndex = 9;
            this.btnOK.Text = "OK";
            this.btnOK.Click += new EventHandler(this.btnOK_Click);
            this.btnCancel.DialogResult = DialogResult.Cancel;
            this.btnCancel.FlatStyle = FlatStyle.Flat;
            this.btnCancel.Location = new Point(0x110, 0x48);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new Size(0x4c, 0x1a);
            this.btnCancel.TabIndex = 10;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.Click += new EventHandler(this.btnCancel_Click);
            this.txtPassword.AcceptsReturn = true;
            this.txtPassword.BorderStyle = BorderStyle.FixedSingle;
            this.txtPassword.Location = new Point(80, 0x48);
            this.txtPassword.MaxLength = 0;
            this.txtPassword.Name = "txtPassword";
            this.txtPassword.PasswordChar = '*';
            this.txtPassword.Size = new Size(0xb0, 20);
            this.txtPassword.TabIndex = 4;
            this.txtPassword.TextChanged += new EventHandler(this.txtPassword_TextChanged);
            this.Label1.Location = new Point(8, 8);
            this.Label1.Name = "Label1";
            this.Label1.Size = new Size(0x100, 0x15);
            this.Label1.TabIndex = 0;
            this.Label1.Text = "Please Enter User Name and Password";
            this.Label1.TextAlign = ContentAlignment.MiddleLeft;
            this.lblUserName.Location = new Point(8, 40);
            this.lblUserName.Name = "lblUserName";
            this.lblUserName.Size = new Size(0x40, 0x15);
            this.lblUserName.TabIndex = 1;
            this.lblUserName.Text = "&User Name:";
            this.lblUserName.TextAlign = ContentAlignment.MiddleRight;
            this.lblPassword.Location = new Point(8, 0x48);
            this.lblPassword.Name = "lblPassword";
            this.lblPassword.Size = new Size(0x40, 0x15);
            this.lblPassword.TabIndex = 3;
            this.lblPassword.Text = "&Password:";
            this.lblPassword.TextAlign = ContentAlignment.MiddleRight;
            this.lblServer.Location = new Point(8, 0x68);
            this.lblServer.Name = "lblServer";
            this.lblServer.Size = new Size(0x40, 0x15);
            this.lblServer.TabIndex = 5;
            this.lblServer.Text = "&Server:";
            this.lblServer.TextAlign = ContentAlignment.MiddleRight;
            this.cmbServer.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbServer.FlatStyle = FlatStyle.Flat;
            this.cmbServer.Location = new Point(80, 0x68);
            this.cmbServer.Name = "cmbServer";
            this.cmbServer.Size = new Size(0xb0, 0x15);
            this.cmbServer.TabIndex = 6;
            this.cmbServer.TextChanged += new EventHandler(this.cmbServer_TextChanged);
            this.lvRecords.BorderStyle = BorderStyle.FixedSingle;
            ColumnHeader[] values = new ColumnHeader[] { this.chDatabase, this.chCompany };
            this.lvRecords.Columns.AddRange(values);
            this.lvRecords.Dock = DockStyle.Bottom;
            this.lvRecords.FullRowSelect = true;
            this.lvRecords.HideSelection = false;
            this.lvRecords.Location = new Point(4, 0x9b);
            this.lvRecords.MultiSelect = false;
            this.lvRecords.Name = "lvRecords";
            this.lvRecords.Size = new Size(0x15a, 0xc0);
            this.lvRecords.TabIndex = 8;
            this.lvRecords.UseCompatibleStateImageBehavior = false;
            this.lvRecords.View = View.Details;
            this.lvRecords.DoubleClick += new EventHandler(this.lvRecords_DoubleClick);
            this.chDatabase.Text = "Database Name";
            this.chDatabase.Width = 100;
            this.chCompany.Text = "Company Name";
            this.chCompany.Width = 220;
            this.Label2.Dock = DockStyle.Bottom;
            this.Label2.Location = new Point(4, 0x86);
            this.Label2.Name = "Label2";
            this.Label2.Size = new Size(0x15a, 0x15);
            this.Label2.TabIndex = 7;
            this.Label2.Text = "Please Select Database";
            this.Label2.TextAlign = ContentAlignment.MiddleLeft;
            base.AcceptButton = this.btnOK;
            this.AutoScaleBaseSize = new Size(5, 13);
            base.CancelButton = this.btnCancel;
            base.ClientSize = new Size(0x162, 0x15f);
            base.Controls.Add(this.Label2);
            base.Controls.Add(this.lvRecords);
            base.Controls.Add(this.cmbServer);
            base.Controls.Add(this.lblServer);
            base.Controls.Add(this.txtUserName);
            base.Controls.Add(this.btnOK);
            base.Controls.Add(this.btnCancel);
            base.Controls.Add(this.txtPassword);
            base.Controls.Add(this.Label1);
            base.Controls.Add(this.lblUserName);
            base.Controls.Add(this.lblPassword);
            base.FormBorderStyle = FormBorderStyle.FixedDialog;
            base.Location = new Point(0xbd, 0xe8);
            base.MaximizeBox = false;
            base.MinimizeBox = false;
            base.Name = "FormLogin";
            base.Padding = new Padding(4);
            base.ShowInTaskbar = false;
            base.StartPosition = FormStartPosition.CenterScreen;
            this.Text = "Login DME Works";
            base.ResumeLayout(false);
            base.PerformLayout();
        }

        private static DataTable LoadDatabaseList(MySqlServerInfo server, string login, string password)
        {
            if (server == null)
            {
                throw new ArgumentNullException("server");
            }
            DataTable dataTable = new DataTable();
            dataTable.Columns.Add("Database", typeof(string));
            dataTable.Columns.Add("CompanyName", typeof(string));
            dataTable.Columns.Add("LoginState", typeof(int));
            using (MySqlConnection connection = new MySqlConnection(server.GetConnectionString("DMEUser", "DMEPassword")))
            {
                connection.Open();
                using (MySqlDataAdapter adapter = new MySqlDataAdapter("SHOW DATABASES", connection))
                {
                    adapter.MissingSchemaAction = MissingSchemaAction.Error;
                    adapter.Fill(dataTable);
                }
                using (MySqlCommand command = new MySqlCommand("", connection))
                {
                    command.CommandType = CommandType.Text;
                    command.Parameters.Add("Login", MySqlType.VarChar, 50).Value = login;
                    command.Parameters.Add("Password", MySqlType.VarChar, 50).Value = password;
                    for (int i = 0; i < dataTable.Rows.Count; i++)
                    {
                        DataRow row = dataTable.Rows[i];
                        string identifier = Convert.ToString(row["Database"]);
                        command.CommandText = $"SELECT Count(*)
FROM {MySqlUtilities.QuoteIdentifier(identifier)}.tbl_user
WHERE (Login = :Login)
  AND (Password = :Password)
  AND (BINARY Password = BINARY :Password)";
                        try
                        {
                            row["LoginState"] = command.ExecuteScalar();
                        }
                        catch
                        {
                            row["LoginState"] = 0;
                        }
                        command.CommandText = $"SELECT Name FROM {MySqlUtilities.QuoteIdentifier(identifier)}.tbl_company WHERE (ID = 1)";
                        try
                        {
                            object obj2 = command.ExecuteScalar();
                            row["CompanyName"] = !(obj2 is string) ? "<<empty>>" : obj2;
                        }
                        catch (Exception exception)
                        {
                            row["CompanyName"] = exception.Message;
                            row["LoginState"] = 0;
                        }
                    }
                }
            }
            dataTable.AcceptChanges();
            return dataTable;
        }

        public void LoadDatabases(MySqlServerInfo server, string Login, string Password)
        {
            try
            {
                DataTable table = LoadDatabaseList(server, Login, Password);
                this.lvRecords.BeginUpdate();
                try
                {
                    this.lvRecords.Items.Clear();
                    foreach (DataRow row in table.Select("LoginState > 0"))
                    {
                        string[] items = new string[] { Convert.ToString(row["Database"]), Convert.ToString(row["CompanyName"]) };
                        this.lvRecords.Items.Add(new ListViewItem(items));
                    }
                }
                finally
                {
                    this.lvRecords.EndUpdate();
                }
            }
            catch (MySqlException exception)
            {
                this.ShowException(new UserNotifyException("Cannot connect to the server", exception));
            }
            catch (Exception exception2)
            {
                this.ShowException(exception2);
            }
        }

        public void LoadLastLoginInfo()
        {
            using (RegistryKey key = Registry.CurrentUser.CreateSubKey(@"Software\DME\LastLogin"))
            {
                if (key != null)
                {
                    this.txtUserName.Text = Convert.ToString(key.GetValue("UserName", ""));
                    string b = Convert.ToString(key.GetValue("Database", ""));
                    for (int i = 0; i < this.cmbServer.Items.Count; i++)
                    {
                        MySqlOdbcDsnInfo info = this.cmbServer.Items[i] as MySqlOdbcDsnInfo;
                        if ((info != null) && string.Equals(info.DsnName, b, StringComparison.OrdinalIgnoreCase))
                        {
                            this.cmbServer.SelectedIndex = i;
                            break;
                        }
                    }
                }
            }
        }

        private void lvRecords_DoubleClick(object sender, EventArgs e)
        {
            this.btnOK_Click(sender, e);
        }

        public void SaveLastLoginInfo()
        {
            RegistryKey key = Registry.CurrentUser.CreateSubKey(@"Software\DME\LastLogin");
            try
            {
                key.SetValue("UserName", this.UserName);
                MySqlOdbcDsnInfo dsnInfo = this.DsnInfo;
                key.SetValue("Database", (dsnInfo != null) ? dsnInfo.DsnName : string.Empty);
            }
            finally
            {
                key.Close();
            }
        }

        private void txtPassword_TextChanged(object sender, EventArgs e)
        {
            this.lvRecords.Items.Clear();
        }

        private void txtUserName_TextChanged(object sender, EventArgs e)
        {
            this.lvRecords.Items.Clear();
        }

        public string UserName =>
            this.txtUserName.Text;

        public string Password =>
            this.txtPassword.Text;

        public MySqlOdbcDsnInfo DsnInfo =>
            this.cmbServer.SelectedItem as MySqlOdbcDsnInfo;

        public string Database =>
            (this.lvRecords.SelectedItems.Count > 0) ? this.lvRecords.SelectedItems[0].Text : string.Empty;
    }
}


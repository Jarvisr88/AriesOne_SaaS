namespace DMEWorks.Misc
{
    using ActiproSoftware.Wizard;
    using Devart.Data.MySql;
    using DMEWorks;
    using DMEWorks.Core;
    using DMEWorks.Data.MySql;
    using DMEWorks.Forms;
    using Infragistics.Win.UltraWinEditors;
    using System;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.IO;
    using System.Linq;
    using System.Runtime.CompilerServices;
    using System.Windows.Forms;

    public class DialogDeposit : DmeForm
    {
        protected const string CrLf = "\r\n";
        private readonly BaseStage stageWelcome;
        private readonly BaseStage stageCustomer;
        private readonly BaseStage stageDeposit;
        private readonly BaseStage stageAmounts;
        private readonly BaseStage stageReview;
        private readonly BaseStage stageResult;
        private TableDetails details;
        private int? m_customerID;
        private int? m_orderID;
        private bool m_depositExists;
        private IContainer components;
        private ActiproSoftware.Wizard.Wizard wizard;
        private WizardPage wpAmounts;
        private WizardPage wpDeposit;
        private FilteredGrid Grid;
        private WizardWelcomePage wpWelcome;
        private Label label3;
        private Label label2;
        private Label label1;
        private WizardPage wpResult;
        private WizardPage wpCustomer;
        private Label lblCustomer;
        private Label lblOrder;
        private Label lblResult;
        private StatusStrip StatusStrip1;
        private ToolStripStatusLabel tsslInvoiceTotal;
        private ToolStripStatusLabel tsslDepositAmount;
        private ToolStripStatusLabel tsslRemainingAmount;
        private NumericBox nmbDepositAmount;
        private Label lblDepositAmount;
        private UltraDateTimeEditor dtpDepositDate;
        private Label lblDepositDate;
        private TextBox txtDepositNotes;
        private Label lblDepositNotes;
        private ComboBox cmbPaymentMethod;
        private Label lblPaymentMethod;
        private Label lblInvoiceTotal;
        private WizardPage wpSummary;
        private TextBox txtSummary;
        private Label txtInvoiceTotal;
        private Label txtOrder;
        private Label txtCustomer;

        public DialogDeposit()
        {
            this.stageWelcome = new StageWelcome(this);
            this.stageCustomer = new StageCustomer(this);
            this.stageDeposit = new StageDeposit(this);
            this.stageAmounts = new StageAmounts(this);
            this.stageReview = new StageSummary(this);
            this.stageResult = new StageResult(this);
            this.details = new TableDetails();
            this.InitializeComponent();
            this.InitializeGrid(this.Grid.Appearance);
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private TableDetails GetTable()
        {
            this.details.AcceptChanges();
            Func<DataRow, bool> predicate = <>c.<>9__19_0;
            if (<>c.<>9__19_0 == null)
            {
                Func<DataRow, bool> local1 = <>c.<>9__19_0;
                predicate = <>c.<>9__19_0 = r => r.HasErrors;
            }
            if (0 < this.details.Select().Count<DataRow>(predicate))
            {
                throw new UserNotifyException("Please fix all errors");
            }
            TableDetails details = this.details;
            double totalEntered = details.GetTotalEntered();
            if (0.01 <= Math.Abs((double) (this.nmbDepositAmount.AsDouble.GetValueOrDefault(0.0) - totalEntered)))
            {
                throw new UserNotifyException("Please split entire amount among line items");
            }
            return details;
        }

        private void InitializeComponent()
        {
            WindowsClassicWizardRenderer renderer = new WindowsClassicWizardRenderer();
            this.wizard = new ActiproSoftware.Wizard.Wizard();
            this.wpWelcome = new WizardWelcomePage();
            this.label3 = new Label();
            this.label2 = new Label();
            this.label1 = new Label();
            this.wpCustomer = new WizardPage();
            this.txtInvoiceTotal = new Label();
            this.txtOrder = new Label();
            this.txtCustomer = new Label();
            this.lblInvoiceTotal = new Label();
            this.lblOrder = new Label();
            this.lblCustomer = new Label();
            this.wpDeposit = new WizardPage();
            this.txtDepositNotes = new TextBox();
            this.lblDepositNotes = new Label();
            this.cmbPaymentMethod = new ComboBox();
            this.lblPaymentMethod = new Label();
            this.nmbDepositAmount = new NumericBox();
            this.lblDepositAmount = new Label();
            this.dtpDepositDate = new UltraDateTimeEditor();
            this.lblDepositDate = new Label();
            this.wpAmounts = new WizardPage();
            this.Grid = new FilteredGrid();
            this.StatusStrip1 = new StatusStrip();
            this.tsslInvoiceTotal = new ToolStripStatusLabel();
            this.tsslDepositAmount = new ToolStripStatusLabel();
            this.tsslRemainingAmount = new ToolStripStatusLabel();
            this.wpSummary = new WizardPage();
            this.txtSummary = new TextBox();
            this.wpResult = new WizardPage();
            this.lblResult = new Label();
            ((ISupportInitialize) this.wizard).BeginInit();
            this.wpWelcome.SuspendLayout();
            this.wpCustomer.SuspendLayout();
            this.wpDeposit.SuspendLayout();
            this.wpAmounts.SuspendLayout();
            this.StatusStrip1.SuspendLayout();
            this.wpSummary.SuspendLayout();
            this.wpResult.SuspendLayout();
            base.SuspendLayout();
            this.wizard.Dock = DockStyle.Fill;
            this.wizard.Location = new Point(0, 0);
            this.wizard.Name = "wizard";
            WizardPage[] pages = new WizardPage[] { this.wpWelcome, this.wpCustomer, this.wpDeposit, this.wpAmounts, this.wpSummary, this.wpResult };
            this.wizard.Pages.AddRange(pages);
            this.wizard.Renderer = renderer;
            this.wizard.Size = new Size(0x1fd, 0x169);
            this.wizard.TabIndex = 0;
            this.wizard.Text = "wizard1";
            this.wizard.BackButtonClick += new WizardPageCancelEventHandler(this.Wizard_BackButtonClick);
            this.wizard.CancelButtonClick += new EventHandler(this.Wizard_CancelButtonClick);
            this.wizard.FinishButtonClick += new EventHandler(this.Wizard_FinishButtonClick);
            this.wizard.NextButtonClick += new WizardPageCancelEventHandler(this.Wizard_NextButtonClick);
            this.wpWelcome.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Bottom | AnchorStyles.Top;
            this.wpWelcome.BackColor = SystemColors.Window;
            this.wpWelcome.Controls.Add(this.label3);
            this.wpWelcome.Controls.Add(this.label2);
            this.wpWelcome.Controls.Add(this.label1);
            this.wpWelcome.HelpButtonVisible = false;
            this.wpWelcome.IsInteriorPage = false;
            this.wpWelcome.Location = new Point(0, 0);
            this.wpWelcome.Name = "wpWelcome";
            this.wpWelcome.PageCaption = "";
            this.wpWelcome.PageDescription = "";
            this.wpWelcome.Size = new Size(0x1fd, 0x142);
            this.wpWelcome.TabIndex = 0;
            this.label3.Anchor = AnchorStyles.Left | AnchorStyles.Bottom;
            this.label3.AutoSize = true;
            this.label3.Location = new Point(0xb2, 0x126);
            this.label3.Name = "label3";
            this.label3.Size = new Size(120, 13);
            this.label3.TabIndex = 2;
            this.label3.Text = "To continue, click Next.";
            this.label2.Location = new Point(0xb2, 0x45);
            this.label2.Name = "label2";
            this.label2.Size = new Size(0x13c, 0xf4);
            this.label2.TabIndex = 1;
            this.label2.Text = "It will guide you through making deposit";
            this.label1.Font = new Font("Verdana", 12f, FontStyle.Bold);
            this.label1.Location = new Point(0xb0, 13);
            this.label1.Name = "label1";
            this.label1.Size = new Size(0x135, 0x37);
            this.label1.TabIndex = 0;
            this.label1.Text = "Welcome to the Deposit Wizard";
            this.wpCustomer.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Bottom | AnchorStyles.Top;
            this.wpCustomer.Controls.Add(this.txtInvoiceTotal);
            this.wpCustomer.Controls.Add(this.txtOrder);
            this.wpCustomer.Controls.Add(this.txtCustomer);
            this.wpCustomer.Controls.Add(this.lblInvoiceTotal);
            this.wpCustomer.Controls.Add(this.lblOrder);
            this.wpCustomer.Controls.Add(this.lblCustomer);
            this.wpCustomer.HelpButtonVisible = false;
            this.wpCustomer.Location = new Point(0x10, 0x4c);
            this.wpCustomer.Name = "wpCustomer";
            this.wpCustomer.PageCaption = "Customer / Order";
            this.wpCustomer.PageDescription = "";
            this.wpCustomer.Size = new Size(0x1dd, 230);
            this.wpCustomer.TabIndex = 1;
            this.wpCustomer.Text = "wizardPage1";
            this.txtInvoiceTotal.Location = new Point(0x58, 0x48);
            this.txtInvoiceTotal.Name = "txtInvoiceTotal";
            this.txtInvoiceTotal.Size = new Size(0x178, 0x15);
            this.txtInvoiceTotal.TabIndex = 5;
            this.txtInvoiceTotal.Text = "$0.00";
            this.txtInvoiceTotal.TextAlign = ContentAlignment.MiddleLeft;
            this.txtOrder.Location = new Point(0x58, 40);
            this.txtOrder.Name = "txtOrder";
            this.txtOrder.Size = new Size(0x178, 0x15);
            this.txtOrder.TabIndex = 3;
            this.txtOrder.Text = "###";
            this.txtOrder.TextAlign = ContentAlignment.MiddleLeft;
            this.txtCustomer.Location = new Point(0x58, 8);
            this.txtCustomer.Name = "txtCustomer";
            this.txtCustomer.Size = new Size(0x178, 0x15);
            this.txtCustomer.TabIndex = 1;
            this.txtCustomer.Text = "Last Name, First Name";
            this.txtCustomer.TextAlign = ContentAlignment.MiddleLeft;
            this.lblInvoiceTotal.Location = new Point(0x10, 0x48);
            this.lblInvoiceTotal.Name = "lblInvoiceTotal";
            this.lblInvoiceTotal.Size = new Size(0x40, 0x15);
            this.lblInvoiceTotal.TabIndex = 4;
            this.lblInvoiceTotal.Text = "Total";
            this.lblInvoiceTotal.TextAlign = ContentAlignment.MiddleLeft;
            this.lblOrder.Location = new Point(0x10, 40);
            this.lblOrder.Name = "lblOrder";
            this.lblOrder.Size = new Size(0x40, 0x15);
            this.lblOrder.TabIndex = 2;
            this.lblOrder.Text = "Order #";
            this.lblOrder.TextAlign = ContentAlignment.MiddleLeft;
            this.lblCustomer.Location = new Point(0x10, 8);
            this.lblCustomer.Name = "lblCustomer";
            this.lblCustomer.Size = new Size(0x40, 0x15);
            this.lblCustomer.TabIndex = 0;
            this.lblCustomer.Text = "Customer";
            this.lblCustomer.TextAlign = ContentAlignment.MiddleLeft;
            this.wpDeposit.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Bottom | AnchorStyles.Top;
            this.wpDeposit.Controls.Add(this.txtDepositNotes);
            this.wpDeposit.Controls.Add(this.lblDepositNotes);
            this.wpDeposit.Controls.Add(this.cmbPaymentMethod);
            this.wpDeposit.Controls.Add(this.lblPaymentMethod);
            this.wpDeposit.Controls.Add(this.nmbDepositAmount);
            this.wpDeposit.Controls.Add(this.lblDepositAmount);
            this.wpDeposit.Controls.Add(this.dtpDepositDate);
            this.wpDeposit.Controls.Add(this.lblDepositDate);
            this.wpDeposit.HelpButtonVisible = false;
            this.wpDeposit.Location = new Point(0x10, 0x4c);
            this.wpDeposit.Name = "wpDeposit";
            this.wpDeposit.PageCaption = "Deposit";
            this.wpDeposit.PageDescription = "Deposit information";
            this.wpDeposit.Size = new Size(0x1dd, 230);
            this.wpDeposit.TabIndex = 3;
            this.txtDepositNotes.Location = new Point(120, 80);
            this.txtDepositNotes.Multiline = true;
            this.txtDepositNotes.Name = "txtDepositNotes";
            this.txtDepositNotes.Size = new Size(0x158, 0x70);
            this.txtDepositNotes.TabIndex = 7;
            this.lblDepositNotes.Location = new Point(0x10, 80);
            this.lblDepositNotes.Name = "lblDepositNotes";
            this.lblDepositNotes.Size = new Size(0x60, 0x15);
            this.lblDepositNotes.TabIndex = 6;
            this.lblDepositNotes.Text = "Notes";
            this.lblDepositNotes.TextAlign = ContentAlignment.MiddleLeft;
            object[] items = new object[] { "Cash", "Check", "Credit card" };
            this.cmbPaymentMethod.Items.AddRange(items);
            this.cmbPaymentMethod.Location = new Point(120, 0x38);
            this.cmbPaymentMethod.Name = "cmbPaymentMethod";
            this.cmbPaymentMethod.Size = new Size(0x79, 0x15);
            this.cmbPaymentMethod.TabIndex = 5;
            this.lblPaymentMethod.Location = new Point(0x10, 0x38);
            this.lblPaymentMethod.Name = "lblPaymentMethod";
            this.lblPaymentMethod.Size = new Size(0x60, 0x15);
            this.lblPaymentMethod.TabIndex = 4;
            this.lblPaymentMethod.Text = "Payment Method";
            this.lblPaymentMethod.TextAlign = ContentAlignment.MiddleLeft;
            this.nmbDepositAmount.Location = new Point(120, 0x20);
            this.nmbDepositAmount.Name = "nmbDepositAmount";
            this.nmbDepositAmount.Size = new Size(120, 20);
            this.nmbDepositAmount.TabIndex = 3;
            this.lblDepositAmount.Location = new Point(0x10, 0x20);
            this.lblDepositAmount.Name = "lblDepositAmount";
            this.lblDepositAmount.Size = new Size(0x60, 0x15);
            this.lblDepositAmount.TabIndex = 2;
            this.lblDepositAmount.Text = "Deposit Amount";
            this.lblDepositAmount.TextAlign = ContentAlignment.MiddleLeft;
            this.dtpDepositDate.Location = new Point(120, 8);
            this.dtpDepositDate.Name = "dtpDepositDate";
            this.dtpDepositDate.Size = new Size(120, 0x15);
            this.dtpDepositDate.TabIndex = 1;
            this.lblDepositDate.Location = new Point(0x10, 8);
            this.lblDepositDate.Name = "lblDepositDate";
            this.lblDepositDate.Size = new Size(0x60, 0x15);
            this.lblDepositDate.TabIndex = 0;
            this.lblDepositDate.Text = "Deposit Date";
            this.lblDepositDate.TextAlign = ContentAlignment.MiddleLeft;
            this.wpAmounts.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Bottom | AnchorStyles.Top;
            this.wpAmounts.Controls.Add(this.Grid);
            this.wpAmounts.Controls.Add(this.StatusStrip1);
            this.wpAmounts.HelpButtonVisible = false;
            this.wpAmounts.Location = new Point(0x10, 0x4c);
            this.wpAmounts.Name = "wpAmounts";
            this.wpAmounts.PageCaption = "Deposit amounts";
            this.wpAmounts.PageDescription = "Enter deposit amount for each line item";
            this.wpAmounts.Size = new Size(0x1dd, 230);
            this.wpAmounts.TabIndex = 2;
            this.Grid.Dock = DockStyle.Fill;
            this.Grid.Location = new Point(0, 0);
            this.Grid.Name = "Grid";
            this.Grid.Size = new Size(0x1dd, 0xd0);
            this.Grid.TabIndex = 2;
            ToolStripItem[] toolStripItems = new ToolStripItem[] { this.tsslInvoiceTotal, this.tsslDepositAmount, this.tsslRemainingAmount };
            this.StatusStrip1.Items.AddRange(toolStripItems);
            this.StatusStrip1.Location = new Point(0, 0xd0);
            this.StatusStrip1.Name = "StatusStrip1";
            this.StatusStrip1.Size = new Size(0x1dd, 0x16);
            this.StatusStrip1.SizingGrip = false;
            this.StatusStrip1.TabIndex = 4;
            this.tsslInvoiceTotal.BorderSides = ToolStripStatusLabelBorderSides.All;
            this.tsslInvoiceTotal.Margin = new Padding(0, 1, 0, 0);
            this.tsslInvoiceTotal.Name = "tsslInvoiceTotal";
            this.tsslInvoiceTotal.Size = new Size(0x6f, 0x15);
            this.tsslInvoiceTotal.Text = "Invoice Total: $0.00";
            this.tsslDepositAmount.BorderSides = ToolStripStatusLabelBorderSides.All;
            this.tsslDepositAmount.Margin = new Padding(0, 1, 0, 0);
            this.tsslDepositAmount.Name = "tsslDepositAmount";
            this.tsslDepositAmount.Size = new Size(0x83, 0x15);
            this.tsslDepositAmount.Text = "Deposit Amount: $0.00";
            this.tsslRemainingAmount.BorderSides = ToolStripStatusLabelBorderSides.All;
            this.tsslRemainingAmount.Margin = new Padding(0, 1, 0, 0);
            this.tsslRemainingAmount.Name = "tsslRemainingAmount";
            this.tsslRemainingAmount.Size = new Size(0x65, 0x15);
            this.tsslRemainingAmount.Text = "Remaining: $0.00";
            this.wpSummary.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Bottom | AnchorStyles.Top;
            this.wpSummary.Controls.Add(this.txtSummary);
            this.wpSummary.HelpButtonVisible = false;
            this.wpSummary.Location = new Point(0x10, 0x4c);
            this.wpSummary.Name = "wpSummary";
            this.wpSummary.PageCaption = "Summary";
            this.wpSummary.PageDescription = "Please verify and proceed";
            this.wpSummary.PageTitleBarText = "Summary";
            this.wpSummary.Size = new Size(0x1dd, 230);
            this.wpSummary.TabIndex = 5;
            this.txtSummary.Dock = DockStyle.Fill;
            this.txtSummary.Font = new Font("Consolas", 9.75f, FontStyle.Regular, GraphicsUnit.Point, 0xcc);
            this.txtSummary.Location = new Point(0, 0);
            this.txtSummary.Multiline = true;
            this.txtSummary.Name = "txtSummary";
            this.txtSummary.ScrollBars = ScrollBars.Both;
            this.txtSummary.Size = new Size(0x1dd, 230);
            this.txtSummary.TabIndex = 8;
            this.txtSummary.WordWrap = false;
            this.wpResult.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Bottom | AnchorStyles.Top;
            this.wpResult.Controls.Add(this.lblResult);
            this.wpResult.HelpButtonVisible = false;
            this.wpResult.Location = new Point(0x10, 0x4c);
            this.wpResult.Name = "wpResult";
            this.wpResult.PageCaption = "Result";
            this.wpResult.PageDescription = "";
            this.wpResult.Size = new Size(0x5f2, 0x217);
            this.wpResult.TabIndex = 4;
            this.wpResult.Text = "wizardPage1";
            this.lblResult.Dock = DockStyle.Top;
            this.lblResult.Location = new Point(0, 0);
            this.lblResult.Name = "lblResult";
            this.lblResult.Size = new Size(0x5f2, 0x17);
            this.lblResult.TabIndex = 2;
            this.lblResult.Text = "Deposit Result";
            this.lblResult.TextAlign = ContentAlignment.MiddleLeft;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.ClientSize = new Size(0x1fd, 0x169);
            base.Controls.Add(this.wizard);
            base.Name = "DialogDeposit";
            this.Text = "Make Deposit";
            ((ISupportInitialize) this.wizard).EndInit();
            this.wpWelcome.ResumeLayout(false);
            this.wpWelcome.PerformLayout();
            this.wpCustomer.ResumeLayout(false);
            this.wpDeposit.ResumeLayout(false);
            this.wpDeposit.PerformLayout();
            this.wpAmounts.ResumeLayout(false);
            this.wpAmounts.PerformLayout();
            this.StatusStrip1.ResumeLayout(false);
            this.StatusStrip1.PerformLayout();
            this.wpSummary.ResumeLayout(false);
            this.wpSummary.PerformLayout();
            this.wpResult.ResumeLayout(false);
            base.ResumeLayout(false);
        }

        private void InitializeGrid(FilteredGridAppearance appearance)
        {
            appearance.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.None;
            appearance.RowHeadersWidth = 30;
            appearance.RowTemplate.Height = 20;
            appearance.AutoGenerateColumns = false;
            appearance.AllowEdit = true;
            appearance.AllowNew = false;
            appearance.MultiSelect = true;
            appearance.Columns.Clear();
            appearance.SelectionMode = DataGridViewSelectionMode.RowHeaderSelect;
            appearance.EditMode = DataGridViewEditMode.EditOnEnter;
            appearance.ShowCellErrors = true;
            appearance.ShowRowErrors = true;
            appearance.AddTextColumn("BillingCode", "Billing Code", 70);
            appearance.AddTextColumn("InventoryItemName", "Inventory Item", 230);
            appearance.AddTextColumn("BillableAmount", "Billable", 60, appearance.PriceStyle());
            DataGridViewTextBoxColumn column1 = appearance.AddTextColumn("EnteredAmount", "Amount", 60);
            column1.DefaultCellStyle = appearance.PriceStyle();
            column1.DefaultCellStyle.BackColor = Color.LightSteelBlue;
            column1.ReadOnly = false;
        }

        private void LoadDialog(int orderId)
        {
            this.details.Clear();
            this.details.AcceptChanges();
            using (MySqlConnection connection = new MySqlConnection(Globals.ConnectionString))
            {
                connection.Open();
                using (MySqlCommand command = new MySqlCommand("", connection))
                {
                    command.CommandText = "SELECT\r\n  c.ID as CustomerID\r\n, o.ID as OrderID\r\n, CONCAT(c.LastName, ', ', c.FirstName) as CustomerName\r\n, CASE WHEN d.OrderID IS NOT NULL THEN 1 ELSE 0 END as DepositExists\r\n, d.Amount\r\n, d.Date\r\n, d.Notes\r\n, d.PaymentMethod\r\nFROM tbl_order as o\r\n     INNER JOIN tbl_customer as c ON c.ID = o.CustomerID\r\n     LEFT JOIN tbl_deposits as d ON d.CustomerID = o.CustomerID\r\n                                AND d.OrderID = o.ID\r\nWHERE o.ID = :OrderID";
                    command.Parameters.Add("OrderID", MySqlType.Int).Value = orderId;
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        if (!reader.Read())
                        {
                            throw new UserNotifyException("Cannot find order");
                        }
                        this.m_customerID = new int?(reader.GetInt32("CustomerID"));
                        this.m_orderID = new int?(reader.GetInt32("OrderID"));
                        this.m_depositExists = reader.GetBoolean("DepositExists");
                        this.nmbDepositAmount.AsDecimal = NullableConvert.ToDecimal(reader["Amount"]);
                        this.dtpDepositDate.Value = NullableConvert.ToDate(reader["Date"]);
                        this.txtDepositNotes.Text = reader.GetString("Notes");
                        this.cmbPaymentMethod.Text = reader.GetString("PaymentMethod");
                        this.txtOrder.Text = this.m_orderID.ToString();
                        this.txtCustomer.Text = reader.GetString(reader.GetOrdinal("CustomerName"));
                    }
                }
                using (MySqlDataAdapter adapter = new MySqlDataAdapter("", connection))
                {
                    adapter.AcceptChangesDuringFill = true;
                    adapter.SelectCommand.CommandText = "SELECT\r\n  d.ID as OrderDetailsID\r\n, d.BillingCode\r\n, IFNULL(i.Name, '') as InventoryItemName\r\n, (1 - IFNULL(o.Discount, 0) / 100) *\r\n  GetAmountMultiplier(d.DOSFrom, d.DOSTo, d.EndDate, d.ActualSaleRentType, d.ActualOrderedWhen, d.ActualBilledWhen) *\r\n  IF((d.Taxable = 1) AND (tr.ID IS NOT NULL)\r\n    ,GetAllowableAmount(d.ActualSaleRentType, 1 /*d.BillingMonth*/, d.AllowablePrice, d.BilledQuantity, pc.Sale_AllowablePrice, d.FlatRate) * (1 + IFNULL(tr.TotalTax, 0) / 100)\r\n    ,GetBillableAmount (d.ActualSaleRentType, 1 /*d.BillingMonth*/, d.BillablePrice , d.BilledQuantity, pc.Sale_BillablePrice, d.FlatRate))\r\n  as BillableAmount\r\n, (1 - IFNULL(o.Discount, 0) / 100) *\r\n  GetAmountMultiplier(d.DOSFrom, d.DOSTo, d.EndDate, d.ActualSaleRentType, d.ActualOrderedWhen, d.ActualBilledWhen) *\r\n  GetAllowableAmount(d.ActualSaleRentType, 1 /*d.BillingMonth*/, d.AllowablePrice, d.BilledQuantity, pc.Sale_AllowablePrice, d.FlatRate)\r\n  as AllowableAmount\r\n, dd.Amount as EnteredAmount\r\n, d.BilledQuantity as Quantity\r\n, d.DOSFrom\r\n, d.DOSTo\r\nFROM tbl_order as o\r\n     INNER JOIN view_orderdetails_core as d ON d.CustomerID = o.CustomerID\r\n                                           AND d.OrderID    = o.ID\r\n     INNER JOIN tbl_inventoryitem as i ON i.ID = d.InventoryItemID\r\n     INNER JOIN tbl_pricecode_item as pc ON pc.PriceCodeID = d.PriceCodeID\r\n                                        AND pc.InventoryItemID = d.InventoryItemID\r\n     LEFT JOIN tbl_customer as c ON c.ID = o.CustomerID\r\n     LEFT JOIN tbl_company ON tbl_company.ID = 1\r\n     LEFT JOIN view_taxrate as tr ON tr.ID = IFNULL(c.TaxRateID, tbl_company.TaxRateID)\r\n     LEFT JOIN tbl_depositdetails as dd ON dd.CustomerID     = d.CustomerID\r\n                                       AND dd.OrderID        = d.OrderID\r\n                                       AND dd.OrderDetailsID = d.ID\r\nWHERE (o.ID = :OrderID)";
                    adapter.SelectCommand.Parameters.Add("OrderID", MySqlType.Int).Value = orderId;
                    adapter.Fill(this.details);
                }
            }
            double totalBillable = this.details.GetTotalBillable();
            this.tsslInvoiceTotal.Text = $"Total : ${totalBillable:0.00}";
            this.txtInvoiceTotal.Text = totalBillable.ToString("0.00");
        }

        private void NavigateBack(BaseStage stage)
        {
            this.CurrentStage = stage;
            stage.UpdateButtons();
        }

        private void NavigateNext(BaseStage stage)
        {
            this.CurrentStage = stage;
            stage.Begin();
            stage.UpdateButtons();
        }

        public bool ShowDialog(int orderId)
        {
            this.LoadDialog(orderId);
            return (base.ShowDialog() == DialogResult.OK);
        }

        private void Wizard_BackButtonClick(object sender, WizardPageCancelEventArgs e)
        {
            e.Cancel = true;
            BaseStage currentStage = this.CurrentStage;
            if ((currentStage != null) && !ReferenceEquals(currentStage, this.stageWelcome))
            {
                if (ReferenceEquals(currentStage, this.stageCustomer))
                {
                    this.NavigateBack(this.stageWelcome);
                }
                else if (ReferenceEquals(currentStage, this.stageDeposit))
                {
                    this.NavigateBack(this.stageCustomer);
                }
                else if (ReferenceEquals(currentStage, this.stageAmounts))
                {
                    this.NavigateBack(this.stageDeposit);
                }
                else if (ReferenceEquals(currentStage, this.stageReview))
                {
                    this.NavigateBack(this.stageAmounts);
                }
                else
                {
                    BaseStage stageResult = this.stageResult;
                    BaseStage stage2 = currentStage;
                }
            }
        }

        private void Wizard_CancelButtonClick(object sender, EventArgs e)
        {
            base.DialogResult = DialogResult.Cancel;
            base.Close();
        }

        private void Wizard_FinishButtonClick(object sender, EventArgs e)
        {
            base.DialogResult = DialogResult.OK;
            base.Close();
        }

        private void Wizard_NextButtonClick(object sender, WizardPageCancelEventArgs e)
        {
            e.Cancel = true;
            try
            {
                BaseStage currentStage = this.CurrentStage;
                if (currentStage != null)
                {
                    currentStage.Commit();
                    if (ReferenceEquals(currentStage, this.stageWelcome))
                    {
                        this.NavigateNext(this.stageCustomer);
                    }
                    else if (ReferenceEquals(currentStage, this.stageCustomer))
                    {
                        this.NavigateNext(this.stageDeposit);
                    }
                    else if (ReferenceEquals(currentStage, this.stageDeposit))
                    {
                        this.NavigateNext(this.stageAmounts);
                    }
                    else if (ReferenceEquals(currentStage, this.stageAmounts))
                    {
                        this.NavigateNext(this.stageReview);
                    }
                    else if (ReferenceEquals(currentStage, this.stageReview))
                    {
                        this.NavigateNext(this.stageResult);
                    }
                    else
                    {
                        BaseStage stageResult = this.stageResult;
                        BaseStage stage2 = currentStage;
                    }
                }
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private BaseStage CurrentStage
        {
            get => 
                !ReferenceEquals(this.wizard.SelectedPage, this.stageWelcome.Page) ? (!ReferenceEquals(this.wizard.SelectedPage, this.stageCustomer.Page) ? (!ReferenceEquals(this.wizard.SelectedPage, this.stageDeposit.Page) ? (!ReferenceEquals(this.wizard.SelectedPage, this.stageAmounts.Page) ? (!ReferenceEquals(this.wizard.SelectedPage, this.stageReview.Page) ? (!ReferenceEquals(this.wizard.SelectedPage, this.stageResult.Page) ? null : this.stageResult) : this.stageReview) : this.stageAmounts) : this.stageDeposit) : this.stageCustomer) : this.stageWelcome;
            set
            {
                if (value == null)
                {
                    throw new ArgumentNullException("value");
                }
                this.wizard.SelectedPage = value.Page;
            }
        }

        [Serializable, CompilerGenerated]
        private sealed class <>c
        {
            public static readonly DialogDeposit.<>c <>9 = new DialogDeposit.<>c();
            public static Func<DataRow, bool> <>9__19_0;

            internal bool <GetTable>b__19_0(DataRow r) => 
                r.HasErrors;
        }

        private abstract class BaseStage
        {
            public readonly DialogDeposit wizard;

            protected BaseStage(DialogDeposit wizard)
            {
                if (wizard == null)
                {
                    DialogDeposit local1 = wizard;
                    throw new ArgumentNullException("wizard");
                }
                this.wizard = wizard;
            }

            public virtual void Begin()
            {
            }

            public virtual void Commit()
            {
            }

            public virtual void UpdateButtons()
            {
            }

            public abstract WizardPage Page { get; }
        }

        private class StageAmounts : DialogDeposit.BaseStage
        {
            public StageAmounts(DialogDeposit wizard) : base(wizard)
            {
            }

            public override void Begin()
            {
                bool flag = !base.wizard.m_depositExists;
                base.wizard.Grid.Appearance.AllowEdit = flag;
                base.wizard.tsslRemainingAmount.Visible = flag;
                base.wizard.tsslDepositAmount.Text = $"Deposit Amount: ${base.wizard.nmbDepositAmount.AsDouble:0.00}";
                this.UpdateRemainingAmount();
                base.wizard.details.ColumnChanged -= new DataColumnChangeEventHandler(this.Details_ColumnChanged);
                base.wizard.Grid.GridSource = base.wizard.details.ToGridSource();
                base.wizard.details.ColumnChanged += new DataColumnChangeEventHandler(this.Details_ColumnChanged);
            }

            public override void Commit()
            {
                if (!base.wizard.m_depositExists)
                {
                    base.wizard.GetTable();
                }
            }

            private void Details_ColumnChanged(object sender, DataColumnChangeEventArgs e)
            {
                this.UpdateRemainingAmount();
            }

            private void Details_RowChanged(object sender, DataRowChangeEventArgs e)
            {
                this.UpdateRemainingAmount();
            }

            public override void UpdateButtons()
            {
                bool flag = !base.wizard.m_depositExists;
                this.Page.NextButtonEnabled = flag ? WizardButtonEnabledDefault.True : WizardButtonEnabledDefault.False;
                this.Page.NextButtonVisible = flag;
                this.Page.FinishButtonEnabled = !flag ? WizardButtonEnabledDefault.True : WizardButtonEnabledDefault.False;
                this.Page.FinishButtonVisible = !flag;
            }

            private void UpdateRemainingAmount()
            {
                double? nullable1;
                double? nullable2 = base.wizard.nmbDepositAmount.AsDouble;
                double totalEntered = base.wizard.details.GetTotalEntered();
                if (nullable2 != null)
                {
                    nullable1 = new double?(nullable2.GetValueOrDefault() - totalEntered);
                }
                else
                {
                    nullable1 = null;
                }
                base.wizard.tsslRemainingAmount.Text = $"Remaining amount: ${nullable1:0.00}";
            }

            public override WizardPage Page =>
                base.wizard.wpAmounts;
        }

        private class StageCustomer : DialogDeposit.BaseStage
        {
            public StageCustomer(DialogDeposit wizard) : base(wizard)
            {
            }

            public override WizardPage Page =>
                base.wizard.wpCustomer;
        }

        private class StageDeposit : DialogDeposit.BaseStage
        {
            public StageDeposit(DialogDeposit wizard) : base(wizard)
            {
            }

            public override void Begin()
            {
                bool flag = !base.wizard.m_depositExists;
                base.wizard.dtpDepositDate.Enabled = flag;
                base.wizard.nmbDepositAmount.ReadOnly = !flag;
                base.wizard.txtDepositNotes.ReadOnly = !flag;
                base.wizard.cmbPaymentMethod.Enabled = flag;
            }

            public override void Commit()
            {
                if (!base.wizard.m_depositExists)
                {
                    if (NullableConvert.ToDate(base.wizard.dtpDepositDate.Value) == null)
                    {
                        throw new UserNotifyException("Please enter deposit date");
                    }
                    double? asDouble = base.wizard.nmbDepositAmount.AsDouble;
                    if (asDouble == null)
                    {
                        throw new UserNotifyException("Please enter deposit amount");
                    }
                    double? nullable3 = asDouble;
                    double num = 0.0;
                    if ((nullable3.GetValueOrDefault() < num) & (nullable3 != null))
                    {
                        throw new UserNotifyException("Deposit amount cannot be negative");
                    }
                    nullable3 = asDouble;
                    if ((base.wizard.details.GetTotalBillable() < nullable3.GetValueOrDefault()) & (nullable3 != null))
                    {
                        throw new UserNotifyException("Deposit amount cannot be greater than total");
                    }
                    string str = base.wizard.cmbPaymentMethod.Text ?? string.Empty;
                    if (!str.Equals("Cash", StringComparison.InvariantCultureIgnoreCase) && (!str.Equals("Check", StringComparison.InvariantCultureIgnoreCase) && !str.Equals("Credit Card", StringComparison.InvariantCultureIgnoreCase)))
                    {
                        throw new UserNotifyException("Please select payment method");
                    }
                }
            }

            public override void UpdateButtons()
            {
            }

            public override WizardPage Page =>
                base.wizard.wpDeposit;
        }

        private class StageResult : DialogDeposit.BaseStage
        {
            public StageResult(DialogDeposit wizard) : base(wizard)
            {
            }

            public override void Begin()
            {
                if (base.wizard.m_depositExists)
                {
                    throw new InvalidOperationException();
                }
                try
                {
                    DialogDeposit.TableDetails table = base.wizard.GetTable();
                    int? customerID = base.wizard.m_customerID;
                    int? orderID = base.wizard.m_orderID;
                    using (MySqlConnection connection = new MySqlConnection(Globals.ConnectionString))
                    {
                        connection.Open();
                        MySqlTransaction transaction = connection.BeginTransaction();
                        try
                        {
                            using (MySqlCommand command = new MySqlCommand("", connection, transaction))
                            {
                                command.CommandText = "INSERT INTO tbl_deposits (CustomerID, OrderID, Amount, Date, Notes, PaymentMethod, LastUpdateUserID)\r\nVALUES (:CustomerID, :OrderID, :Amount, :Date, :Notes, :PaymentMethod, :LastUpdateUserID)";
                                MySqlParameter parameter1 = new MySqlParameter("CustomerId", MySqlType.Int);
                                parameter1.Value = customerID;
                                MySqlParameter[] values = new MySqlParameter[7];
                                values[0] = parameter1;
                                MySqlParameter parameter2 = new MySqlParameter("OrderId", MySqlType.Int);
                                parameter2.Value = orderID;
                                values[1] = parameter2;
                                MySqlParameter parameter3 = new MySqlParameter("Amount", MySqlType.Decimal);
                                parameter3.Value = table.GetTotalEntered();
                                values[2] = parameter3;
                                MySqlParameter parameter4 = new MySqlParameter("Date", MySqlType.Date);
                                parameter4.Value = base.wizard.dtpDepositDate.Value;
                                values[3] = parameter4;
                                MySqlParameter parameter5 = new MySqlParameter("Notes", MySqlType.Text);
                                parameter5.Value = base.wizard.txtDepositNotes.Text;
                                values[4] = parameter5;
                                MySqlParameter parameter6 = new MySqlParameter("PaymentMethod", MySqlType.VarChar, 20);
                                parameter6.Value = base.wizard.cmbPaymentMethod.Text;
                                values[5] = parameter6;
                                MySqlParameter parameter7 = new MySqlParameter("LastUpdateUserID", MySqlType.SmallInt);
                                parameter7.Value = Globals.CompanyUserID;
                                values[6] = parameter7;
                                command.Parameters.AddRange(values);
                                command.ExecuteNonQuery();
                            }
                            using (MySqlCommand command2 = new MySqlCommand("", connection, transaction))
                            {
                                command2.CommandText = "INSERT INTO tbl_depositdetails (CustomerID, OrderID, OrderDetailsID, Amount, LastUpdateUserID)\r\nVALUES (:CustomerID, :OrderID, :OrderDetailsID, :Amount, :LastUpdateUserID)";
                                MySqlParameter parameter8 = new MySqlParameter("CustomerId", MySqlType.Int);
                                parameter8.Value = customerID;
                                MySqlParameter[] values = new MySqlParameter[5];
                                values[0] = parameter8;
                                MySqlParameter parameter9 = new MySqlParameter("OrderId", MySqlType.Int);
                                parameter9.Value = orderID;
                                values[1] = parameter9;
                                values[2] = new MySqlParameter("OrderDetailsID", MySqlType.Int);
                                values[3] = new MySqlParameter("Amount", MySqlType.Decimal);
                                MySqlParameter parameter10 = new MySqlParameter("LastUpdateUserID", MySqlType.SmallInt);
                                parameter10.Value = Globals.CompanyUserID;
                                values[4] = parameter10;
                                command2.Parameters.AddRange(values);
                                foreach (DataRow row in table.Select("0.01 <= EnteredAmount"))
                                {
                                    command2.Parameters["OrderDetailsID"].Value = row[table.Col_OrderDetailsId];
                                    command2.Parameters["Amount"].Value = row[table.Col_EnteredAmount];
                                    command2.ExecuteNonQuery();
                                }
                            }
                            using (MySqlCommand command3 = new MySqlCommand("", connection, transaction))
                            {
                                command3.Parameters.Add("P_OrderID", MySqlType.Int).Value = orderID;
                                command3.ExecuteProcedure("Order_ConvertDepositsIntoPayments");
                            }
                            transaction.Commit();
                        }
                        catch (Exception exception)
                        {
                            transaction.Rollback();
                            throw new UserNotifyException("Transactions cannot be created", exception);
                        }
                    }
                    base.wizard.lblResult.Text = "Deposit have been successfully created";
                }
                catch (Exception exception2)
                {
                    base.wizard.lblResult.Text = "Application errors : " + exception2.ToString();
                }
            }

            public override void Commit()
            {
            }

            public override void UpdateButtons()
            {
                this.Page.BackButtonVisible = false;
                this.Page.BackButtonEnabled = WizardButtonEnabledDefault.False;
                this.Page.CancelButtonVisible = false;
                this.Page.CancelButtonEnabled = WizardButtonEnabledDefault.False;
            }

            public override WizardPage Page =>
                base.wizard.wpResult;
        }

        private class StageSummary : DialogDeposit.BaseStage
        {
            public StageSummary(DialogDeposit wizard) : base(wizard)
            {
            }

            public override void Begin()
            {
                if (base.wizard.m_depositExists)
                {
                    throw new InvalidOperationException();
                }
                DialogDeposit wizard = base.wizard;
                using (StringWriter writer = new StringWriter())
                {
                    writer.WriteLine("Review your selections");
                    writer.WriteLine("---------------------");
                    writer.WriteLine("Customer       : " + wizard.txtCustomer.Text);
                    writer.WriteLine("Order #        : " + wizard.txtOrder.Text);
                    writer.WriteLine("Total          : ${0:0.00}", wizard.details.GetTotalBillable());
                    writer.WriteLine("Deposit date   : {0:MM/dd/yyyy}", wizard.dtpDepositDate.Value);
                    writer.WriteLine("Deposit amount : ${0:0.00}", wizard.nmbDepositAmount.AsDouble);
                    writer.WriteLine("Payment method : {0}", wizard.cmbPaymentMethod.Text);
                    base.wizard.txtSummary.Text = writer.ToString();
                }
            }

            public override void Commit()
            {
            }

            public override void UpdateButtons()
            {
            }

            public override WizardPage Page =>
                base.wizard.wpSummary;
        }

        private class StageWelcome : DialogDeposit.BaseStage
        {
            public StageWelcome(DialogDeposit wizard) : base(wizard)
            {
            }

            public override WizardPage Page =>
                base.wizard.wpWelcome;
        }

        public class TableDetails : DataTable
        {
            public DataColumn Col_AllowableAmount;
            public DataColumn Col_BillableAmount;
            public DataColumn Col_BillingCode;
            public DataColumn Col_DOSFrom;
            public DataColumn Col_DOSTo;
            public DataColumn Col_EnteredAmount;
            public DataColumn Col_InventoryItemName;
            public DataColumn Col_OrderDetailsId;
            public DataColumn Col_Quantity;

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
                DialogDeposit.TableDetails details1 = (DialogDeposit.TableDetails) base.Clone();
                details1.InitializeFields();
                return details1;
            }

            private void CreateColumns()
            {
                base.Columns.Add("OrderDetailsId", typeof(int)).ReadOnly = true;
                base.Columns.Add("BillingCode", typeof(string)).ReadOnly = true;
                base.Columns.Add("InventoryItemName", typeof(string)).ReadOnly = true;
                base.Columns.Add("BillableAmount", typeof(double)).ReadOnly = true;
                base.Columns.Add("AllowableAmount", typeof(double)).ReadOnly = true;
                base.Columns.Add("EnteredAmount", typeof(double));
                base.Columns.Add("Quantity", typeof(double)).ReadOnly = true;
                base.Columns.Add("DOSFrom", typeof(DateTime)).ReadOnly = true;
                base.Columns.Add("DOSTo", typeof(DateTime)).ReadOnly = true;
            }

            public double GetTotalBillable() => 
                Convert.ToDouble(base.Compute("SUM(BillableAmount)", ""));

            public double GetTotalEntered()
            {
                double num = 0.0;
                foreach (DataRow row in base.Select("", "", DataViewRowState.CurrentRows))
                {
                    DataRowVersion version = !row.HasVersion(DataRowVersion.Proposed) ? DataRowVersion.Default : DataRowVersion.Proposed;
                    num += NullableConvert.ToDouble(row[this.Col_EnteredAmount, version], 0.0);
                }
                return num;
            }

            private void InitializeFields()
            {
                this.Col_OrderDetailsId = base.Columns["OrderDetailsId"];
                this.Col_BillingCode = base.Columns["BillingCode"];
                this.Col_InventoryItemName = base.Columns["InventoryItemName"];
                this.Col_BillableAmount = base.Columns["BillableAmount"];
                this.Col_AllowableAmount = base.Columns["AllowableAmount"];
                this.Col_EnteredAmount = base.Columns["EnteredAmount"];
                this.Col_Quantity = base.Columns["Quantity"];
                this.Col_DOSFrom = base.Columns["DOSFrom"];
                this.Col_DOSTo = base.Columns["DOSTo"];
            }

            protected override void OnColumnChanged(DataColumnChangeEventArgs e)
            {
                if (ReferenceEquals(e.Column, this.Col_EnteredAmount) || ReferenceEquals(e.Column, this.Col_BillableAmount))
                {
                    double num = NullableConvert.ToDouble(e.Row[this.Col_EnteredAmount], 0.0);
                    double num2 = NullableConvert.ToDouble(e.Row[this.Col_BillableAmount], 0.0);
                    if (num < 0.0)
                    {
                        e.Row.SetColumnError(this.Col_EnteredAmount, "Cannot be negative");
                    }
                    else if (num2 < num)
                    {
                        e.Row.SetColumnError(this.Col_EnteredAmount, "Cannot be greater than billable");
                    }
                    else
                    {
                        e.Row.SetColumnError(this.Col_EnteredAmount, "");
                    }
                }
                base.OnColumnChanged(e);
            }
        }
    }
}


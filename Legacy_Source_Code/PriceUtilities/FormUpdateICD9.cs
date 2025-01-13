namespace DMEWorks.PriceUtilities
{
    using DMEWorks.Csv;
    using DMEWorks.Forms;
    using System;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.IO;
    using System.Windows.Forms;

    public class FormUpdateICD9 : DmeForm
    {
        private DataTable table;
        private IContainer components;
        private Panel pnlSelectFile;
        private Label lblFileName;
        private Button btnBrowse;
        private TextBox txtFilePath;
        private Panel panel4;
        private Button btnBack;
        private Button btnCancel;
        private Button btnFinish;
        private Button btnNext;
        private Panel pnlResults;
        private Panel pnlPreview;
        private DataGridView dgvPreview;
        private Label lblPreview;
        private TextBox txtResults;
        private Label lblResults;
        private Panel panel5;
        private Label lblStageDescription;
        private Label lblStage;
        private OpenFileDialog openFileDialog1;

        public FormUpdateICD9()
        {
            this.InitializeComponent();
            this.pnlSelectFile.Dock = DockStyle.Fill;
            this.pnlPreview.Dock = DockStyle.Fill;
            this.pnlResults.Dock = DockStyle.Fill;
            this.CurrentStage = StageEnum.None;
        }

        private void btnBack_Click(object sender, EventArgs e)
        {
            StageEnum currentStage = this.CurrentStage;
            try
            {
                if (currentStage == StageEnum.Preview)
                {
                    this.CurrentStage = StageEnum.SelectFile;
                }
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private void btnBrowse_Click(object sender, EventArgs e)
        {
            try
            {
                this.openFileDialog1.FileName = this.txtFilePath.Text;
            }
            catch
            {
            }
            if (this.openFileDialog1.ShowDialog() == DialogResult.OK)
            {
                this.txtFilePath.Text = this.openFileDialog1.FileName;
            }
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            base.Close();
        }

        private void btnFinish_Click(object sender, EventArgs e)
        {
            base.Close();
        }

        private void btnNext_Click(object sender, EventArgs e)
        {
            StageEnum currentStage = this.CurrentStage;
            try
            {
                switch (currentStage)
                {
                    case StageEnum.None:
                        this.CurrentStage = StageEnum.SelectFile;
                        break;

                    case StageEnum.SelectFile:
                        this.ProcessStage_SelectFile();
                        this.CurrentStage = StageEnum.Preview;
                        break;

                    case StageEnum.Preview:
                        this.ProcessStage_Preview();
                        this.CurrentStage = StageEnum.Results;
                        break;

                    case StageEnum.Results:
                        this.ProcessStage_Results();
                        this.CurrentStage = StageEnum.None;
                        break;

                    default:
                        break;
                }
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
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

        private void InitializeComponent()
        {
            this.pnlSelectFile = new Panel();
            this.panel4 = new Panel();
            this.pnlResults = new Panel();
            this.pnlPreview = new Panel();
            this.btnNext = new Button();
            this.btnFinish = new Button();
            this.btnCancel = new Button();
            this.btnBack = new Button();
            this.txtFilePath = new TextBox();
            this.btnBrowse = new Button();
            this.lblFileName = new Label();
            this.dgvPreview = new DataGridView();
            this.lblPreview = new Label();
            this.lblResults = new Label();
            this.txtResults = new TextBox();
            this.panel5 = new Panel();
            this.lblStage = new Label();
            this.lblStageDescription = new Label();
            this.openFileDialog1 = new OpenFileDialog();
            this.pnlSelectFile.SuspendLayout();
            this.panel4.SuspendLayout();
            this.pnlResults.SuspendLayout();
            this.pnlPreview.SuspendLayout();
            ((ISupportInitialize) this.dgvPreview).BeginInit();
            this.panel5.SuspendLayout();
            base.SuspendLayout();
            this.pnlSelectFile.BorderStyle = BorderStyle.FixedSingle;
            this.pnlSelectFile.Controls.Add(this.lblFileName);
            this.pnlSelectFile.Controls.Add(this.btnBrowse);
            this.pnlSelectFile.Controls.Add(this.txtFilePath);
            this.pnlSelectFile.Location = new Point(0, 0x20);
            this.pnlSelectFile.Name = "pnlSelectFile";
            this.pnlSelectFile.Size = new Size(0x1fa, 0x169);
            this.pnlSelectFile.TabIndex = 1;
            this.pnlSelectFile.Visible = false;
            this.panel4.Controls.Add(this.btnBack);
            this.panel4.Controls.Add(this.btnCancel);
            this.panel4.Controls.Add(this.btnFinish);
            this.panel4.Controls.Add(this.btnNext);
            this.panel4.Dock = DockStyle.Bottom;
            this.panel4.Location = new Point(0, 0x1b1);
            this.panel4.Name = "panel4";
            this.panel4.Size = new Size(530, 0x30);
            this.panel4.TabIndex = 4;
            this.pnlResults.BorderStyle = BorderStyle.FixedSingle;
            this.pnlResults.Controls.Add(this.txtResults);
            this.pnlResults.Controls.Add(this.lblResults);
            this.pnlResults.Location = new Point(6, 0x4f);
            this.pnlResults.Margin = new Padding(0);
            this.pnlResults.Name = "pnlResults";
            this.pnlResults.Padding = new Padding(4);
            this.pnlResults.Size = new Size(0x204, 0x155);
            this.pnlResults.TabIndex = 3;
            this.pnlResults.Visible = false;
            this.pnlPreview.BorderStyle = BorderStyle.FixedSingle;
            this.pnlPreview.Controls.Add(this.dgvPreview);
            this.pnlPreview.Controls.Add(this.lblPreview);
            this.pnlPreview.Location = new Point(2, 0x33);
            this.pnlPreview.Margin = new Padding(0);
            this.pnlPreview.Name = "pnlPreview";
            this.pnlPreview.Padding = new Padding(4);
            this.pnlPreview.Size = new Size(0x20a, 0x164);
            this.pnlPreview.TabIndex = 2;
            this.pnlPreview.Visible = false;
            this.btnNext.Location = new Point(0x114, 15);
            this.btnNext.Name = "btnNext";
            this.btnNext.Size = new Size(0x4b, 0x17);
            this.btnNext.TabIndex = 1;
            this.btnNext.Text = "&Next >";
            this.btnNext.UseVisualStyleBackColor = true;
            this.btnNext.Click += new EventHandler(this.btnNext_Click);
            this.btnFinish.Location = new Point(0x165, 15);
            this.btnFinish.Name = "btnFinish";
            this.btnFinish.Size = new Size(0x4b, 0x17);
            this.btnFinish.TabIndex = 2;
            this.btnFinish.Text = "&Finish >>|";
            this.btnFinish.UseVisualStyleBackColor = true;
            this.btnFinish.Click += new EventHandler(this.btnFinish_Click);
            this.btnCancel.Location = new Point(0x1b6, 15);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new Size(0x4b, 0x17);
            this.btnCancel.TabIndex = 3;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new EventHandler(this.btnCancel_Click);
            this.btnBack.Location = new Point(0xc3, 15);
            this.btnBack.Name = "btnBack";
            this.btnBack.Size = new Size(0x4b, 0x17);
            this.btnBack.TabIndex = 0;
            this.btnBack.Text = "< &Back";
            this.btnBack.UseVisualStyleBackColor = true;
            this.btnBack.Click += new EventHandler(this.btnBack_Click);
            this.txtFilePath.BorderStyle = BorderStyle.FixedSingle;
            this.txtFilePath.Location = new Point(0x10, 0x29);
            this.txtFilePath.Name = "txtFilePath";
            this.txtFilePath.Size = new Size(0x173, 20);
            this.txtFilePath.TabIndex = 1;
            this.btnBrowse.FlatStyle = FlatStyle.Flat;
            this.btnBrowse.Location = new Point(0x189, 0x27);
            this.btnBrowse.Name = "btnBrowse";
            this.btnBrowse.Size = new Size(0x4b, 0x16);
            this.btnBrowse.TabIndex = 2;
            this.btnBrowse.Text = "Browse";
            this.btnBrowse.UseVisualStyleBackColor = true;
            this.btnBrowse.Click += new EventHandler(this.btnBrowse_Click);
            this.lblFileName.Location = new Point(15, 0x12);
            this.lblFileName.Name = "lblFileName";
            this.lblFileName.Size = new Size(0x97, 20);
            this.lblFileName.TabIndex = 0;
            this.lblFileName.Text = "File Path:";
            this.dgvPreview.AllowUserToAddRows = false;
            this.dgvPreview.AllowUserToDeleteRows = false;
            this.dgvPreview.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvPreview.Dock = DockStyle.Fill;
            this.dgvPreview.Location = new Point(4, 0x1c);
            this.dgvPreview.Name = "dgvPreview";
            this.dgvPreview.ReadOnly = true;
            this.dgvPreview.Size = new Size(0x200, 0x142);
            this.dgvPreview.TabIndex = 0;
            this.lblPreview.Dock = DockStyle.Top;
            this.lblPreview.Location = new Point(4, 4);
            this.lblPreview.Margin = new Padding(0);
            this.lblPreview.Name = "lblPreview";
            this.lblPreview.Size = new Size(0x200, 0x18);
            this.lblPreview.TabIndex = 1;
            this.lblPreview.Text = "Preview";
            this.lblResults.Dock = DockStyle.Top;
            this.lblResults.Location = new Point(4, 4);
            this.lblResults.Margin = new Padding(0);
            this.lblResults.Name = "lblResults";
            this.lblResults.Size = new Size(0x1fa, 0x18);
            this.lblResults.TabIndex = 0;
            this.lblResults.Text = "Results";
            this.txtResults.BorderStyle = BorderStyle.FixedSingle;
            this.txtResults.Dock = DockStyle.Fill;
            this.txtResults.Location = new Point(4, 0x1c);
            this.txtResults.Margin = new Padding(0);
            this.txtResults.Multiline = true;
            this.txtResults.Name = "txtResults";
            this.txtResults.ScrollBars = ScrollBars.Vertical;
            this.txtResults.Size = new Size(0x1fa, 0x133);
            this.txtResults.TabIndex = 1;
            this.txtResults.WordWrap = false;
            this.panel5.Controls.Add(this.lblStageDescription);
            this.panel5.Controls.Add(this.lblStage);
            this.panel5.Dock = DockStyle.Top;
            this.panel5.Location = new Point(0, 0);
            this.panel5.Name = "panel5";
            this.panel5.Size = new Size(530, 60);
            this.panel5.TabIndex = 0;
            this.lblStage.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Bold, GraphicsUnit.Point, 0xcc);
            this.lblStage.Location = new Point(4, 4);
            this.lblStage.Name = "lblStage";
            this.lblStage.Size = new Size(0x16d, 0x15);
            this.lblStage.TabIndex = 0;
            this.lblStage.Text = "Stage";
            this.lblStageDescription.Location = new Point(12, 30);
            this.lblStageDescription.Name = "lblStageDescription";
            this.lblStageDescription.Size = new Size(0x183, 0x15);
            this.lblStageDescription.TabIndex = 1;
            this.lblStageDescription.Text = "Stage Description";
            this.openFileDialog1.FileName = "openFileDialog1";
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.ClientSize = new Size(530, 0x1e1);
            base.Controls.Add(this.pnlPreview);
            base.Controls.Add(this.pnlResults);
            base.Controls.Add(this.pnlSelectFile);
            base.Controls.Add(this.panel5);
            base.Controls.Add(this.panel4);
            base.Name = "FormUpdateICD9";
            this.Text = "FormUpdateICD9";
            this.pnlSelectFile.ResumeLayout(false);
            this.pnlSelectFile.PerformLayout();
            this.panel4.ResumeLayout(false);
            this.pnlResults.ResumeLayout(false);
            this.pnlResults.PerformLayout();
            this.pnlPreview.ResumeLayout(false);
            ((ISupportInitialize) this.dgvPreview).EndInit();
            this.panel5.ResumeLayout(false);
            base.ResumeLayout(false);
        }

        private void ProcessStage_None()
        {
            this.table = null;
        }

        private void ProcessStage_Preview()
        {
        }

        private void ProcessStage_Results()
        {
            base.Close();
        }

        private void ProcessStage_SelectFile()
        {
            using (StreamReader reader = new StreamReader(this.txtFilePath.Text))
            {
                using (IDataReader reader2 = new CsvReader(reader, true))
                {
                    DataTable table = new DataTable("");
                    int i = 0;
                    while (true)
                    {
                        if (i >= reader2.FieldCount)
                        {
                            while (true)
                            {
                                if (!reader2.Read())
                                {
                                    this.table = table;
                                    this.dgvPreview.DataSource = this.table;
                                    break;
                                }
                                DataRow row = table.NewRow();
                                int num2 = 0;
                                while (true)
                                {
                                    if (num2 >= reader2.FieldCount)
                                    {
                                        table.Rows.Add(row);
                                        row.AcceptChanges();
                                        break;
                                    }
                                    row[table.Columns[num2]] = reader2.GetString(num2);
                                    num2++;
                                }
                            }
                            break;
                        }
                        table.Columns.Add(reader2.GetName(i), typeof(string));
                        i++;
                    }
                }
            }
        }

        private StageEnum CurrentStage
        {
            get => 
                !this.pnlSelectFile.Visible ? (!this.pnlPreview.Visible ? (!this.pnlResults.Visible ? StageEnum.None : StageEnum.Results) : StageEnum.Preview) : StageEnum.SelectFile;
            set
            {
                this.pnlSelectFile.Visible = value == StageEnum.SelectFile;
                this.pnlPreview.Visible = value == StageEnum.Preview;
                this.pnlResults.Visible = value == StageEnum.Results;
                this.btnBack.Enabled = this.pnlSelectFile.Visible || this.pnlPreview.Visible;
                this.btnNext.Enabled = this.pnlSelectFile.Visible || ((!this.pnlSelectFile.Visible && !this.pnlPreview.Visible) && !this.pnlResults.Visible);
                this.btnFinish.Enabled = this.pnlPreview.Visible;
            }
        }

        private enum StageEnum
        {
            None,
            SelectFile,
            Preview,
            Results
        }
    }
}


namespace DMEWorks.Core
{
    using DMEWorks.Forms;
    using DMEWorks.Forms.Properties;
    using DMEWorks.Properties;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Diagnostics;
    using System.Drawing;
    using System.Windows.Forms;

    public class Navigator : UserControl
    {
        private readonly HashSet<string> m_tableNames;
        private static readonly object m_keyCreateSource = new object();
        private static readonly object m_keyFillSource = new object();
        private static readonly object m_keyNavigatorRowClick = new object();
        private readonly Queue<DateTime> m_filterQueue;
        private readonly Queue<DateTime> m_reloadQueue;
        private IContainer components;
        private FilteredGrid grid;
        private TextBox txtFilter;
        private BackgroundWorker worker;
        private Panel pnlFilter;
        private Label spinner;
        private Timer timer;
        private Button btnColumns;
        private Button btnRefresh;

        public event EventHandler<CreateSourceEventArgs> CreateSource
        {
            add
            {
                base.Events.AddHandler(m_keyCreateSource, value);
            }
            remove
            {
                base.Events.RemoveHandler(m_keyCreateSource, value);
            }
        }

        public event EventHandler<FillSourceEventArgs> FillSource
        {
            add
            {
                base.Events.AddHandler(m_keyFillSource, value);
            }
            remove
            {
                base.Events.RemoveHandler(m_keyFillSource, value);
            }
        }

        public event EventHandler<NavigatorRowClickEventArgs> NavigatorRowClick
        {
            add
            {
                base.Events.AddHandler(m_keyNavigatorRowClick, value);
            }
            remove
            {
                base.Events.RemoveHandler(m_keyNavigatorRowClick, value);
            }
        }

        public Navigator()
        {
            this.m_filterQueue = new Queue<DateTime>();
            this.m_reloadQueue = new Queue<DateTime>();
            this.m_tableNames = new HashSet<string>(StringComparer.InvariantCultureIgnoreCase);
            this.InitializeComponent();
            this.txtFilter.TextChanged += new EventHandler(this.txtFilter_TextChanged);
            this.btnRefresh.Click += new EventHandler(this.btnRefresh_Click);
            this.pnlFilter.Layout += new LayoutEventHandler(this.pnlFilter_Layout);
            this.grid.RowDoubleClick += new EventHandler<GridMouseEventArgs>(this.grid_RowDoubleClick);
            this.timer.Tick += new EventHandler(this.timer_Tick);
            this.worker.DoWork += new DoWorkEventHandler(this.worker_DoWork);
            this.worker.RunWorkerCompleted += new RunWorkerCompletedEventHandler(this.worker_RunWorkerCompleted);
            this.worker.ProgressChanged += new ProgressChangedEventHandler(this.worker_ProgressChanged);
        }

        public Navigator(Action<FilteredGridAppearance> @delegate, IEnumerable<string> tableNames) : this()
        {
            if (@delegate != null)
            {
                @delegate(this.grid.Appearance);
            }
            if (tableNames != null)
            {
                this.m_tableNames.UnionWith(tableNames);
            }
        }

        private void btnColumns_Click(object sender, EventArgs e)
        {
            using (FormChooseColumns columns = new FormChooseColumns(this.grid.GetGrid()))
            {
                columns.StartPosition = FormStartPosition.CenterScreen;
                columns.ShowDialog();
            }
        }

        private void btnRefresh_Click(object sender, EventArgs e)
        {
            this.m_reloadQueue.Enqueue(DateTime.UtcNow.AddMilliseconds(500.0));
        }

        public void ClearNavigator()
        {
            this.grid.GridSource = null;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void DoCreateSource(CreateSourceEventArgs args)
        {
            EventHandler<CreateSourceEventArgs> handler = base.Events[m_keyCreateSource] as EventHandler<CreateSourceEventArgs>;
            if (handler != null)
            {
                handler(this, args);
            }
        }

        private void DoFillSource(FillSourceEventArgs args)
        {
            EventHandler<FillSourceEventArgs> handler = base.Events[m_keyFillSource] as EventHandler<FillSourceEventArgs>;
            if (handler != null)
            {
                DateTime utcNow = DateTime.UtcNow;
                handler(this, args);
                double totalMilliseconds = (DateTime.UtcNow - utcNow).TotalMilliseconds;
                if (1000.0 < totalMilliseconds)
                {
                    TraceHelper.TraceInfo("Navigator.FillSource: duration = " + totalMilliseconds.ToString("0"));
                }
            }
        }

        private void DoNavigatorRowClick(NavigatorRowClickEventArgs args)
        {
            EventHandler<NavigatorRowClickEventArgs> handler = base.Events[m_keyNavigatorRowClick] as EventHandler<NavigatorRowClickEventArgs>;
            if (handler != null)
            {
                handler(this, args);
            }
        }

        private void grid_RowDoubleClick(object sender, GridMouseEventArgs e)
        {
            try
            {
                this.DoNavigatorRowClick(new NavigatorRowClickEventArgs(e.Row));
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        public void HighlightReloadButton()
        {
            this.btnRefresh.BackgroundImage = DMEWorks.Properties.Resources.Reload2;
        }

        [DebuggerStepThrough]
        private void InitializeComponent()
        {
            this.components = new Container();
            ComponentResourceManager manager = new ComponentResourceManager(typeof(Navigator));
            this.grid = new FilteredGrid();
            this.txtFilter = new TextBox();
            this.worker = new BackgroundWorker();
            this.pnlFilter = new Panel();
            this.timer = new Timer(this.components);
            this.spinner = new Label();
            this.btnRefresh = new Button();
            this.btnColumns = new Button();
            this.pnlFilter.SuspendLayout();
            base.SuspendLayout();
            this.grid.Dock = DockStyle.Fill;
            this.grid.Location = new Point(0, 0x16);
            this.grid.Name = "grid";
            this.grid.Size = new Size(480, 0x112);
            this.grid.TabIndex = 1;
            this.txtFilter.BorderStyle = BorderStyle.FixedSingle;
            this.txtFilter.Location = new Point(0x30, 0);
            this.txtFilter.Name = "txtFilter";
            this.txtFilter.Size = new Size(400, 20);
            this.txtFilter.TabIndex = 1;
            this.worker.WorkerReportsProgress = true;
            this.pnlFilter.Controls.Add(this.btnRefresh);
            this.pnlFilter.Controls.Add(this.btnColumns);
            this.pnlFilter.Controls.Add(this.txtFilter);
            this.pnlFilter.Dock = DockStyle.Top;
            this.pnlFilter.Location = new Point(0, 0);
            this.pnlFilter.Name = "pnlFilter";
            this.pnlFilter.Size = new Size(480, 0x16);
            this.pnlFilter.TabIndex = 0;
            this.timer.Enabled = true;
            this.spinner.Font = new Font("Arial", 9f, FontStyle.Regular, GraphicsUnit.Point, 0xcc);
            this.spinner.Image = (Image) manager.GetObject("spinner.Image");
            this.spinner.ImageAlign = ContentAlignment.MiddleRight;
            this.spinner.Location = new Point(0xc4, 0x95);
            this.spinner.Name = "spinner";
            this.spinner.Size = new Size(0x58, 0x17);
            this.spinner.TabIndex = 3;
            this.spinner.Text = "Loading...";
            this.spinner.TextAlign = ContentAlignment.MiddleLeft;
            this.spinner.Visible = false;
            this.btnRefresh.BackgroundImage = DMEWorks.Properties.Resources.Reload2;
            this.btnRefresh.BackgroundImageLayout = ImageLayout.Center;
            this.btnRefresh.FlatStyle = FlatStyle.Flat;
            this.btnRefresh.Location = new Point(0, 0);
            this.btnRefresh.Name = "btnRefresh";
            this.btnRefresh.Size = new Size(0x18, 20);
            this.btnRefresh.TabIndex = 4;
            this.btnRefresh.TabStop = false;
            this.btnRefresh.UseVisualStyleBackColor = true;
            this.btnColumns.FlatStyle = FlatStyle.Flat;
            this.btnColumns.Image = DMEWorks.Forms.Properties.Resources.ImageColumns;
            this.btnColumns.Location = new Point(0x1c8, 0);
            this.btnColumns.Margin = new Padding(0);
            this.btnColumns.Name = "btnColumns";
            this.btnColumns.Size = new Size(0x18, 20);
            this.btnColumns.TabIndex = 3;
            this.btnColumns.TabStop = false;
            this.btnColumns.UseVisualStyleBackColor = true;
            this.btnColumns.Click += new EventHandler(this.btnColumns_Click);
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.Controls.Add(this.spinner);
            base.Controls.Add(this.grid);
            base.Controls.Add(this.pnlFilter);
            base.Name = "Navigator";
            base.Size = new Size(480, 320);
            this.pnlFilter.ResumeLayout(false);
            this.pnlFilter.PerformLayout();
            base.ResumeLayout(false);
        }

        public void LoadNavigator()
        {
            if (this.grid.GridSource == null)
            {
                this.m_reloadQueue.Enqueue(DateTime.UtcNow);
            }
        }

        private void pnlFilter_Layout(object sender, LayoutEventArgs e)
        {
            this.btnRefresh.Top = 0;
            this.txtFilter.Top = 0;
            this.btnColumns.Top = 0;
            this.btnRefresh.Left = 0;
            this.btnColumns.Left = this.pnlFilter.Width - this.btnColumns.Width;
            this.txtFilter.Left = (this.btnRefresh.Left + this.btnRefresh.Width) + 2;
            this.txtFilter.Width = Math.Max(20, (this.btnColumns.Left - this.txtFilter.Left) - 2);
        }

        private void ProcessFilterQueue()
        {
            if (this.m_filterQueue.Count != 0)
            {
                while ((0 < this.m_filterQueue.Count) && (this.m_filterQueue.Peek() < DateTime.UtcNow))
                {
                    this.m_filterQueue.Dequeue();
                }
                if (this.m_filterQueue.Count == 0)
                {
                    this.grid.FilterText = this.txtFilter.Text;
                }
            }
        }

        private void ProcessReloadQueue()
        {
            if (this.m_reloadQueue.Count != 0)
            {
                while ((0 < this.m_reloadQueue.Count) && (this.m_reloadQueue.Peek() < DateTime.UtcNow))
                {
                    this.m_reloadQueue.Dequeue();
                }
                if (0 >= this.m_reloadQueue.Count)
                {
                    if (this.worker.IsBusy)
                    {
                        this.m_reloadQueue.Enqueue(DateTime.UtcNow.AddMilliseconds(500.0));
                    }
                    else
                    {
                        CreateSourceEventArgs args = new CreateSourceEventArgs();
                        this.DoCreateSource(args);
                        this.worker.RunWorkerAsync(new PagedFillSourceEventArgs(args.Source, this.txtFilter.Text));
                    }
                }
            }
        }

        public bool ShouldHandleDatabaseChanged(string[] tableNames) => 
            this.m_tableNames.Overlaps(tableNames);

        private void timer_Tick(object sender, EventArgs e)
        {
            this.ProcessFilterQueue();
            this.ProcessReloadQueue();
        }

        private void txtFilter_TextChanged(object sender, EventArgs e)
        {
            this.m_filterQueue.Enqueue(DateTime.UtcNow.AddMilliseconds(500.0));
        }

        private void worker_DoWork(object sender, DoWorkEventArgs e)
        {
            FillSourceEventArgs argument = e.Argument as FillSourceEventArgs;
            if (argument != null)
            {
                this.worker.ReportProgress(0);
                this.DoFillSource(argument);
                e.Result = argument;
            }
        }

        private void worker_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            this.spinner.Location = new Point((base.Width - this.spinner.Width) / 2, (base.Height - this.spinner.Height) / 2);
            this.spinner.Visible = true;
        }

        private void worker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            this.spinner.Visible = false;
            if (e.Error != null)
            {
                TraceHelper.TraceException(e.Error);
            }
            else if (!e.Cancelled)
            {
                FillSourceEventArgs result = (FillSourceEventArgs) e.Result;
                this.grid.GridSource = result.Source;
                this.btnRefresh.BackgroundImage = DMEWorks.Properties.Resources.Reload;
            }
        }
    }
}


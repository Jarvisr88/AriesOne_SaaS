namespace DMEWorks.Controls
{
    using DMEWorks.Forms.Maps;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Drawing;
    using System.Runtime.CompilerServices;
    using System.Threading;
    using System.Windows.Forms;

    public class ControlAddress : UserControl
    {
        private static readonly object EventMapClick = new object();
        private static readonly object EventFindClick = new object();
        private IContainer components;
        public Button btnMaps;
        public Button btnFind;
        public Label lblCity;
        public TextBox txtZip;
        public TextBox txtState;
        public TextBox txtCity;
        public TextBox txtAddress2;
        public TextBox txtAddress1;
        public Label lblAddress;
        internal ContextMenuStrip cmsMaps;

        public static event EventHandler DefaultFindClick;

        public static event EventHandler<MapProviderEventArgs> DefaultMapClick;

        public event EventHandler FindClick
        {
            add
            {
                base.Events.AddHandler(EventFindClick, value);
            }
            remove
            {
                base.Events.RemoveHandler(EventFindClick, value);
            }
        }

        public event EventHandler<MapProviderEventArgs> MapClick
        {
            add
            {
                base.Events.AddHandler(EventMapClick, value);
            }
            remove
            {
                base.Events.RemoveHandler(EventMapClick, value);
            }
        }

        public ControlAddress()
        {
            this.InitializeComponent();
            this.txtAddress1.TextChanged += new EventHandler(this.HandleTextChanged);
            this.txtAddress2.TextChanged += new EventHandler(this.HandleTextChanged);
            this.txtCity.TextChanged += new EventHandler(this.HandleTextChanged);
            this.txtState.TextChanged += new EventHandler(this.HandleTextChanged);
            this.txtZip.TextChanged += new EventHandler(this.HandleTextChanged);
            this.btnFind.Click += new EventHandler(this.btnFind_Click);
            this.btnMaps.Click += new EventHandler(this.btnMaps_Click);
        }

        private void btnFind_Click(object sender, EventArgs args)
        {
            this.OnFindClick(EventArgs.Empty);
        }

        private void btnMaps_Click(object sender, EventArgs args)
        {
            if (this.cmsMaps.Items.Count == 0)
            {
                using (IEnumerator<MapProvider> enumerator = MapProvider.GetProviders().GetEnumerator())
                {
                    while (enumerator.MoveNext())
                    {
                        MapProviderMenuItem item = new MapProviderMenuItem(enumerator.Current, new EventHandler(this.tsmiMap_Click));
                        this.cmsMaps.Items.Add(item);
                    }
                }
            }
            this.cmsMaps.Show(this.btnMaps, new Point(0, this.btnMaps.Height));
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void HandleTextChanged(object sender, EventArgs args)
        {
            this.OnTextChanged(args);
        }

        private void InitializeComponent()
        {
            this.components = new Container();
            ComponentResourceManager manager = new ComponentResourceManager(typeof(ControlAddress));
            this.btnMaps = new Button();
            this.btnFind = new Button();
            this.lblCity = new Label();
            this.txtZip = new TextBox();
            this.txtState = new TextBox();
            this.txtCity = new TextBox();
            this.txtAddress2 = new TextBox();
            this.txtAddress1 = new TextBox();
            this.lblAddress = new Label();
            this.cmsMaps = new ContextMenuStrip(this.components);
            base.SuspendLayout();
            this.btnMaps.FlatStyle = FlatStyle.Flat;
            this.btnMaps.Image = (Image) manager.GetObject("btnMaps.Image");
            this.btnMaps.Location = new Point(0x160, 0);
            this.btnMaps.Name = "btnMaps";
            this.btnMaps.Size = new Size(0x15, 0x15);
            this.btnMaps.TabIndex = 2;
            this.btnMaps.TabStop = false;
            this.btnFind.FlatStyle = FlatStyle.Flat;
            this.btnFind.Image = (Image) manager.GetObject("btnFind.Image");
            this.btnFind.Location = new Point(0x160, 0x30);
            this.btnFind.Name = "btnFind";
            this.btnFind.Size = new Size(0x15, 0x15);
            this.btnFind.TabIndex = 6;
            this.btnFind.TabStop = false;
            this.lblCity.Location = new Point(0, 0x30);
            this.lblCity.Name = "lblCity";
            this.lblCity.Size = new Size(0x40, 0x15);
            this.lblCity.TabIndex = 4;
            this.lblCity.Text = "City, St, Zip";
            this.lblCity.TextAlign = ContentAlignment.MiddleRight;
            this.txtZip.Location = new Point(0x120, 0x30);
            this.txtZip.MaxLength = 10;
            this.txtZip.Name = "txtZip";
            this.txtZip.Size = new Size(0x40, 20);
            this.txtZip.TabIndex = 5;
            this.txtState.CharacterCasing = CharacterCasing.Upper;
            this.txtState.Location = new Point(0xf8, 0x30);
            this.txtState.MaxLength = 2;
            this.txtState.Name = "txtState";
            this.txtState.Size = new Size(0x20, 20);
            this.txtState.TabIndex = 8;
            this.txtCity.Location = new Point(0x48, 0x30);
            this.txtCity.MaxLength = 0x19;
            this.txtCity.Name = "txtCity";
            this.txtCity.Size = new Size(0xa8, 20);
            this.txtCity.TabIndex = 7;
            this.txtAddress2.Location = new Point(0x48, 0x18);
            this.txtAddress2.MaxLength = 40;
            this.txtAddress2.Name = "txtAddress2";
            this.txtAddress2.Size = new Size(0x130, 20);
            this.txtAddress2.TabIndex = 3;
            this.txtAddress1.Location = new Point(0x48, 0);
            this.txtAddress1.MaxLength = 40;
            this.txtAddress1.Name = "txtAddress1";
            this.txtAddress1.Size = new Size(280, 20);
            this.txtAddress1.TabIndex = 1;
            this.lblAddress.Location = new Point(0, 0);
            this.lblAddress.Name = "lblAddress";
            this.lblAddress.Size = new Size(0x40, 0x15);
            this.lblAddress.TabIndex = 0;
            this.lblAddress.Text = "Address";
            this.lblAddress.TextAlign = ContentAlignment.MiddleRight;
            this.cmsMaps.Name = "cmsMaps";
            this.cmsMaps.Size = new Size(0x3d, 4);
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.Controls.Add(this.btnMaps);
            base.Controls.Add(this.btnFind);
            base.Controls.Add(this.lblCity);
            base.Controls.Add(this.txtZip);
            base.Controls.Add(this.txtState);
            base.Controls.Add(this.txtCity);
            base.Controls.Add(this.txtAddress2);
            base.Controls.Add(this.txtAddress1);
            base.Controls.Add(this.lblAddress);
            base.Name = "ControlAddress";
            base.Size = new Size(0x178, 0x48);
            base.ResumeLayout(false);
            base.PerformLayout();
        }

        private void OnFindClick(EventArgs args)
        {
            EventHandler handler = base.Events[EventFindClick] as EventHandler;
            if (handler != null)
            {
                handler(this, args);
            }
            else
            {
                EventHandler defaultFindClick = DefaultFindClick;
                if (defaultFindClick != null)
                {
                    defaultFindClick(this, args);
                }
            }
        }

        protected override void OnLayout(LayoutEventArgs e)
        {
            base.OnLayout(e);
            int width = base.Width;
            if (this.btnMaps.Visible)
            {
                this.btnMaps.Left = width - this.btnMaps.Width;
                width = (width - this.btnMaps.Width) - 1;
            }
            this.txtAddress1.Width = Math.Max(width - this.txtAddress1.Left, 8);
            width = base.Width;
            this.txtAddress2.Width = Math.Max(width - this.txtAddress2.Left, 8);
            width = base.Width;
            if (this.btnFind.Visible)
            {
                this.btnFind.Left = width - this.btnFind.Width;
                width = (width - this.btnFind.Width) - 1;
            }
            this.txtZip.Left = width - this.txtZip.Width;
            width = (width - this.txtZip.Width) - 4;
            this.txtState.Left = width - this.txtState.Width;
            width = (width - this.txtState.Width) - 4;
            this.txtCity.Width = Math.Max(width - this.txtCity.Left, 8);
        }

        private void OnMapClick(MapProviderEventArgs args)
        {
            EventHandler<MapProviderEventArgs> handler = base.Events[EventMapClick] as EventHandler<MapProviderEventArgs>;
            if (handler != null)
            {
                handler(this, args);
            }
            else
            {
                EventHandler<MapProviderEventArgs> defaultMapClick = DefaultMapClick;
                if (defaultMapClick != null)
                {
                    defaultMapClick(this, args);
                }
            }
        }

        private void tsmiMap_Click(object sender, EventArgs args)
        {
            MapProviderMenuItem item = sender as MapProviderMenuItem;
            if (item != null)
            {
                this.OnMapClick(new MapProviderEventArgs(item.Provider));
            }
        }

        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden), Browsable(false)]
        public bool ReadOnly
        {
            get => 
                this.txtAddress1.ReadOnly && (this.txtAddress2.ReadOnly && (this.txtCity.ReadOnly && (this.txtState.ReadOnly && this.txtZip.ReadOnly)));
            set
            {
                this.txtAddress1.ReadOnly = value;
                this.txtAddress2.ReadOnly = value;
                this.txtCity.ReadOnly = value;
                this.txtState.ReadOnly = value;
                this.txtZip.ReadOnly = value;
            }
        }

        public DMEWorks.Forms.Maps.Address Address =>
            new DMEWorks.Forms.Maps.Address(this.txtAddress1.Text, this.txtAddress2.Text, this.txtCity.Text, this.txtState.Text, this.txtZip.Text);
    }
}


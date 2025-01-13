namespace DMEWorks.Core
{
    using DMEWorks;
    using DMEWorks.Controls;
    using DMEWorks.Data;
    using DMEWorks.Forms;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Diagnostics;
    using System.Drawing;
    using System.Runtime.CompilerServices;
    using System.Windows.Forms;

    public class FormMaintainBase : DmeForm, IParameters
    {
        protected const string CrLf = "\r\n";
        protected readonly bool _ButtonClone;
        protected readonly bool _ButtonClose;
        protected readonly bool _ButtonDelete;
        protected readonly bool _ButtonMissing;
        protected readonly bool _ButtonNew;
        protected readonly bool _ButtonReload;
        private readonly Stack<FormState> FStateStack = new Stack<FormState>();
        private readonly DMEWorks.Controls.ChangesTracker m_changesTracker;
        private int m_changeCount;
        private static readonly object HANDLER_ENTITYSAVED = new object();
        private IContainer components;
        private ImageList imglButtons;
        private ToolBarButton tbbClose;
        private ToolBarButton tbbDelete;
        private ToolBarButton tbbNew;
        private ToolBarButton tbbSave;
        private ToolBarButton tbbSearch;
        private ToolBarButton tbbPrint;
        private ToolBarButton tbbGoto;
        private ToolBarButton tbbClone;
        private ToolBarButton tbbActions;
        private ToolBarButton tbbFilter;
        private ToolBarButton tbbReload;
        private ToolBarButton tbbMissing;
        private ToolBar tlbMain;
        private TabControl PageControl;
        protected TabPage tpWorkArea;
        protected ToolTip ToolTip1;
        protected ErrorProvider ValidationErrors;
        protected ErrorProvider ValidationWarnings;
        protected ErrorProvider MissingData;
        protected ContextMenu cmnuGoto;
        protected ContextMenu cmnuActions;
        protected ContextMenu cmnuFilter;
        private Label lblChanged;
        private const string ReloadQuestion = "You are about to reload objest from database.\r\nYour changes will be dismissed.\r\n\r\nAre you sure you want to proceed?";

        public event EventHandler<EntityCreatedEventArgs> EntityCreated
        {
            add
            {
                base.Events.AddHandler(HANDLER_ENTITYSAVED, value);
            }
            remove
            {
                base.Events.RemoveHandler(HANDLER_ENTITYSAVED, value);
            }
        }

        public FormMaintainBase()
        {
            this.InitializeComponent();
            this.PageControl.SelectedIndexChanged += new EventHandler(this.PageControl_SelectedIndexChanged);
            this.tlbMain.ButtonClick += new ToolBarButtonClickEventHandler(this.ToolBar_ButtonClick);
            ButtonsAttribute customAttribute = (ButtonsAttribute) Attribute.GetCustomAttribute(base.GetType(), typeof(ButtonsAttribute));
            customAttribute ??= ButtonsAttribute.Default;
            this._ButtonClone = customAttribute.ButtonClone;
            this._ButtonClose = customAttribute.ButtonClose;
            this._ButtonDelete = customAttribute.ButtonDelete;
            this._ButtonMissing = customAttribute.ButtonMissing;
            this._ButtonNew = customAttribute.ButtonNew;
            this._ButtonReload = customAttribute.ButtonReload;
            this.tbbClone.Visible = this._ButtonClone;
            this.tbbClone.Enabled = this._ButtonClone;
            this.tbbClose.Visible = this._ButtonClose;
            this.tbbClose.Enabled = this._ButtonClose;
            this.tbbDelete.Visible = this._ButtonDelete;
            this.tbbDelete.Enabled = this._ButtonDelete;
            this.tbbMissing.Visible = this._ButtonMissing;
            this.tbbMissing.Enabled = this._ButtonMissing;
            this.tbbNew.Visible = this._ButtonNew;
            this.tbbNew.Enabled = this._ButtonNew;
            this.tbbSave.Visible = true;
            this.tbbSave.Enabled = true;
            this.tbbSearch.Visible = true;
            this.tbbSearch.Enabled = true;
            this.tbbPrint.Visible = false;
            this.tbbPrint.Enabled = false;
            this.m_changesTracker = new DMEWorks.Controls.ChangesTracker(new EventHandler(this.HandleControlChanged));
        }

        public TabPage AddNavigator(NavigatorOptions options)
        {
            if (options == null)
            {
                throw new ArgumentException("options");
            }
            Navigator navigator1 = new Navigator((Action<FilteredGridAppearance>) options.InitializeAppearance, options.TableNames);
            navigator1.Dock = DockStyle.Fill;
            Navigator navigator = navigator1;
            if (options.CreateSource != null)
            {
                navigator.CreateSource += options.CreateSource;
            }
            if (options.FillSource != null)
            {
                navigator.FillSource += options.FillSource;
            }
            if (options.NavigatorRowClick != null)
            {
                navigator.NavigatorRowClick += options.NavigatorRowClick;
            }
            NavigatorTabPage page1 = new NavigatorTabPage();
            page1.Text = options.Caption;
            page1.Switchable = options.Switchable;
            NavigatorTabPage page = page1;
            page.Controls.Add(navigator);
            this.PageControl.TabPages.Add(page);
            return page;
        }

        public TabPage AddPagedNavigator(NavigatorEventsHandler handler)
        {
            if (handler == null)
            {
                throw new ArgumentException("handler");
            }
            PagedNavigator navigator1 = new PagedNavigator(new Action<FilteredGridAppearance>(handler.InitializeAppearance), handler.TableNames);
            navigator1.Dock = DockStyle.Fill;
            PagedNavigator navigator = navigator1;
            navigator.CreateSource += new EventHandler<CreateSourceEventArgs>(handler.CreateSource);
            navigator.FillSource += new EventHandler<PagedFillSourceEventArgs>(handler.FillSource);
            navigator.NavigatorRowClick += new EventHandler<NavigatorRowClickEventArgs>(handler.NavigatorRowClick);
            NavigatorTabPage page1 = new NavigatorTabPage();
            page1.Text = handler.Caption;
            page1.Switchable = handler.Switchable;
            NavigatorTabPage page = page1;
            page.Controls.Add(navigator);
            this.PageControl.TabPages.Add(page);
            return page;
        }

        public TabPage AddSimpleNavigator(NavigatorEventsHandler handler)
        {
            if (handler == null)
            {
                throw new ArgumentException("handler");
            }
            Navigator navigator1 = new Navigator(new Action<FilteredGridAppearance>(handler.InitializeAppearance), handler.TableNames);
            navigator1.Dock = DockStyle.Fill;
            Navigator navigator = navigator1;
            navigator.CreateSource += new EventHandler<CreateSourceEventArgs>(handler.CreateSource);
            navigator.FillSource += new EventHandler<FillSourceEventArgs>(handler.FillSource);
            navigator.NavigatorRowClick += new EventHandler<NavigatorRowClickEventArgs>(handler.NavigatorRowClick);
            NavigatorTabPage page1 = new NavigatorTabPage();
            page1.Text = handler.Caption;
            page1.Switchable = handler.Switchable;
            NavigatorTabPage page = page1;
            page.Controls.Add(navigator);
            this.PageControl.TabPages.Add(page);
            return page;
        }

        protected void AddToolbarButton(ToolBarButton button, EventHandler handler)
        {
            if (button == null)
            {
                throw new ArgumentNullException("button");
            }
            if (handler == null)
            {
                throw new ArgumentNullException("handler");
            }
            this.tlbMain.Buttons.Add(button);
            this.tlbMain.ButtonClick += delegate (object sender, ToolBarButtonClickEventArgs args) {
                if (ReferenceEquals(args.Button, button))
                {
                    handler(button, EventArgs.Empty);
                }
            };
            this.tlbMain.ButtonDropDown += delegate (object sender, ToolBarButtonClickEventArgs args) {
                if (ReferenceEquals(args.Button, button))
                {
                    handler(button, EventArgs.Empty);
                }
            };
        }

        [DebuggerNonUserCode]
        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        void IParameters.SetParameters(FormParameters parameters)
        {
            if (parameters != null)
            {
                this.SetParameters(parameters);
            }
        }

        protected virtual void DoCloneClick()
        {
            if (this.SaveOrCancelChanges())
            {
                this.WrappedCloneObject();
                this.SwitchToWorkArea();
            }
        }

        protected void DoCloseClick()
        {
            base.Close();
        }

        protected void DoDeleteClick()
        {
            this.WrappedDeleteObject();
        }

        protected void DoNewClick()
        {
            if (this.SaveOrCancelChanges())
            {
                this.WrappedClearObject();
                this.SwitchToWorkArea();
            }
        }

        protected void DoReloadClick()
        {
            ExistingObjectInfo currentObjectInfo = this.GetCurrentObjectInfo() as ExistingObjectInfo;
            if ((currentObjectInfo != null) && (!this.HasUnsavedChanges || (MessageBox.Show("You are about to reload objest from database.\r\nYour changes will be dismissed.\r\n\r\nAre you sure you want to proceed?", this.Text, MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.No)))
            {
                this.WrappedLoadObject(currentObjectInfo.Key);
            }
        }

        protected void DoSaveClick()
        {
            this.WrappedSaveObject();
        }

        protected void DoSearchClick()
        {
            this.PageControl.SelectedIndex = GetNextSwitchable(this.PageControl.TabPages, this.PageControl.SelectedIndex);
        }

        protected void DoShowMissingInformation()
        {
            this.WrappedShowMissingInformation();
        }

        protected bool GetConfirmation(string confirmationText) => 
            MessageBox.Show(confirmationText, this.Text, MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2) == DialogResult.Yes;

        protected bool GetConfirmation(string format, object arg0) => 
            this.GetConfirmation(string.Format(format, arg0));

        protected virtual ObjectInfo GetCurrentObjectInfo()
        {
            throw new NotImplementedException();
        }

        protected virtual StandardMessages GetMessages()
        {
            StandardMessages messages1 = new StandardMessages();
            messages1.InsufficientPermissionsToDelete = "You do not have permissions to Delete Objects";
            messages1.InsufficientPermissionsToSave = "You do not have permissions to Add or Edit Objects";
            messages1.ConfirmDeleting = "You are about to delete object.\r\nAre you sure you want to proceed?";
            messages1.DeletedSuccessfully = "Object have been successfully deleted from database";
            messages1.DeleteObjectDeadlock = "Deadlock found when trying to delete object from database.\r\ntry to delete once again a bit later";
            messages1.ObjectToBeDeletedIsModified = "Object cannot be deleted since it was modified.\r\nTo proceed you have to reload it and try to delete again.\r\nWould you like to reload it?";
            messages1.ObjectToBeDeletedIsNotFound = "Object cannot be deleted since it cannot be found in database.";
            messages1.SaveObjectDeadlock = "Deadlock found when trying to delete object from database.\r\ntry to delete once again a bit later";
            messages1.ObjectToBeInsertedAlreadyExists = "Object cannot be inserted since it was already inserted.\r\nTo proceed you either have to reload it and redo your changes or have to save using different key.\r\n\r\nWould you like to reload it?";
            messages1.ObjectToBeSelectedIsNotFound = "Object cannot be loaded since it cannot be found in database.";
            messages1.DuplicateKey = "Changes to object cannot be saved since object with new value of key already exists.";
            messages1.ObjectToBeUpdatedIsModified = "Changes to object cannot be saved since it was modified in the database.\r\nTo proceed you have to reload it and redo your changes.\r\nWould you like to reload it?";
            messages1.ObjectToBeUpdatedIsNotFound = "Changes to object cannot be saved since it cannot be found in the database.\r\nTo proceed you either have to mark new it or dismiss your changes.\r\nWould you like to mark it as new?";
            return messages1;
        }

        private static int GetNextSwitchable(TabControl.TabPageCollection pages, int index)
        {
            int count = pages.Count;
            for (int i = 1; i < count; i++)
            {
                int num3 = ((count - i) + index) % count;
                NavigatorTabPage page = pages[num3] as NavigatorTabPage;
                if ((page != null) && page.Switchable)
                {
                    return num3;
                }
            }
            return index;
        }

        protected void HandleControlChanged(object sender, EventArgs args)
        {
            this.ChangeCount++;
        }

        public void HandleDatabaseChanged(string[] tableNames, bool local)
        {
            if ((tableNames != null) && (tableNames.Length != 0))
            {
                foreach (TabPage page in this.PageControl.TabPages)
                {
                    if (page.Controls.Count != 0)
                    {
                        Control control = page.Controls[0];
                        Navigator navigator = control as Navigator;
                        if (navigator != null)
                        {
                            if (!navigator.ShouldHandleDatabaseChanged(tableNames))
                            {
                                continue;
                            }
                            if (local)
                            {
                                navigator.ClearNavigator();
                                continue;
                            }
                            navigator.HighlightReloadButton();
                            continue;
                        }
                        PagedNavigator navigator2 = control as PagedNavigator;
                        if ((navigator2 != null) && navigator2.ShouldHandleDatabaseChanged(tableNames))
                        {
                            if (local)
                            {
                                navigator2.ClearNavigator();
                                continue;
                            }
                            navigator2.HighlightReloadButton();
                        }
                    }
                }
                this.LoadObjectList();
            }
        }

        [DebuggerStepThrough]
        private void InitializeComponent()
        {
            this.components = new Container();
            ComponentResourceManager manager = new ComponentResourceManager(typeof(FormMaintainBase));
            this.tlbMain = new ToolBar();
            this.tbbReload = new ToolBarButton();
            this.tbbSearch = new ToolBarButton();
            this.tbbNew = new ToolBarButton();
            this.tbbClone = new ToolBarButton();
            this.tbbSave = new ToolBarButton();
            this.tbbDelete = new ToolBarButton();
            this.tbbPrint = new ToolBarButton();
            this.tbbGoto = new ToolBarButton();
            this.cmnuGoto = new ContextMenu();
            this.tbbActions = new ToolBarButton();
            this.cmnuActions = new ContextMenu();
            this.tbbFilter = new ToolBarButton();
            this.cmnuFilter = new ContextMenu();
            this.tbbMissing = new ToolBarButton();
            this.tbbClose = new ToolBarButton();
            this.imglButtons = new ImageList(this.components);
            this.PageControl = new TabControl();
            this.tpWorkArea = new TabPage();
            this.ToolTip1 = new ToolTip(this.components);
            this.ValidationErrors = new ErrorProvider(this.components);
            this.lblChanged = new Label();
            this.ValidationWarnings = new ErrorProvider(this.components);
            this.MissingData = new ErrorProvider(this.components);
            this.PageControl.SuspendLayout();
            ((ISupportInitialize) this.ValidationErrors).BeginInit();
            ((ISupportInitialize) this.ValidationWarnings).BeginInit();
            ((ISupportInitialize) this.MissingData).BeginInit();
            base.SuspendLayout();
            this.tlbMain.Appearance = ToolBarAppearance.Flat;
            this.tlbMain.BorderStyle = BorderStyle.FixedSingle;
            ToolBarButton[] buttons = new ToolBarButton[12];
            buttons[0] = this.tbbReload;
            buttons[1] = this.tbbSearch;
            buttons[2] = this.tbbNew;
            buttons[3] = this.tbbClone;
            buttons[4] = this.tbbSave;
            buttons[5] = this.tbbDelete;
            buttons[6] = this.tbbPrint;
            buttons[7] = this.tbbGoto;
            buttons[8] = this.tbbActions;
            buttons[9] = this.tbbFilter;
            buttons[10] = this.tbbMissing;
            buttons[11] = this.tbbClose;
            this.tlbMain.Buttons.AddRange(buttons);
            this.tlbMain.Divider = false;
            this.tlbMain.DropDownArrows = true;
            this.tlbMain.ImageList = this.imglButtons;
            this.tlbMain.Location = new Point(0, 0);
            this.tlbMain.Name = "tlbMain";
            this.tlbMain.ShowToolTips = true;
            this.tlbMain.Size = new Size(0x248, 0x31);
            this.tlbMain.TabIndex = 0;
            this.tbbReload.ImageKey = "ImageRefresh";
            this.tbbReload.Name = "tbbReload";
            this.tbbReload.Text = "Reload";
            this.tbbSearch.ImageKey = "ImageFind";
            this.tbbSearch.Name = "tbbSearch";
            this.tbbSearch.Text = "Search";
            this.tbbNew.ImageKey = "ImageNew";
            this.tbbNew.Name = "tbbNew";
            this.tbbNew.Text = "New";
            this.tbbClone.ImageKey = "ImageClone";
            this.tbbClone.Name = "tbbClone";
            this.tbbClone.Text = "Clone";
            this.tbbSave.ImageKey = "ImageSave";
            this.tbbSave.Name = "tbbSave";
            this.tbbSave.Text = "Save";
            this.tbbDelete.ImageKey = "ImageDelete";
            this.tbbDelete.Name = "tbbDelete";
            this.tbbDelete.Text = "Delete";
            this.tbbPrint.ImageKey = "ImagePrint";
            this.tbbPrint.Name = "tbbPrint";
            this.tbbPrint.Style = ToolBarButtonStyle.DropDownButton;
            this.tbbPrint.Text = "Print";
            this.tbbGoto.DropDownMenu = this.cmnuGoto;
            this.tbbGoto.ImageKey = "ImageGoto";
            this.tbbGoto.Name = "tbbGoto";
            this.tbbGoto.Style = ToolBarButtonStyle.DropDownButton;
            this.tbbGoto.Text = "Go To";
            this.tbbActions.DropDownMenu = this.cmnuActions;
            this.tbbActions.ImageKey = "ImageAction";
            this.tbbActions.Name = "tbbActions";
            this.tbbActions.Style = ToolBarButtonStyle.DropDownButton;
            this.tbbActions.Text = "Actions";
            this.tbbFilter.DropDownMenu = this.cmnuFilter;
            this.tbbFilter.ImageKey = "ImageFilter";
            this.tbbFilter.Name = "tbbFilter";
            this.tbbFilter.Style = ToolBarButtonStyle.DropDownButton;
            this.tbbFilter.Text = "Filter";
            this.tbbMissing.ImageKey = "Missing";
            this.tbbMissing.Name = "tbbMissingInformation";
            this.tbbMissing.Style = ToolBarButtonStyle.ToggleButton;
            this.tbbMissing.Text = "Missing";
            this.tbbClose.ImageKey = "ImageClose";
            this.tbbClose.Name = "tbbClose";
            this.tbbClose.Text = "Close";
            this.imglButtons.ImageStream = (ImageListStreamer) manager.GetObject("imglButtons.ImageStream");
            this.imglButtons.TransparentColor = Color.Magenta;
            this.imglButtons.Images.SetKeyName(0, "ImageClose");
            this.imglButtons.Images.SetKeyName(1, "");
            this.imglButtons.Images.SetKeyName(2, "");
            this.imglButtons.Images.SetKeyName(3, "");
            this.imglButtons.Images.SetKeyName(4, "");
            this.imglButtons.Images.SetKeyName(5, "");
            this.imglButtons.Images.SetKeyName(6, "");
            this.imglButtons.Images.SetKeyName(7, "");
            this.imglButtons.Images.SetKeyName(8, "");
            this.imglButtons.Images.SetKeyName(9, "");
            this.imglButtons.Images.SetKeyName(10, "");
            this.imglButtons.Images.SetKeyName(11, "");
            this.imglButtons.Images.SetKeyName(12, "");
            this.imglButtons.Images.SetKeyName(13, "");
            this.imglButtons.Images.SetKeyName(14, "");
            this.imglButtons.Images.SetKeyName(15, "");
            this.imglButtons.Images.SetKeyName(0x10, "");
            this.imglButtons.Images.SetKeyName(0x11, "");
            this.imglButtons.Images.SetKeyName(0x12, "");
            this.imglButtons.Images.SetKeyName(0x13, "");
            this.imglButtons.Images.SetKeyName(20, "");
            this.imglButtons.Images.SetKeyName(0x15, "");
            this.imglButtons.Images.SetKeyName(0x16, "");
            this.imglButtons.Images.SetKeyName(0x17, "");
            this.imglButtons.Images.SetKeyName(0x18, "Missing");
            this.imglButtons.Images.SetKeyName(0x19, "ImageAction");
            this.imglButtons.Images.SetKeyName(0x1a, "ImagePrint");
            this.imglButtons.Images.SetKeyName(0x1b, "ImageSave");
            this.imglButtons.Images.SetKeyName(0x1c, "ImageFind");
            this.imglButtons.Images.SetKeyName(0x1d, "ImageNew");
            this.imglButtons.Images.SetKeyName(30, "ImageDelete");
            this.imglButtons.Images.SetKeyName(0x1f, "ImageClone");
            this.imglButtons.Images.SetKeyName(0x20, "ImageGoto");
            this.imglButtons.Images.SetKeyName(0x21, "ImageFilter");
            this.imglButtons.Images.SetKeyName(0x22, "ImageRefresh");
            this.PageControl.Alignment = TabAlignment.Bottom;
            this.PageControl.Controls.Add(this.tpWorkArea);
            this.PageControl.Dock = DockStyle.Fill;
            this.PageControl.Location = new Point(0, 0x31);
            this.PageControl.Name = "PageControl";
            this.PageControl.SelectedIndex = 0;
            this.PageControl.Size = new Size(0x248, 0x158);
            this.PageControl.TabIndex = 1;
            this.tpWorkArea.Location = new Point(4, 4);
            this.tpWorkArea.Name = "tpWorkArea";
            this.tpWorkArea.Size = new Size(0x240, 0x13e);
            this.tpWorkArea.TabIndex = 0;
            this.tpWorkArea.Text = "Work Area";
            this.ValidationErrors.ContainerControl = this;
            this.ValidationErrors.DataMember = "";
            this.lblChanged.Font = new Font("Tahoma", 8.25f, FontStyle.Bold, GraphicsUnit.Point, 0xcc);
            this.lblChanged.ForeColor = Color.Red;
            this.lblChanged.Location = new Point(0x1e1, 0x178);
            this.lblChanged.Name = "lblChanged";
            this.lblChanged.Size = new Size(100, 0x10);
            this.lblChanged.TabIndex = 2;
            this.lblChanged.Text = "Changed";
            this.lblChanged.TextAlign = ContentAlignment.BottomRight;
            this.lblChanged.Visible = false;
            this.ValidationWarnings.ContainerControl = this;
            this.ValidationWarnings.DataMember = "";
            this.ValidationWarnings.Icon = (Icon) manager.GetObject("ValidationWarnings.Icon");
            this.MissingData.ContainerControl = this;
            this.MissingData.DataMember = "";
            this.MissingData.Icon = (Icon) manager.GetObject("MissingProvider.Icon");
            this.AutoScaleBaseSize = new Size(5, 13);
            base.ClientSize = new Size(0x248, 0x189);
            base.Controls.Add(this.lblChanged);
            base.Controls.Add(this.PageControl);
            base.Controls.Add(this.tlbMain);
            base.KeyPreview = true;
            base.Name = "FormMaintainBase";
            base.ShowInTaskbar = false;
            this.Text = "Form Maintain";
            this.PageControl.ResumeLayout(false);
            ((ISupportInitialize) this.ValidationErrors).EndInit();
            ((ISupportInitialize) this.ValidationWarnings).EndInit();
            ((ISupportInitialize) this.MissingData).EndInit();
            base.ResumeLayout(false);
            base.PerformLayout();
        }

        protected virtual void InitPrintMenu()
        {
        }

        protected virtual void InvalidateObjectList()
        {
            foreach (TabPage page in this.PageControl.TabPages)
            {
                if (page.Controls.Count != 0)
                {
                    Control control = page.Controls[0];
                    Navigator navigator = control as Navigator;
                    if (navigator != null)
                    {
                        navigator.ClearNavigator();
                        continue;
                    }
                    PagedNavigator navigator2 = control as PagedNavigator;
                    if (navigator2 != null)
                    {
                        navigator2.ClearNavigator();
                    }
                }
            }
            this.LoadObjectList();
        }

        protected void LoadObjectList()
        {
            TabPage selectedTab = this.PageControl.SelectedTab;
            if (selectedTab.Controls.Count != 0)
            {
                Control control = selectedTab.Controls[0];
                Navigator navigator = control as Navigator;
                if (navigator != null)
                {
                    navigator.LoadNavigator();
                }
                else
                {
                    PagedNavigator navigator2 = control as PagedNavigator;
                    if (navigator2 != null)
                    {
                        navigator2.LoadNavigator();
                    }
                }
            }
        }

        [HandleDatabaseChanged("tbl_crystalreport")]
        private void LoadTableCrystalReport()
        {
            this.InitPrintMenu();
        }

        protected void NotifyUser(string notificationText)
        {
            MessageBox.Show(notificationText, this.Text, MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
        }

        protected void NotifyUser(string format, object arg0)
        {
            this.NotifyUser(string.Format(format, arg0));
        }

        protected override void OnClosing(CancelEventArgs args)
        {
            base.OnClosing(args);
            args.Cancel ??= !this.SaveOrCancelChanges();
        }

        protected override void OnKeyDown(KeyEventArgs args)
        {
            base.OnKeyDown(args);
            if ((args.KeyCode == Keys.S) && args.Control)
            {
                this.DoSaveClick();
            }
            else if ((args.KeyCode == Keys.N) && args.Control)
            {
                this.DoNewClick();
            }
            else if ((args.KeyCode == Keys.F) && args.Control)
            {
                this.DoSearchClick();
            }
        }

        protected override void OnLayout(LayoutEventArgs args)
        {
            base.OnLayout(args);
            Size clientSize = base.ClientSize;
            Size size = this.lblChanged.Size;
            this.lblChanged.Location = new Point(clientSize.Width - size.Width, clientSize.Height - size.Height);
        }

        protected override void OnLoad(EventArgs args)
        {
            base.OnLoad(args);
            this.tbbGoto.Visible = 0 < this.cmnuGoto.MenuItems.Count;
            this.tbbActions.Visible = 0 < this.cmnuActions.MenuItems.Count;
            this.tbbFilter.Visible = 0 < this.cmnuFilter.MenuItems.Count;
            this.SafeInvoke(new Action(this.InitPrintMenu));
            this.SafeInvoke(new Action(this.InvalidateObjectList));
            this.WrappedClearObject();
        }

        protected void OnObjectChanged(object sender)
        {
            this.ChangeCount++;
        }

        protected virtual void OnTableUpdate()
        {
        }

        protected void OpenObject(Func<object> factory)
        {
            if (factory == null)
            {
                throw new ArgumentNullException("factory");
            }
            try
            {
                this.OpenObject(factory());
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        protected void OpenObject(object key)
        {
            if (this.SaveOrCancelChanges() && this.WrappedLoadObject(key))
            {
                this.SwitchToWorkArea();
            }
        }

        private void PageControl_SelectedIndexChanged(object sender, EventArgs args)
        {
            this.LoadObjectList();
        }

        protected virtual void PrivateClearObject()
        {
            if (!base.DesignMode)
            {
                throw new NotImplementedException();
            }
        }

        protected virtual void PrivateCloneObject()
        {
            if (!base.DesignMode)
            {
                throw new NotImplementedException();
            }
        }

        protected virtual void PrivateDeleteObject()
        {
            if (!base.DesignMode)
            {
                throw new NotImplementedException();
            }
        }

        protected virtual void PrivateLoadObject(object key)
        {
            if (!base.DesignMode)
            {
                throw new NotImplementedException();
            }
        }

        protected virtual bool PrivateSaveObject()
        {
            throw new NotImplementedException();
        }

        protected void ProcessParameter_EntityCreatedListener(FormParameters parameters)
        {
            if (parameters != null)
            {
                IEntityCreatedEventListener listener = parameters["EntityCreatedListener"] as IEntityCreatedEventListener;
                if (listener != null)
                {
                    this.EntityCreated += new EventHandler<EntityCreatedEventArgs>(listener.Handle);
                    listener.Unhook += delegate (object sender, EventArgs args) {
                        this.EntityCreated -= new EventHandler<EntityCreatedEventArgs>(listener.Handle);
                    };
                }
            }
        }

        protected void ProcessParameter_ShowMissing(FormParameters parameters)
        {
            if ((parameters != null) && parameters.ContainsKey("ShowMissing"))
            {
                this.tbbMissing.Pushed = true;
                this.DoShowMissingInformation();
            }
        }

        protected void ProcessParameter_TabPage(FormParameters parameters)
        {
            if (parameters != null)
            {
                string a = parameters["TabPage"] as string;
                foreach (TabPage page in this.PageControl.TabPages)
                {
                    if (string.Equals(a, page.Text, StringComparison.OrdinalIgnoreCase))
                    {
                        this.PageControl.SelectedTab = page;
                        break;
                    }
                }
            }
        }

        protected virtual void RaiseEntityCreated(EntityCreatedEventArgs args)
        {
            EventHandler<EntityCreatedEventArgs> handler = base.Events[HANDLER_ENTITYSAVED] as EventHandler<EntityCreatedEventArgs>;
            if (handler != null)
            {
                handler(this, args);
            }
        }

        protected void ResetChangeCount()
        {
            this.ChangeCount = 0;
        }

        protected bool SaveOrCancelChanges()
        {
            if (!this.HasUnsavedChanges)
            {
                return true;
            }
            DialogResult result = MessageBox.Show("Do you want to save changes?", this.Text, MessageBoxButtons.YesNoCancel, MessageBoxIcon.Question);
            return ((result != DialogResult.Cancel) && ((result != DialogResult.Yes) || this.WrappedSaveObject()));
        }

        protected virtual void SetParameters(FormParameters parameters)
        {
            this.ProcessParameter_EntityCreatedListener(parameters);
            this.ProcessParameter_TabPage(parameters);
        }

        protected void SetPrintMenu(ContextMenu menu)
        {
            bool flag = (menu != null) && (0 < menu.MenuItems.Count);
            this.tbbPrint.DropDownMenu = menu;
            this.tbbPrint.Visible = flag;
            this.tbbPrint.Enabled = flag;
        }

        protected virtual void ShowMissingInformation(bool show)
        {
        }

        protected void SwitchToTabPage(TabPage page)
        {
            if (page == null)
            {
                TabPage local1 = page;
                throw new ArgumentNullException("page");
            }
            this.PageControl.SelectedTab = page;
        }

        protected void SwitchToWorkArea()
        {
            this.PageControl.SelectedTab = this.tpWorkArea;
        }

        private void ToolBar_ButtonClick(object sender, ToolBarButtonClickEventArgs e)
        {
            if (ReferenceEquals(e.Button, this.tbbClose))
            {
                this.DoCloseClick();
            }
            else if (ReferenceEquals(e.Button, this.tbbDelete))
            {
                this.DoDeleteClick();
            }
            else if (ReferenceEquals(e.Button, this.tbbNew))
            {
                this.DoNewClick();
            }
            else if (ReferenceEquals(e.Button, this.tbbClone))
            {
                this.DoCloneClick();
            }
            else if (ReferenceEquals(e.Button, this.tbbReload))
            {
                this.DoReloadClick();
            }
            else if (ReferenceEquals(e.Button, this.tbbSave))
            {
                this.DoSaveClick();
            }
            else if (ReferenceEquals(e.Button, this.tbbSearch))
            {
                this.DoSearchClick();
            }
            else if (ReferenceEquals(e.Button, this.tbbMissing))
            {
                this.DoShowMissingInformation();
            }
        }

        private void WrappedClearObject()
        {
            this.FStateStack.Push(FormState.ClearingData);
            try
            {
                try
                {
                    this.PrivateClearObject();
                }
                catch (Exception exception)
                {
                    this.ShowException(exception, "Clear Error");
                    return;
                }
                this.ResetChangeCount();
                this.WrappedShowMissingInformation();
                Application.DoEvents();
            }
            finally
            {
                this.FStateStack.Pop();
            }
        }

        private void WrappedCloneObject()
        {
            this.FStateStack.Push(FormState.CloningData);
            try
            {
                try
                {
                    this.PrivateCloneObject();
                }
                catch (Exception exception)
                {
                    this.ShowException(exception, "Clone Error");
                    return;
                }
                this.ResetChangeCount();
                this.WrappedShowMissingInformation();
                Application.DoEvents();
            }
            finally
            {
                this.FStateStack.Pop();
            }
        }

        private void WrappedDeleteObject()
        {
            StandardMessages messages = this.GetMessages();
            this.FStateStack.Push(FormState.DeletingData);
            try
            {
                if (this.Permissions.Allow_DELETE)
                {
                    if ((this.GetCurrentObjectInfo() is ExistingObjectInfo) && this.GetConfirmation(messages.ConfirmDeleting))
                    {
                        try
                        {
                            this.PrivateDeleteObject();
                        }
                        catch (ObjectIsModifiedException exception1)
                        {
                            TraceHelper.TraceException(exception1);
                            if (this.GetConfirmation(messages.ObjectToBeDeletedIsModified))
                            {
                                ExistingObjectInfo info;
                                this.WrappedLoadObject(info.Key);
                            }
                            return;
                        }
                        catch (ObjectIsNotFoundException exception2)
                        {
                            TraceHelper.TraceException(exception2);
                            this.NotifyUser(messages.ObjectToBeDeletedIsNotFound);
                            this.WrappedClearObject();
                            return;
                        }
                        catch (DeadlockException exception3)
                        {
                            TraceHelper.TraceException(exception3);
                            this.NotifyUser(messages.DeleteObjectDeadlock);
                            return;
                        }
                        catch (Exception exception)
                        {
                            this.ShowException(exception, "Delete Error");
                            return;
                        }
                        this.OnTableUpdate();
                        this.WrappedClearObject();
                        this.NotifyUser(messages.DeletedSuccessfully);
                        Application.DoEvents();
                    }
                }
                else
                {
                    this.NotifyUser(messages.InsufficientPermissionsToDelete);
                }
            }
            finally
            {
                this.FStateStack.Pop();
            }
        }

        private bool WrappedLoadObject(object key)
        {
            bool flag;
            StandardMessages messages = this.GetMessages();
            this.FStateStack.Push(FormState.LoadingData);
            try
            {
                try
                {
                    this.PrivateLoadObject(key);
                    goto TR_0005;
                }
                catch (ObjectIsNotFoundException exception1)
                {
                    TraceHelper.TraceException(exception1);
                    this.NotifyUser(messages.ObjectToBeSelectedIsNotFound);
                    this.WrappedClearObject();
                    flag = false;
                }
                catch (Exception exception)
                {
                    this.ShowException(exception, "Load Error");
                    flag = false;
                }
                return flag;
            TR_0005:
                this.ResetChangeCount();
                this.WrappedShowMissingInformation();
                Application.DoEvents();
                return true;
            }
            finally
            {
                this.FStateStack.Pop();
            }
            return flag;
        }

        private bool WrappedSaveObject()
        {
            bool flag;
            StandardMessages messages = this.GetMessages();
            this.FStateStack.Push(FormState.SavingData);
            try
            {
                ObjectInfo currentObjectInfo;
                if (this.Permissions.Allow_ADD_EDIT)
                {
                    ObjectIsModifiedException exception;
                    ObjectIsNotFoundException exception2;
                    DuplicateKeyException exception3;
                    DuplicateKeyException exception4;
                    currentObjectInfo = this.GetCurrentObjectInfo();
                    try
                    {
                        if (this.PrivateSaveObject())
                        {
                            goto TR_0015;
                        }
                        else
                        {
                            flag = false;
                        }
                    }
                    catch (ObjectIsModifiedException exception1) when ((() => // NOTE: To create compilable code, filter at IL offset 004E was represented using lambda expression.
                    {
                        exception = exception1;
                        return (currentObjectInfo is ExistingObjectInfo);
                    })())
                    {
                        TraceHelper.TraceException(exception);
                        if (this.GetConfirmation(messages.ObjectToBeUpdatedIsModified))
                        {
                            this.WrappedLoadObject(((ExistingObjectInfo) currentObjectInfo).Key);
                        }
                        flag = false;
                    }
                    catch (ObjectIsNotFoundException exception6) when ((() => // NOTE: To create compilable code, filter at IL offset 0097 was represented using lambda expression.
                    {
                        exception2 = exception6;
                        return (currentObjectInfo is ExistingObjectInfo);
                    })())
                    {
                        TraceHelper.TraceException(exception2);
                        if (this.GetConfirmation(messages.ObjectToBeUpdatedIsNotFound))
                        {
                            this.WrappedCloneObject();
                        }
                        flag = false;
                    }
                    catch (DuplicateKeyException exception7) when ((() => // NOTE: To create compilable code, filter at IL offset 00D6 was represented using lambda expression.
                    {
                        exception3 = exception7;
                        return (currentObjectInfo is ExistingObjectInfo);
                    })())
                    {
                        TraceHelper.TraceException(exception3);
                        this.NotifyUser(messages.DuplicateKey);
                        flag = false;
                    }
                    catch (DuplicateKeyException exception8) when ((() => // NOTE: To create compilable code, filter at IL offset 010D was represented using lambda expression.
                    {
                        exception4 = exception8;
                        return (currentObjectInfo is NewObjectInfo);
                    })())
                    {
                        TraceHelper.TraceException(exception4);
                        this.NotifyUser(messages.ObjectToBeInsertedAlreadyExists);
                        flag = false;
                    }
                    catch (DeadlockException exception9)
                    {
                        TraceHelper.TraceException(exception9);
                        this.NotifyUser(messages.SaveObjectDeadlock);
                        flag = false;
                    }
                    catch (Exception exception5)
                    {
                        this.ShowException(exception5, "Save Error");
                        flag = false;
                    }
                }
                else
                {
                    this.NotifyUser(messages.InsufficientPermissionsToSave);
                    flag = false;
                }
                return flag;
            TR_0015:
                this.OnTableUpdate();
                this.ResetChangeCount();
                this.WrappedShowMissingInformation();
                if (currentObjectInfo is NewObjectInfo)
                {
                    ObjectInfo currentObjectInfo = this.GetCurrentObjectInfo();
                    if (currentObjectInfo is ExistingObjectInfo)
                    {
                        EntityCreatedEventArgs args = new EntityCreatedEventArgs(((ExistingObjectInfo) currentObjectInfo).Key);
                        this.RaiseEntityCreated(args);
                    }
                }
                Application.DoEvents();
                return true;
            }
            finally
            {
                this.FStateStack.Pop();
            }
            return flag;
        }

        private void WrappedShowMissingInformation()
        {
            try
            {
                this.ShowMissingInformation(this.tbbMissing.Pushed);
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        protected PermissionsStruct Permissions =>
            Globals.GetUserPermissions(base.GetType().Name).Value;

        protected FormState State =>
            (0 < this.FStateStack.Count) ? this.FStateStack.Peek() : FormState.None;

        private int ChangeCount
        {
            get => 
                this.m_changeCount;
            set
            {
                this.m_changeCount = value;
                this.lblChanged.Visible = 0 < this.m_changeCount;
            }
        }

        protected bool HasUnsavedChanges =>
            0 < this.ChangeCount;

        protected DMEWorks.Controls.ChangesTracker ChangesTracker =>
            this.m_changesTracker;

        protected bool IsSaveAllowed
        {
            get => 
                this.tbbSave.Enabled;
            set
            {
                this.tbbSave.Enabled = value;
                this.tbbSave.Visible = value;
            }
        }

        private class ExistingObjectInfo : FormMaintainBase.ObjectInfo
        {
            public ExistingObjectInfo(object key)
            {
                if (key == null)
                {
                    object local1 = key;
                    throw new ArgumentNullException("key");
                }
                this.<Key>k__BackingField = key;
            }

            public object Key { get; }
        }

        public enum FormState
        {
            None,
            Closing,
            ClearingData,
            CloningData,
            DeletingData,
            LoadingData,
            SavingData,
            LoadingControls
        }

        private class NavigatorTabPage : TabPage
        {
            public NavigatorTabPage()
            {
                base.Padding = new Padding(2, 0, 2, 4);
            }

            public bool Switchable { get; set; }
        }

        private class NewObjectInfo : FormMaintainBase.ObjectInfo
        {
        }

        protected class ObjectInfo
        {
            public static FormMaintainBase.ObjectInfo CreateExisting(object key) => 
                new FormMaintainBase.ExistingObjectInfo(key);

            public static FormMaintainBase.ObjectInfo CreateNew() => 
                new FormMaintainBase.NewObjectInfo();
        }

        public static class ParameterNames
        {
            public const string EntityCreatedListener = "EntityCreatedListener";
            public const string ShowMissing = "ShowMissing";
            public const string TabPage = "TabPage";
        }

        protected sealed class StandardMessages
        {
            public string InsufficientPermissionsToDelete { get; set; }

            public string InsufficientPermissionsToSave { get; set; }

            public string ConfirmDeleting { get; set; }

            public string DeletedSuccessfully { get; set; }

            public string DeleteObjectDeadlock { get; set; }

            public string ObjectToBeDeletedIsModified { get; set; }

            public string ObjectToBeDeletedIsNotFound { get; set; }

            public string SaveObjectDeadlock { get; set; }

            public string ObjectToBeInsertedAlreadyExists { get; set; }

            public string ObjectToBeSelectedIsNotFound { get; set; }

            public string DuplicateKey { get; set; }

            public string ObjectToBeUpdatedIsModified { get; set; }

            public string ObjectToBeUpdatedIsNotFound { get; set; }
        }
    }
}


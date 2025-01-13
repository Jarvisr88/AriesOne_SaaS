namespace DMEWorks.Calendar
{
    using DMEWorks.Forms;
    using Google.Apis.Auth.OAuth2;
    using Google.Apis.Calendar.v3;
    using Google.Apis.Calendar.v3.Data;
    using Google.Apis.Services;
    using Google.Apis.Util.Store;
    using Infragistics.Win.UltraWinEditors;
    using System;
    using System.Collections.Generic;
    using System.Collections.ObjectModel;
    using System.ComponentModel;
    using System.Drawing;
    using System.IO;
    using System.Reflection;
    using System.Text;
    using System.Threading;
    using System.Windows.Forms;

    public class DialogCreateCalendarEvent : DmeForm
    {
        private static ReadOnlyCollection<CalendarListEntry> _calendars;
        private IContainer components;
        private Label lblCalendar;
        private ComboBox cmbCalendar;
        private Label lblSummary;
        private TextBox txtSummary;
        private TextBox txtDescription;
        private Label lblDescription;
        private Label label1;
        private Button btnOK;
        private Button btnCancel;
        private UltraDateTimeEditor dtpDate;
        private ComboBox cmbTime;
        private ErrorProvider errorProvider1;

        public DialogCreateCalendarEvent(string summary, string description)
        {
            this.InitializeComponent();
            this.txtSummary.Text = summary;
            this.txtDescription.Text = description;
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            base.Close();
        }

        private void btnOK_Click(object sender, EventArgs e)
        {
            try
            {
                CalendarListEntry selectedValue = this.cmbCalendar.SelectedValue as CalendarListEntry;
                this.errorProvider1.SetError(this.cmbCalendar, (selectedValue == null) ? "Select Calendar to use" : null);
                TimeSpan? nullable = this.cmbTime.SelectedValue as TimeSpan?;
                this.errorProvider1.SetError(this.cmbTime, (nullable == null) ? "Select event time" : null);
                string str = this.txtSummary.Text.Trim();
                string str2 = this.txtDescription.Text.Trim();
                this.errorProvider1.SetError(this.txtSummary, string.IsNullOrEmpty(str) ? "Enter event summary" : null);
                StringBuilder builder = new StringBuilder("There are some errors in input data");
                if (0 < Utilities.EnumerateErrors(this, this.errorProvider1, builder))
                {
                    throw new UserNotifyException(builder.ToString());
                }
                DateTime time = this.dtpDate.DateTime.Date.Add(nullable.Value);
                Event body = new Event {
                    Description = str2,
                    Summary = str
                };
                EventDateTime time1 = new EventDateTime();
                time1.DateTime = new DateTime?(FromDateTime(time));
                body.Start = time1;
                EventDateTime time3 = new EventDateTime();
                time3.DateTime = new DateTime?(FromDateTime(time.AddHours(1.0)));
                body.End = time3;
                body.Reminders = new Event.RemindersData();
                body.Reminders.UseDefault = false;
                EventReminder reminder1 = new EventReminder();
                reminder1.Method = "email";
                reminder1.Minutes = 15;
                EventReminder[] reminderArray1 = new EventReminder[3];
                reminderArray1[0] = reminder1;
                EventReminder reminder2 = new EventReminder();
                reminder2.Method = "popup";
                reminder2.Minutes = 15;
                reminderArray1[1] = reminder2;
                EventReminder reminder3 = new EventReminder();
                reminder3.Method = "sms";
                reminder3.Minutes = 15;
                reminderArray1[2] = reminder3;
                body.Reminders.Overrides = reminderArray1;
                CreateService().Events.Insert(body, selectedValue.Id).Execute();
                base.Close();
            }
            catch (Exception exception)
            {
                this.ShowException(exception);
            }
        }

        private static CalendarService CreateService()
        {
            string folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Personal), ".credentials");
            string[] scopes = new string[] { CalendarService.Scope.Calendar };
            UserCredential result = GoogleWebAuthorizationBroker.AuthorizeAsync(GetSecrets(), scopes, "user", CancellationToken.None, new FileDataStore(folder, true), null).Result;
            BaseClientService.Initializer initializer = new BaseClientService.Initializer();
            initializer.HttpClientInitializer = result;
            initializer.ApplicationName = "DME Works!";
            return new CalendarService(initializer);
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
            try
            {
                this.LoadCombobox_Calendar();
                this.LoadCombobox_Time();
                this.dtpDate.MinDate = DateTime.Today;
                this.dtpDate.MaxDate = DateTime.Today.AddYears(1);
                this.dtpDate.DateTime = DateTime.Today.AddDays(1.0);
            }
            catch (Exception exception)
            {
                throw new UserNotifyException("Cannot retrieve list of calendars", exception);
            }
        }

        internal static DateTime FromDateTime(DateTime value)
        {
            if (value.Kind == DateTimeKind.Unspecified)
            {
                value = new DateTime(value.Ticks, DateTimeKind.Local);
            }
            return value.ToLocalTime();
        }

        private static List<CalendarListEntry> GetCalendars(bool showHidden)
        {
            CalendarService service = CreateService();
            List<CalendarListEntry> list = new List<CalendarListEntry>();
            CalendarList list2 = null;
            while (true)
            {
                CalendarListResource.ListRequest request = service.CalendarList.List();
                request.ShowHidden = new bool?(showHidden);
                if (list2 != null)
                {
                    request.PageToken = list2.NextPageToken;
                }
                list2 = request.Execute();
                list.AddRange(list2.Items);
                if (string.IsNullOrEmpty(list2.NextPageToken))
                {
                    return list;
                }
            }
        }

        private static ClientSecrets GetSecrets()
        {
            using (Stream stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("DMEWorks.Resources.client_secret.json"))
            {
                return GoogleClientSecrets.Load(stream).Secrets;
            }
        }

        private static string GetSummary(CalendarListEntry entry) => 
            (entry != null) ? (string.IsNullOrEmpty(entry.SummaryOverride) ? entry.Summary : entry.SummaryOverride) : "";

        private void InitializeComponent()
        {
            this.components = new Container();
            this.lblCalendar = new Label();
            this.cmbCalendar = new ComboBox();
            this.lblSummary = new Label();
            this.txtSummary = new TextBox();
            this.txtDescription = new TextBox();
            this.lblDescription = new Label();
            this.label1 = new Label();
            this.btnOK = new Button();
            this.btnCancel = new Button();
            this.dtpDate = new UltraDateTimeEditor();
            this.cmbTime = new ComboBox();
            this.errorProvider1 = new ErrorProvider(this.components);
            ((ISupportInitialize) this.errorProvider1).BeginInit();
            base.SuspendLayout();
            this.lblCalendar.Location = new Point(8, 8);
            this.lblCalendar.Name = "lblCalendar";
            this.lblCalendar.Size = new Size(0x48, 0x15);
            this.lblCalendar.TabIndex = 0;
            this.lblCalendar.Text = "Calendar:";
            this.lblCalendar.TextAlign = ContentAlignment.MiddleRight;
            this.cmbCalendar.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.cmbCalendar.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbCalendar.FormattingEnabled = true;
            this.cmbCalendar.Location = new Point(0x58, 8);
            this.cmbCalendar.Name = "cmbCalendar";
            this.cmbCalendar.Size = new Size(0x100, 0x15);
            this.cmbCalendar.TabIndex = 1;
            this.lblSummary.Location = new Point(8, 40);
            this.lblSummary.Name = "lblSummary";
            this.lblSummary.Size = new Size(0x48, 0x15);
            this.lblSummary.TabIndex = 2;
            this.lblSummary.Text = "Summary:";
            this.lblSummary.TextAlign = ContentAlignment.MiddleRight;
            this.txtSummary.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Top;
            this.txtSummary.Location = new Point(0x58, 40);
            this.txtSummary.Name = "txtSummary";
            this.txtSummary.Size = new Size(0x100, 20);
            this.txtSummary.TabIndex = 3;
            this.txtDescription.Anchor = AnchorStyles.Right | AnchorStyles.Left | AnchorStyles.Bottom | AnchorStyles.Top;
            this.txtDescription.Location = new Point(0x58, 0x58);
            this.txtDescription.Multiline = true;
            this.txtDescription.Name = "txtDescription";
            this.txtDescription.Size = new Size(0x100, 90);
            this.txtDescription.TabIndex = 8;
            this.lblDescription.Location = new Point(8, 0x58);
            this.lblDescription.Name = "lblDescription";
            this.lblDescription.Size = new Size(0x48, 0x15);
            this.lblDescription.TabIndex = 7;
            this.lblDescription.Text = "Description:";
            this.lblDescription.TextAlign = ContentAlignment.MiddleRight;
            this.label1.Location = new Point(8, 0x40);
            this.label1.Name = "label1";
            this.label1.Size = new Size(0x48, 0x15);
            this.label1.TabIndex = 4;
            this.label1.Text = "Event Time:";
            this.label1.TextAlign = ContentAlignment.MiddleRight;
            this.btnOK.Anchor = AnchorStyles.Right | AnchorStyles.Bottom;
            this.btnOK.Location = new Point(0xc0, 0xba);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new Size(0x4b, 0x17);
            this.btnOK.TabIndex = 11;
            this.btnOK.Text = "OK";
            this.btnOK.UseVisualStyleBackColor = true;
            this.btnOK.Click += new EventHandler(this.btnOK_Click);
            this.btnCancel.Anchor = AnchorStyles.Right | AnchorStyles.Bottom;
            this.btnCancel.Location = new Point(0x110, 0xba);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new Size(0x4b, 0x17);
            this.btnCancel.TabIndex = 12;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new EventHandler(this.btnCancel_Click);
            this.dtpDate.Location = new Point(0x58, 0x40);
            this.dtpDate.Name = "dtpDate";
            this.dtpDate.Size = new Size(0x80, 0x15);
            this.dtpDate.TabIndex = 5;
            this.cmbTime.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbTime.FormattingEnabled = true;
            this.cmbTime.Location = new Point(0xe0, 0x40);
            this.cmbTime.Name = "cmbTime";
            this.cmbTime.Size = new Size(120, 0x15);
            this.cmbTime.TabIndex = 6;
            this.errorProvider1.ContainerControl = this;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.ClientSize = new Size(0x160, 0xd5);
            base.Controls.Add(this.cmbTime);
            base.Controls.Add(this.dtpDate);
            base.Controls.Add(this.btnCancel);
            base.Controls.Add(this.btnOK);
            base.Controls.Add(this.label1);
            base.Controls.Add(this.lblDescription);
            base.Controls.Add(this.txtDescription);
            base.Controls.Add(this.txtSummary);
            base.Controls.Add(this.lblSummary);
            base.Controls.Add(this.cmbCalendar);
            base.Controls.Add(this.lblCalendar);
            this.MinimumSize = new Size(360, 240);
            base.Name = "DialogCreateCalendarEvent";
            base.SizeGripStyle = SizeGripStyle.Hide;
            this.Text = "Create new event";
            base.Load += new EventHandler(this.Form1_Load);
            ((ISupportInitialize) this.errorProvider1).EndInit();
            base.ResumeLayout(false);
            base.PerformLayout();
        }

        private void LoadCombobox_Calendar()
        {
            List<Entry<CalendarListEntry>> list = new List<Entry<CalendarListEntry>> {
                new Entry<CalendarListEntry>(null, "-- Select --")
            };
            foreach (CalendarListEntry entry in Calendars)
            {
                list.Add(new Entry<CalendarListEntry>(entry, GetSummary(entry)));
            }
            this.cmbCalendar.DataSource = list.ToArray();
            this.cmbCalendar.DisplayMember = "Text";
            this.cmbCalendar.ValueMember = "Value";
        }

        private void LoadCombobox_Time()
        {
            List<Entry<TimeSpan?>> list = new List<Entry<TimeSpan?>>();
            TimeSpan? nullable = null;
            list.Add(new Entry<TimeSpan?>(nullable, "-- Select --"));
            for (int i = 0; i < 0x30; i++)
            {
                TimeSpan span = TimeSpan.FromMinutes((double) (30 * i));
                string text = $"{span.Hours:00}:{span.Minutes:00}";
                list.Add(new Entry<TimeSpan?>(new TimeSpan?(span), text));
            }
            this.cmbTime.DataSource = list.ToArray();
            this.cmbTime.DisplayMember = "Text";
            this.cmbTime.ValueMember = "Value";
        }

        private static ReadOnlyCollection<CalendarListEntry> Calendars
        {
            get
            {
                if (_calendars == null)
                {
                    CalendarListEntry[] array = GetCalendars(true).ToArray();
                    Array.Sort<CalendarListEntry>(array, CalendarListEntryComparer.Default);
                    _calendars = Array.AsReadOnly<CalendarListEntry>(array);
                }
                return _calendars;
            }
        }

        private class CalendarListEntryComparer : IComparer<CalendarListEntry>
        {
            public static readonly DialogCreateCalendarEvent.CalendarListEntryComparer Default = new DialogCreateCalendarEvent.CalendarListEntryComparer();

            int IComparer<CalendarListEntry>.Compare(CalendarListEntry x, CalendarListEntry y) => 
                string.Compare(DialogCreateCalendarEvent.GetSummary(x), DialogCreateCalendarEvent.GetSummary(y));
        }
    }
}


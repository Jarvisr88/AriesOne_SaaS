namespace DMEWorks.Ability
{
    using Devart.Data.MySql;
    using DMEWorks;
    using DMEWorks.Ability.Cmn;
    using DMEWorks.Ability.Common;
    using DMEWorks.Core;
    using DMEWorks.Core.Extensions;
    using DMEWorks.Forms;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Data;
    using System.Diagnostics;
    using System.Drawing;
    using System.IO;
    using System.Linq;
    using System.Net;
    using System.Runtime.CompilerServices;
    using System.Security.Cryptography.X509Certificates;
    using System.Text;
    using System.Threading.Tasks;
    using System.Windows.Forms;
    using System.Xml;
    using System.Xml.Serialization;

    public class FormSameOrSimilar : DmeForm
    {
        private readonly string policyNumber;
        private static X509Certificate2Collection selected;
        private const string CrLf = "\r\n";
        private IntegrationSettings m_integrationSettings;
        private IContainer components;
        private Button btnSubmit;
        private Panel panel1;
        private ComboBox cmbNPI;
        private Label lblNPI;
        private Label lblBillingCode;
        private ComboBox cmbBillingCode;
        private FilteredGrid gridResults;

        public FormSameOrSimilar(IEnumerable<string> billingCodes, string policyNumber)
        {
            if (billingCodes == null)
            {
                throw new ArgumentNullException("billingCodes");
            }
            this.policyNumber = policyNumber;
            this.InitializeComponent();
            this.InitializeGridResults(this.gridResults.Appearance);
            this.cmbBillingCode.BeginUpdate();
            try
            {
                this.cmbBillingCode.Items.Clear();
                this.cmbBillingCode.Items.AddRange(billingCodes.ToArray<string>());
            }
            finally
            {
                this.cmbBillingCode.EndUpdate();
            }
        }

        [AsyncStateMachine(typeof(<btnSubmit_Click>d__7))]
        private void btnSubmit_Click(object sender, EventArgs e)
        {
            <btnSubmit_Click>d__7 d__;
            d__.<>4__this = this;
            d__.<>t__builder = AsyncVoidMethodBuilder.Create();
            d__.<>1__state = -1;
            d__.<>t__builder.Start<<btnSubmit_Click>d__7>(ref d__);
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (this.components != null))
            {
                this.components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void FormClaimStatus_Load(object sender, EventArgs e)
        {
            try
            {
                using (MySqlConnection connection = Globals.CreateConnection())
                {
                    List<Tuple<string, string, string>> list;
                    connection.Open();
                    using (MySqlCommand command = connection.CreateCommand())
                    {
                        command.CommandText = "SELECT AbilityIntegrationSettings FROM tbl_company WHERE ID = 1";
                        this.m_integrationSettings = IntegrationSettings.XmlDeserialize(Convert.ToString(command.ExecuteScalar()));
                    }
                    using (MySqlCommand command2 = connection.CreateCommand())
                    {
                        command2.CommandText = "SELECT Npi, State, 'Company' as Description\r\nFROM tbl_company\r\nWHERE ID = 1\r\n  AND Npi != ''\r\nUNION ALL\r\nSELECT Npi, State, Name as Description\r\nFROM tbl_location\r\nWHERE Npi != ''";
                        Func<IDataRecord, Tuple<string, string, string>> selector = <>c.<>9__10_0;
                        if (<>c.<>9__10_0 == null)
                        {
                            Func<IDataRecord, Tuple<string, string, string>> local1 = <>c.<>9__10_0;
                            selector = <>c.<>9__10_0 = delegate (IDataRecord r) {
                                string str = SqlString.Normalize(Convert.ToString(r[0]));
                                string str3 = SqlString.Normalize(Convert.ToString(r[2]));
                                return Tuple.Create<string, string, string>(str, SqlString.Normalize(Convert.ToString(r[1])), str + " - " + str3);
                            };
                        }
                        list = command2.ExecuteList<Tuple<string, string, string>>(selector);
                    }
                    this.cmbNPI.BeginUpdate();
                    try
                    {
                        this.cmbNPI.Items.Clear();
                        HashSet<string> set1 = new HashSet<string>(StringComparer.InvariantCultureIgnoreCase);
                        Func<Tuple<string, string, string>, string> keySelector = <>c.<>9__10_1;
                        if (<>c.<>9__10_1 == null)
                        {
                            Func<Tuple<string, string, string>, string> local2 = <>c.<>9__10_1;
                            keySelector = <>c.<>9__10_1 = t => t.Item1;
                        }
                        Func<IGrouping<string, Tuple<string, string, string>>, string> func3 = <>c.<>9__10_2;
                        if (<>c.<>9__10_2 == null)
                        {
                            Func<IGrouping<string, Tuple<string, string, string>>, string> local3 = <>c.<>9__10_2;
                            func3 = <>c.<>9__10_2 = g => g.Key;
                        }
                        Func<IGrouping<string, Tuple<string, string, string>>, Tuple<string, string, string>> selector = <>c.<>9__10_3;
                        if (<>c.<>9__10_3 == null)
                        {
                            Func<IGrouping<string, Tuple<string, string, string>>, Tuple<string, string, string>> local4 = <>c.<>9__10_3;
                            selector = <>c.<>9__10_3 = g => g.First<Tuple<string, string, string>>();
                        }
                        this.cmbNPI.Items.AddRange(list.GroupBy<Tuple<string, string, string>, string>(keySelector).OrderBy<IGrouping<string, Tuple<string, string, string>>, string>(func3, StringComparer.InvariantCultureIgnoreCase).Select<IGrouping<string, Tuple<string, string, string>>, Tuple<string, string, string>>(selector).ToArray<Tuple<string, string, string>>());
                        this.cmbNPI.ValueMember = "Item1";
                        this.cmbNPI.DisplayMember = "Item3";
                    }
                    finally
                    {
                        this.cmbNPI.EndUpdate();
                    }
                }
            }
            catch (Exception exception)
            {
                this.ShowException(exception, "Same or Similar");
            }
        }

        private static X509Certificate2Collection GetCerts(StoreName storeName, StoreLocation storeLocation)
        {
            X509Certificate2Collection certificates;
            X509Store store = new X509Store(storeName, storeLocation);
            try
            {
                store.Open(OpenFlags.OpenExistingOnly);
                certificates = store.Certificates;
            }
            finally
            {
                store.Close();
            }
            return certificates;
        }

        private void InitializeComponent()
        {
            this.btnSubmit = new Button();
            this.panel1 = new Panel();
            this.cmbBillingCode = new ComboBox();
            this.cmbNPI = new ComboBox();
            this.lblNPI = new Label();
            this.lblBillingCode = new Label();
            this.gridResults = new FilteredGrid();
            this.panel1.SuspendLayout();
            base.SuspendLayout();
            this.btnSubmit.Location = new Point(0x1f8, 0x1f);
            this.btnSubmit.Name = "btnSubmit";
            this.btnSubmit.Size = new Size(0x4b, 0x17);
            this.btnSubmit.TabIndex = 8;
            this.btnSubmit.Text = "Submit";
            this.btnSubmit.UseVisualStyleBackColor = true;
            this.btnSubmit.Click += new EventHandler(this.btnSubmit_Click);
            this.panel1.Controls.Add(this.cmbBillingCode);
            this.panel1.Controls.Add(this.cmbNPI);
            this.panel1.Controls.Add(this.btnSubmit);
            this.panel1.Controls.Add(this.lblNPI);
            this.panel1.Controls.Add(this.lblBillingCode);
            this.panel1.Dock = DockStyle.Top;
            this.panel1.Location = new Point(0, 0);
            this.panel1.Name = "panel1";
            this.panel1.Size = new Size(730, 0x40);
            this.panel1.TabIndex = 0;
            this.cmbBillingCode.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbBillingCode.FormattingEnabled = true;
            this.cmbBillingCode.Location = new Point(0x58, 0x20);
            this.cmbBillingCode.Name = "cmbBillingCode";
            this.cmbBillingCode.Size = new Size(0x128, 0x15);
            this.cmbBillingCode.TabIndex = 3;
            this.cmbNPI.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbNPI.FormattingEnabled = true;
            this.cmbNPI.Location = new Point(0x58, 8);
            this.cmbNPI.Name = "cmbNPI";
            this.cmbNPI.Size = new Size(0x128, 0x15);
            this.cmbNPI.TabIndex = 1;
            this.lblNPI.Location = new Point(8, 8);
            this.lblNPI.Name = "lblNPI";
            this.lblNPI.Size = new Size(0x48, 0x15);
            this.lblNPI.TabIndex = 0;
            this.lblNPI.Text = "NPI:";
            this.lblNPI.TextAlign = ContentAlignment.MiddleRight;
            this.lblBillingCode.Location = new Point(8, 0x20);
            this.lblBillingCode.Name = "lblBillingCode";
            this.lblBillingCode.Size = new Size(0x48, 0x15);
            this.lblBillingCode.TabIndex = 2;
            this.lblBillingCode.Text = "Billing Code:";
            this.lblBillingCode.TextAlign = ContentAlignment.MiddleRight;
            this.gridResults.Dock = DockStyle.Fill;
            this.gridResults.Location = new Point(0, 0x40);
            this.gridResults.Name = "gridResults";
            this.gridResults.Size = new Size(730, 0x198);
            this.gridResults.TabIndex = 1;
            base.AutoScaleDimensions = new SizeF(6f, 13f);
            base.AutoScaleMode = AutoScaleMode.Font;
            base.ClientSize = new Size(730, 0x1d8);
            base.Controls.Add(this.gridResults);
            base.Controls.Add(this.panel1);
            base.Name = "FormSameOrSimilar";
            this.Text = "Same or Similar";
            base.Load += new EventHandler(this.FormClaimStatus_Load);
            this.panel1.ResumeLayout(false);
            base.ResumeLayout(false);
        }

        private void InitializeGridResults(FilteredGridAppearance appearance)
        {
            appearance.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.None;
            appearance.RowHeadersWidth = 30;
            appearance.RowTemplate.Height = 20;
            appearance.AutoGenerateColumns = false;
            appearance.AllowEdit = false;
            appearance.AllowNew = false;
            appearance.MultiSelect = true;
            appearance.Columns.Clear();
            appearance.SelectionMode = DataGridViewSelectionMode.RowHeaderSelect;
            appearance.EditMode = DataGridViewEditMode.EditOnEnter;
            appearance.ShowCellErrors = true;
            appearance.ShowRowErrors = true;
            appearance.AddTextColumn("SubmittedHcpcs", "SubmittedHcpcs", 70);
            appearance.AddTextColumn("ApprovedHcpcs", "ApprovedHcpcs", 70);
            appearance.AddTextColumn("InitialDate", "InitialDate", 70);
            appearance.AddTextColumn("StatusCode", "StatusCode", 70);
            appearance.AddTextColumn("StatusDescription", "StatusDescription", 70);
            appearance.AddTextColumn("StatusDate", "StatusDate", 70);
            appearance.AddTextColumn("LengthOfNeed", "LengthOfNeed", 70);
            appearance.AddTextColumn("TypeValue", "TypeValue", 70);
            appearance.AddTextColumn("TypeDescription", "TypeDescription", 70);
            appearance.AddTextColumn("TotalRentalPayments", "TotalRentalPayments", 70);
            appearance.AddTextColumn("RecertificationRevisedDate", "RecertRevisedDate", 70);
            appearance.AddTextColumn("LastClaimDate", "Last Claim Date", 70);
            appearance.AddTextColumn("SupplierName", "Supplier Name", 70);
            appearance.AddTextColumn("SupplierPhone", "Supplier Phone", 70);
        }

        private static X509Certificate2Collection SelectCert()
        {
            if ((selected == null) || (selected.Count == 0))
            {
                selected = X509Certificate2UI.SelectFromCollection(GetCerts(StoreName.My, StoreLocation.CurrentUser).Find(X509FindType.FindByTimeValid, DateTime.Now, false).Find(X509FindType.FindByApplicationPolicy, "1.3.6.1.5.5.7.3.2", true), "Select Certificate", "Select a certificate from the following list for Ability portal authorization", X509SelectionFlag.MultiSelection);
            }
            return selected;
        }

        [AsyncStateMachine(typeof(<SendRequestAsync>d__6))]
        private static Task<CmnResponse> SendRequestAsync(X509Certificate2 certificate, CmnRequest requestObj)
        {
            <SendRequestAsync>d__6 d__;
            d__.certificate = certificate;
            d__.requestObj = requestObj;
            d__.<>t__builder = AsyncTaskMethodBuilder<CmnResponse>.Create();
            d__.<>1__state = -1;
            d__.<>t__builder.Start<<SendRequestAsync>d__6>(ref d__);
            return d__.<>t__builder.Task;
        }

        [Serializable, CompilerGenerated]
        private sealed class <>c
        {
            public static readonly FormSameOrSimilar.<>c <>9 = new FormSameOrSimilar.<>c();
            public static Func<IDataRecord, Tuple<string, string, string>> <>9__10_0;
            public static Func<Tuple<string, string, string>, string> <>9__10_1;
            public static Func<IGrouping<string, Tuple<string, string, string>>, string> <>9__10_2;
            public static Func<IGrouping<string, Tuple<string, string, string>>, Tuple<string, string, string>> <>9__10_3;

            internal Tuple<string, string, string> <FormClaimStatus_Load>b__10_0(IDataRecord r)
            {
                string str = SqlString.Normalize(Convert.ToString(r[0]));
                string str3 = SqlString.Normalize(Convert.ToString(r[2]));
                return Tuple.Create<string, string, string>(str, SqlString.Normalize(Convert.ToString(r[1])), str + " - " + str3);
            }

            internal string <FormClaimStatus_Load>b__10_1(Tuple<string, string, string> t) => 
                t.Item1;

            internal string <FormClaimStatus_Load>b__10_2(IGrouping<string, Tuple<string, string, string>> g) => 
                g.Key;

            internal Tuple<string, string, string> <FormClaimStatus_Load>b__10_3(IGrouping<string, Tuple<string, string, string>> g) => 
                g.First<Tuple<string, string, string>>();
        }

        [CompilerGenerated]
        private struct <btnSubmit_Click>d__7 : IAsyncStateMachine
        {
            public int <>1__state;
            public AsyncVoidMethodBuilder <>t__builder;
            public FormSameOrSimilar <>4__this;
            private TaskAwaiter<CmnResponse> <>u__1;

            private void MoveNext()
            {
                int num = this.<>1__state;
                FormSameOrSimilar form = this.<>4__this;
                try
                {
                    if (num != 0)
                    {
                        form.btnSubmit.Enabled = false;
                    }
                    try
                    {
                        CmnResponse response;
                        TaskAwaiter<CmnResponse> awaiter;
                        if (num == 0)
                        {
                            awaiter = this.<>u__1;
                            this.<>u__1 = new TaskAwaiter<CmnResponse>();
                            this.<>1__state = num = -1;
                            goto TR_000B;
                        }
                        else
                        {
                            form.gridResults.GridSource = Enumerable.Empty<CmnResponseEntry>().ToGridSource<CmnResponseEntry>(Array.Empty<string>());
                            if ((form.m_integrationSettings == null) || (form.m_integrationSettings.Credentials == null))
                            {
                                throw new UserNotifyException("Ability integration must be properly configured");
                            }
                            Tuple<string, string, string> selectedItem = (Tuple<string, string, string>) form.cmbNPI.SelectedItem;
                            DMEWorks.Ability.Common.Application application1 = new DMEWorks.Ability.Common.Application();
                            application1.DataCenter = DataCenterType.CDS;
                            application1.DataCenterSpecified = true;
                            application1.FacilityState = selectedItem.Item2;
                            application1.FacilityStateSpecified = true;
                            application1.LineOfBusiness = LineOfBusiness.DME;
                            application1.LineOfBusinessSpecified = true;
                            application1.Name = ApplicationName.CSI;
                            application1.NameSpecified = true;
                            MedicareMainframe mainframe1 = new MedicareMainframe();
                            mainframe1.Application = application1;
                            mainframe1.ApplicationSpecified = true;
                            Credential credential1 = new Credential();
                            credential1.Password = form.m_integrationSettings.Credentials.Password;
                            credential1.UserId = form.m_integrationSettings.Credentials.Username;
                            mainframe1.Credential = credential1;
                            mainframe1.CredentialSpecified = true;
                            CmnRequest request1 = new CmnRequest();
                            request1.MedicareMainframe = mainframe1;
                            request1.MockResponse = false;
                            request1.MockResponseSpecified = true;
                            CmnRequestSearchCriteria criteria1 = new CmnRequestSearchCriteria();
                            criteria1.Hcpcs = form.cmbBillingCode.Text;
                            criteria1.Npi = selectedItem.Item1;
                            criteria1.Hic = form.policyNumber;
                            criteria1.Mbi = "";
                            criteria1.MaxResults = 50;
                            criteria1.MaxResultsSpecified = true;
                            request1.SearchCriteria = criteria1;
                            CmnRequest requestObj = request1;
                            X509Certificate2Collection certificates = FormSameOrSimilar.SelectCert();
                            if ((certificates == null) || (certificates.Count == 0))
                            {
                                throw new UserNotifyException("Certificate is required for communication with Ability portal");
                            }
                            if (!certificates[0].HasPrivateKey)
                            {
                                throw new UserNotifyException("Certificate is not suitable for authentication");
                            }
                            awaiter = FormSameOrSimilar.SendRequestAsync(certificates[0], requestObj).GetAwaiter();
                            if (awaiter.IsCompleted)
                            {
                                goto TR_000B;
                            }
                            else
                            {
                                this.<>1__state = num = 0;
                                this.<>u__1 = awaiter;
                                this.<>t__builder.AwaitUnsafeOnCompleted<TaskAwaiter<CmnResponse>, FormSameOrSimilar.<btnSubmit_Click>d__7>(ref awaiter, ref this);
                            }
                        }
                        return;
                    TR_000B:
                        response = awaiter.GetResult();
                        if ((response != null) && (response.Claims != null))
                        {
                            form.gridResults.GridSource = response.Claims.ToGridSource<CmnResponseEntry>(Array.Empty<string>());
                        }
                    }
                    catch (Exception exception1)
                    {
                        form.ShowException(exception1);
                    }
                    finally
                    {
                        if (num < 0)
                        {
                            form.btnSubmit.Enabled = true;
                        }
                    }
                }
                catch (Exception exception2)
                {
                    this.<>1__state = -2;
                    this.<>t__builder.SetException(exception2);
                    return;
                }
                this.<>1__state = -2;
                this.<>t__builder.SetResult();
            }

            [DebuggerHidden]
            private void SetStateMachine(IAsyncStateMachine stateMachine)
            {
                this.<>t__builder.SetStateMachine(stateMachine);
            }
        }

        [CompilerGenerated]
        private struct <SendRequestAsync>d__6 : IAsyncStateMachine
        {
            public int <>1__state;
            public AsyncTaskMethodBuilder<CmnResponse> <>t__builder;
            public CmnRequest requestObj;
            public X509Certificate2 certificate;
            private HttpWebRequest <request>5__2;
            private MemoryStream <stream>5__3;
            private TaskAwaiter<Stream> <>u__1;
            private TaskAwaiter<WebResponse> <>u__2;

            private void MoveNext()
            {
                int num = this.<>1__state;
                try
                {
                    CmnResponse response;
                    string str;
                    StringReader reader4;
                    if (num != 0)
                    {
                        if (num == 1)
                        {
                            goto TR_003B;
                        }
                        else
                        {
                            StringWriter output = new StringWriter();
                            try
                            {
                                XmlWriterSettings settings = new XmlWriterSettings();
                                settings.CloseOutput = false;
                                settings.Indent = true;
                                settings.OmitXmlDeclaration = true;
                                XmlWriter xmlWriter = XmlWriter.Create(output, settings);
                                try
                                {
                                    XmlSerializerNamespaces namespaces = new XmlSerializerNamespaces();
                                    namespaces.Add(string.Empty, string.Empty);
                                    new XmlSerializer(typeof(CmnRequest)).Serialize(xmlWriter, this.requestObj, namespaces);
                                }
                                finally
                                {
                                    if ((num < 0) && (xmlWriter != null))
                                    {
                                        xmlWriter.Dispose();
                                    }
                                }
                                Trace.TraceInformation(output.ToString());
                            }
                            finally
                            {
                                if ((num < 0) && (output != null))
                                {
                                    output.Dispose();
                                }
                            }
                            this.<request>5__2 = WebRequest.CreateHttp("https://access.abilitynetwork.com/access/csi/cmn");
                            this.<request>5__2.Headers.Add("X-Access-Version", "1");
                            this.<request>5__2.Method = "POST";
                            this.<request>5__2.ContentType = "text/xml;charset=UTF-8";
                            this.<request>5__2.ClientCertificates.Add(this.certificate);
                            this.<stream>5__3 = new MemoryStream();
                        }
                    }
                    try
                    {
                        Stream stream;
                        TaskAwaiter<Stream> awaiter;
                        if (num == 0)
                        {
                            awaiter = this.<>u__1;
                            this.<>u__1 = new TaskAwaiter<Stream>();
                            this.<>1__state = num = -1;
                            goto TR_003F;
                        }
                        else
                        {
                            XmlWriterSettings settings = new XmlWriterSettings();
                            settings.CloseOutput = false;
                            settings.Indent = true;
                            settings.OmitXmlDeclaration = true;
                            XmlWriter xmlWriter = XmlWriter.Create(this.<stream>5__3, settings);
                            try
                            {
                                XmlSerializerNamespaces namespaces = new XmlSerializerNamespaces();
                                namespaces.Add(string.Empty, string.Empty);
                                new XmlSerializer(typeof(CmnRequest)).Serialize(xmlWriter, this.requestObj, namespaces);
                            }
                            finally
                            {
                                if ((num < 0) && (xmlWriter != null))
                                {
                                    xmlWriter.Dispose();
                                }
                            }
                            this.<request>5__2.ContentLength = this.<stream>5__3.Length;
                            awaiter = this.<request>5__2.GetRequestStreamAsync().GetAwaiter();
                            if (awaiter.IsCompleted)
                            {
                                goto TR_003F;
                            }
                            else
                            {
                                this.<>1__state = num = 0;
                                this.<>u__1 = awaiter;
                                this.<>t__builder.AwaitUnsafeOnCompleted<TaskAwaiter<Stream>, FormSameOrSimilar.<SendRequestAsync>d__6>(ref awaiter, ref this);
                            }
                        }
                        return;
                    TR_003F:
                        stream = awaiter.GetResult();
                        try
                        {
                            this.<stream>5__3.WriteTo(stream);
                        }
                        finally
                        {
                            if ((num < 0) && (stream != null))
                            {
                                stream.Dispose();
                            }
                        }
                        goto TR_003C;
                    }
                    finally
                    {
                        if ((num < 0) && (this.<stream>5__3 != null))
                        {
                            this.<stream>5__3.Dispose();
                        }
                    }
                    return;
                TR_0031:
                    reader4 = new StringReader(str);
                    try
                    {
                        response = (CmnResponse) new XmlSerializer(typeof(CmnResponse)).Deserialize(reader4);
                    }
                    finally
                    {
                        if ((num < 0) && (reader4 != null))
                        {
                            reader4.Dispose();
                        }
                    }
                    this.<>1__state = -2;
                    this.<request>5__2 = null;
                    this.<>t__builder.SetResult(response);
                    return;
                TR_003B:
                    try
                    {
                        WebResponse response2;
                        TaskAwaiter<WebResponse> awaiter2;
                        if (num == 1)
                        {
                            awaiter2 = this.<>u__2;
                            this.<>u__2 = new TaskAwaiter<WebResponse>();
                            this.<>1__state = num = -1;
                            goto TR_0036;
                        }
                        else
                        {
                            awaiter2 = this.<request>5__2.GetResponseAsync().GetAwaiter();
                            if (awaiter2.IsCompleted)
                            {
                                goto TR_0036;
                            }
                            else
                            {
                                this.<>1__state = num = 1;
                                this.<>u__2 = awaiter2;
                                this.<>t__builder.AwaitUnsafeOnCompleted<TaskAwaiter<WebResponse>, FormSameOrSimilar.<SendRequestAsync>d__6>(ref awaiter2, ref this);
                            }
                        }
                        return;
                    TR_0036:
                        response2 = awaiter2.GetResult();
                        try
                        {
                            StreamReader reader = new StreamReader(response2.GetResponseStream(), Encoding.UTF8);
                            try
                            {
                                str = reader.ReadToEnd();
                                Trace.TraceInformation(str);
                            }
                            finally
                            {
                                if ((num < 0) && (reader != null))
                                {
                                    reader.Dispose();
                                }
                            }
                        }
                        finally
                        {
                            if ((num < 0) && (response2 != null))
                            {
                                response2.Dispose();
                            }
                        }
                        goto TR_0031;
                    }
                    catch (WebException exception)
                    {
                        HttpWebResponse response3 = exception.Response as HttpWebResponse;
                        if (response3 != null)
                        {
                            object[] args = new object[] { response3.StatusCode, response3.StatusDescription };
                            Trace.TraceError("({0}) {1}", args);
                            StreamReader reader2 = new StreamReader(response3.GetResponseStream(), Encoding.UTF8);
                            try
                            {
                                str = reader2.ReadToEnd();
                                Trace.TraceError(str);
                            }
                            finally
                            {
                                if ((num < 0) && (reader2 != null))
                                {
                                    reader2.Dispose();
                                }
                            }
                            StringReader textReader = new StringReader(str);
                            try
                            {
                                DMEWorks.Ability.Common.Error error = (DMEWorks.Ability.Common.Error) new XmlSerializer(typeof(DMEWorks.Ability.Common.Error)).Deserialize(textReader);
                                if ((error != null) && !string.IsNullOrEmpty(error.Message))
                                {
                                    throw new UserNotifyException(error.Message, exception);
                                }
                            }
                            finally
                            {
                                if ((num < 0) && (textReader != null))
                                {
                                    textReader.Dispose();
                                }
                            }
                        }
                        throw exception;
                    }
                    return;
                TR_003C:
                    this.<stream>5__3 = null;
                    goto TR_003B;
                }
                catch (Exception exception2)
                {
                    this.<>1__state = -2;
                    this.<request>5__2 = null;
                    this.<>t__builder.SetException(exception2);
                }
            }

            [DebuggerHidden]
            private void SetStateMachine(IAsyncStateMachine stateMachine)
            {
                this.<>t__builder.SetStateMachine(stateMachine);
            }
        }
    }
}


namespace DMEWorks.Core
{
    using DMEWorks.Forms;
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.Reflection;
    using System.Runtime.CompilerServices;
    using System.Windows.Forms;

    [AttributeUsage(AttributeTargets.Method, AllowMultiple=false, Inherited=false)]
    public class HandleDatabaseChangedAttribute : Attribute
    {
        private static readonly Dictionary<System.Type, TypeHelper> m_typeHelpers = new Dictionary<System.Type, TypeHelper>();

        public HandleDatabaseChangedAttribute(string tableName0)
        {
            this.<TableNames>k__BackingField = new string[] { tableName0 };
        }

        public HandleDatabaseChangedAttribute(string[] tableNames)
        {
            this.<TableNames>k__BackingField = tableNames;
        }

        private static TypeHelper GetTypeHelper(ContainerControl control)
        {
            object syncRoot = ((ICollection) m_typeHelpers).SyncRoot;
            lock (syncRoot)
            {
                TypeHelper helper;
                if (!m_typeHelpers.TryGetValue(control.GetType(), out helper))
                {
                    helper = new TypeHelper(control);
                    m_typeHelpers.Add(helper.Type, helper);
                }
                return helper;
            }
        }

        public static void InvokeHandles(Form form, string[] tableNames)
        {
            if (form == null)
            {
                throw new ArgumentNullException("form");
            }
            if (tableNames == null)
            {
                throw new ArgumentNullException("tableNames");
            }
            HashSet<string> set = new HashSet<string>(tableNames, StringComparer.InvariantCultureIgnoreCase);
            if ((set.Count != 0) && !form.IsDisposed)
            {
                InvokeHandlesRecursively(form, set);
            }
        }

        private static void InvokeHandlesRecursively(Control control, HashSet<string> set)
        {
            for (int i = 0; i < control.Controls.Count; i++)
            {
                InvokeHandlesRecursively(control.Controls[i], set);
            }
            ContainerControl control2 = control as ContainerControl;
            if (control2 != null)
            {
                GetTypeHelper(control2).InvokeHandles(control2, set);
            }
        }

        public string[] TableNames { get; }

        private sealed class MethodHelper
        {
            private readonly MethodInfo m_method;
            private static readonly object[] EmptyArray = new object[0];

            public MethodHelper(MethodInfo method, HandleDatabaseChangedAttribute attribute)
            {
                if (method == null)
                {
                    MethodInfo local1 = method;
                    throw new ArgumentNullException("method");
                }
                this.m_method = method;
                if (attribute == null)
                {
                    HandleDatabaseChangedAttribute local2 = attribute;
                    throw new ArgumentNullException("attribute");
                }
                this.<TableNames>k__BackingField = attribute.TableNames;
            }

            public void Invoke(ContainerControl control)
            {
                this.m_method.Invoke(control, EmptyArray);
            }

            public string[] TableNames { get; }
        }

        private sealed class TypeHelper
        {
            private readonly HandleDatabaseChangedAttribute.MethodHelper[] m_handlers;

            public TypeHelper(ContainerControl control)
            {
                if (control == null)
                {
                    throw new ArgumentNullException("control");
                }
                this.<Type>k__BackingField = control.GetType();
                List<HandleDatabaseChangedAttribute.MethodHelper> list = new List<HandleDatabaseChangedAttribute.MethodHelper>();
                foreach (MethodInfo info in this.Type.GetMethods(BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance))
                {
                    if (!info.ContainsGenericParameters && (info.GetParameters().Length == 0))
                    {
                        HandleDatabaseChangedAttribute customAttribute = info.GetCustomAttribute<HandleDatabaseChangedAttribute>(false);
                        if (customAttribute != null)
                        {
                            list.Add(new HandleDatabaseChangedAttribute.MethodHelper(info, customAttribute));
                        }
                    }
                }
                this.m_handlers = list.ToArray();
            }

            public void InvokeHandles(ContainerControl control, HashSet<string> set)
            {
                if (control == null)
                {
                    throw new ArgumentNullException("control");
                }
                if (this.Type != control.GetType())
                {
                    throw new ArgumentException("control");
                }
                Form parentForm = control.ParentForm;
                if (control is Form)
                {
                    parentForm = (Form) control;
                }
                foreach (HandleDatabaseChangedAttribute.MethodHelper helper in this.m_handlers)
                {
                    if (set.Overlaps(helper.TableNames))
                    {
                        try
                        {
                            helper.Invoke(control);
                        }
                        catch (Exception exception1)
                        {
                            parentForm.ShowException(exception1);
                        }
                    }
                }
            }

            public System.Type Type { get; }
        }
    }
}


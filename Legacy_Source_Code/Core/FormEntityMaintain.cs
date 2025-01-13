namespace DMEWorks.Core
{
    using DMEWorks.Data;
    using DMEWorks.Data.Common;
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Runtime.CompilerServices;
    using System.Text;
    using System.Threading;
    using System.Windows.Forms;

    public class FormEntityMaintain : FormMaintainBase
    {
        private IAdapter m_adapter;
        private object m_entity;

        protected virtual IAdapter CreateAdapter()
        {
            throw new NotImplementedException();
        }

        protected virtual void LoadFromEntity(object entity)
        {
        }

        protected virtual void LoadValidationResult(IValidationResult result)
        {
        }

        protected sealed override void PrivateClearObject()
        {
            object entity = this.Adapter.Create();
            this.PrivateLoadFromEntity(entity);
        }

        protected sealed override void PrivateCloneObject()
        {
            object entity = this.Entity;
            entity = this.Adapter.Clone(entity);
            this.PrivateLoadFromEntity(entity);
        }

        protected sealed override void PrivateDeleteObject()
        {
            object entity = this.Entity;
            int num = 1;
            while (true)
            {
                try
                {
                    this.Adapter.Delete(entity);
                    break;
                }
                catch (DeadlockException) when ((() => // NOTE: To create compilable code, filter at IL offset 0018 was represented using lambda expression.
                {
                    DeadlockException local2 = exception1;
                    return (num < 5);
                })())
                {
                }
                Thread.Sleep(500);
                num++;
            }
        }

        private void PrivateLoadFromEntity(object entity)
        {
            this.LoadFromEntity(entity);
            this.m_entity = entity;
            this.LoadValidationResult(null);
        }

        protected sealed override void PrivateLoadObject(object key)
        {
            object entity = this.Adapter.Load(key);
            this.PrivateLoadFromEntity(entity);
        }

        protected sealed override bool PrivateSaveObject()
        {
            object obj3;
            object entity = this.Entity;
            this.SaveToEntity(entity);
            if (!this.PrivateValidateEntity(entity))
            {
                return false;
            }
            int num = 1;
            while (true)
            {
                try
                {
                    obj3 = this.Adapter.Save(entity);
                    break;
                }
                catch (DeadlockException) when ((() => // NOTE: To create compilable code, filter at IL offset 002B was represented using lambda expression.
                {
                    DeadlockException local2 = exception1;
                    return (num < 5);
                })())
                {
                }
                Thread.Sleep(500);
                num++;
            }
            this.PrivateLoadFromEntity(obj3);
            return true;
        }

        private bool PrivateValidateEntity(object entity)
        {
            this.LoadValidationResult(null);
            IValidationResult result = this.Adapter.Validate(entity);
            this.LoadValidationResult(result);
            Func<IEnumerable<IError>, IEnumerable<string>> selector = <>c.<>9__11_0;
            if (<>c.<>9__11_0 == null)
            {
                Func<IEnumerable<IError>, IEnumerable<string>> local1 = <>c.<>9__11_0;
                selector = <>c.<>9__11_0 = delegate (IEnumerable<IError> v) {
                    Func<IError, bool> predicate = <>c.<>9__11_2;
                    if (<>c.<>9__11_2 == null)
                    {
                        Func<IError, bool> local1 = <>c.<>9__11_2;
                        predicate = <>c.<>9__11_2 = e => e.IsError;
                    }
                    Func<IError, string> func2 = <>c.<>9__11_3;
                    if (<>c.<>9__11_3 == null)
                    {
                        Func<IError, string> local2 = <>c.<>9__11_3;
                        func2 = <>c.<>9__11_3 = e => e.Message;
                    }
                    return v.Where<IError>(predicate).Select<IError, string>(func2);
                };
            }
            List<string> source = result.Values.SelectMany<IEnumerable<IError>, string>(selector).ToList<string>();
            if (source.Any<string>())
            {
                StringBuilder builder = new StringBuilder("There are some errors in the input data");
                foreach (string str in source)
                {
                    builder.Append("\r\n").Append(str);
                }
                builder.Append("\r\n");
                builder.Append("\r\n");
                builder.Append("Cannot proceed.");
                MessageBox.Show(builder.ToString(), this.Text + " - validation errors", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                return false;
            }
            Func<IEnumerable<IError>, IEnumerable<string>> func2 = <>c.<>9__11_1;
            if (<>c.<>9__11_1 == null)
            {
                Func<IEnumerable<IError>, IEnumerable<string>> local2 = <>c.<>9__11_1;
                func2 = <>c.<>9__11_1 = delegate (IEnumerable<IError> v) {
                    Func<IError, bool> predicate = <>c.<>9__11_4;
                    if (<>c.<>9__11_4 == null)
                    {
                        Func<IError, bool> local1 = <>c.<>9__11_4;
                        predicate = <>c.<>9__11_4 = e => !e.IsError;
                    }
                    Func<IError, string> func2 = <>c.<>9__11_5;
                    if (<>c.<>9__11_5 == null)
                    {
                        Func<IError, string> local2 = <>c.<>9__11_5;
                        func2 = <>c.<>9__11_5 = e => e.Message;
                    }
                    return v.Where<IError>(predicate).Select<IError, string>(func2);
                };
            }
            List<string> list2 = result.Values.SelectMany<IEnumerable<IError>, string>(func2).ToList<string>();
            if (!list2.Any<string>())
            {
                return true;
            }
            StringBuilder builder2 = new StringBuilder("There are some warnings in the input data");
            foreach (string str2 in list2)
            {
                builder2.Append("\r\n").Append(str2);
            }
            builder2.Append("\r\n");
            builder2.Append("\r\n");
            builder2.Append("Do you want to proceed?");
            return (MessageBox.Show(builder2.ToString(), this.Text + " - validation warnings", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2) == DialogResult.Yes);
        }

        protected virtual void SaveToEntity(object entity)
        {
        }

        private IAdapter Adapter
        {
            get
            {
                this.m_adapter ??= this.CreateAdapter();
                return this.m_adapter;
            }
        }

        private object Entity
        {
            get
            {
                this.m_entity ??= this.Adapter.Create();
                return this.m_entity;
            }
        }

        [Serializable, CompilerGenerated]
        private sealed class <>c
        {
            public static readonly FormEntityMaintain.<>c <>9 = new FormEntityMaintain.<>c();
            public static Func<IError, bool> <>9__11_2;
            public static Func<IError, string> <>9__11_3;
            public static Func<IEnumerable<IError>, IEnumerable<string>> <>9__11_0;
            public static Func<IError, bool> <>9__11_4;
            public static Func<IError, string> <>9__11_5;
            public static Func<IEnumerable<IError>, IEnumerable<string>> <>9__11_1;

            internal IEnumerable<string> <PrivateValidateEntity>b__11_0(IEnumerable<IError> v)
            {
                Func<IError, bool> predicate = <>9__11_2;
                if (<>9__11_2 == null)
                {
                    Func<IError, bool> local1 = <>9__11_2;
                    predicate = <>9__11_2 = e => e.IsError;
                }
                Func<IError, string> selector = <>9__11_3;
                if (<>9__11_3 == null)
                {
                    Func<IError, string> local2 = <>9__11_3;
                    selector = <>9__11_3 = e => e.Message;
                }
                return v.Where<IError>(predicate).Select<IError, string>(selector);
            }

            internal IEnumerable<string> <PrivateValidateEntity>b__11_1(IEnumerable<IError> v)
            {
                Func<IError, bool> predicate = <>9__11_4;
                if (<>9__11_4 == null)
                {
                    Func<IError, bool> local1 = <>9__11_4;
                    predicate = <>9__11_4 = e => !e.IsError;
                }
                Func<IError, string> selector = <>9__11_5;
                if (<>9__11_5 == null)
                {
                    Func<IError, string> local2 = <>9__11_5;
                    selector = <>9__11_5 = e => e.Message;
                }
                return v.Where<IError>(predicate).Select<IError, string>(selector);
            }

            internal bool <PrivateValidateEntity>b__11_2(IError e) => 
                e.IsError;

            internal string <PrivateValidateEntity>b__11_3(IError e) => 
                e.Message;

            internal bool <PrivateValidateEntity>b__11_4(IError e) => 
                !e.IsError;

            internal string <PrivateValidateEntity>b__11_5(IError e) => 
                e.Message;
        }
    }
}


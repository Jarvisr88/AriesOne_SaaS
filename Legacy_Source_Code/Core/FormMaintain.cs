namespace DMEWorks.Core
{
    using Devart.Data.MySql;
    using DMEWorks.Data;
    using DMEWorks.Forms;
    using System;
    using System.Data;
    using System.Text;
    using System.Threading;
    using System.Windows.Forms;

    public class FormMaintain : FormMaintainBase
    {
        protected sealed override FormMaintainBase.ObjectInfo GetCurrentObjectInfo() => 
            !this.IsNew ? FormMaintainBase.ObjectInfo.CreateExisting(this.ObjectID) : FormMaintainBase.ObjectInfo.CreateNew();

        protected virtual void IntClearObject()
        {
        }

        protected virtual void IntCloneObject()
        {
        }

        protected virtual void IntDeleteObject(object ID)
        {
        }

        protected virtual bool IntLoadObject(object ID) => 
            false;

        protected virtual bool IntSaveObject(object ID, bool IsNew) => 
            false;

        protected virtual void IntValidateObject(object ID, bool IsNew)
        {
        }

        protected sealed override void PrivateClearObject()
        {
            this.IntClearObject();
            this.PrivateClearValidationErrors();
            this.IsNew = true;
        }

        private void PrivateClearValidationErrors()
        {
            Utilities.ClearErrors(this, base.ValidationErrors);
            Utilities.ClearErrors(this, base.ValidationWarnings);
        }

        protected sealed override void PrivateCloneObject()
        {
            this.IntCloneObject();
            this.PrivateClearValidationErrors();
            this.IsNew = true;
        }

        protected sealed override void PrivateDeleteObject()
        {
            int num = 1;
            while (true)
            {
                try
                {
                    this.IntDeleteObject(this.ObjectID);
                    break;
                }
                catch (MySqlException exception1) when ((() => // NOTE: To create compilable code, filter at IL offset 0011 was represented using lambda expression.
                {
                    return (exception1.Code == 0x4bd);
                })())
                {
                    if (5 <= num)
                    {
                        MySqlException exception;
                        throw new DeadlockException("", exception);
                    }
                }
                Thread.Sleep(500);
                num++;
            }
        }

        protected sealed override void PrivateLoadObject(object key)
        {
            if (this.IntLoadObject(key))
            {
                this.PrivateClearValidationErrors();
                this.IsNew = false;
            }
        }

        protected sealed override bool PrivateSaveObject()
        {
            bool flag2;
            if (!this.PrivateValidateObject())
            {
                return false;
            }
            object objectID = this.ObjectID;
            bool isNew = this.IsNew;
            int num = 0;
            while (true)
            {
                DBConcurrencyException exception2;
                try
                {
                    flag2 = this.IntSaveObject(objectID, isNew);
                    break;
                }
                catch (MySqlException exception1) when ((() => // NOTE: To create compilable code, filter at IL offset 0026 was represented using lambda expression.
                {
                    return (exception1.Code == 0x4bd);
                })())
                {
                    if (5 <= num)
                    {
                        MySqlException exception;
                        throw new DeadlockException("", exception);
                    }
                }
                catch (DBConcurrencyException exception3) when ((() => // NOTE: To create compilable code, filter at IL offset 005B was represented using lambda expression.
                {
                    exception2 = exception3;
                    return !isNew;
                })())
                {
                    throw new ObjectIsModifiedException("", exception2);
                }
                Thread.Sleep(500);
                num++;
            }
            if (flag2)
            {
                this.IsNew = false;
            }
            return flag2;
        }

        private bool PrivateValidateObject()
        {
            this.PrivateClearValidationErrors();
            this.IntValidateObject(this.ObjectID, this.IsNew);
            StringBuilder builder = new StringBuilder("There are some errors in the input data");
            if (0 < Utilities.EnumerateErrors(this, base.ValidationErrors, builder))
            {
                builder.Append("\r\n");
                builder.Append("\r\n");
                builder.Append("Cannot proceed.");
                MessageBox.Show(builder.ToString(), this.Text + " - validation errors", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                return false;
            }
            StringBuilder builder2 = new StringBuilder("There are some warnings in the input data");
            if (0 >= Utilities.EnumerateErrors(this, base.ValidationWarnings, builder2))
            {
                return true;
            }
            builder2.Append("\r\n");
            builder2.Append("\r\n");
            builder2.Append("Do you want to proceed?");
            return (MessageBox.Show(builder2.ToString(), this.Text + " - validation warnings", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2) == DialogResult.Yes);
        }

        protected virtual bool IsNew
        {
            get => 
                true;
            set
            {
            }
        }

        protected virtual object ObjectID
        {
            get => 
                null;
            set
            {
            }
        }
    }
}


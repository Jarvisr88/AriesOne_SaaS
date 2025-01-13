-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema c01
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema c01
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `c01` DEFAULT CHARACTER SET latin1 COLLATE latin1_general_ci ;
-- -----------------------------------------------------
-- Schema dmeworks
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema repository
-- -----------------------------------------------------
USE `c01` ;
USE `c01`;

DELIMITER $$
USE `c01`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `c01`.`tbl_invoice_transaction_beforeinsert`
BEFORE INSERT ON `c01`.`tbl_invoice_transaction`
FOR EACH ROW
BEGIN
  DECLARE V_OldValue DECIMAL(18, 2) DEFAULT (0); --
  DECLARE V_Quantity DOUBLE DEFAULT (0); --
  DECLARE V_TranType VARCHAR(50); --

  -- we will allow to change Allowable, Billable and Taxes through transactions but in UI
  -- all will stay the same

  SELECT Name
  INTO V_TranType
  FROM tbl_invoice_transactiontype
  WHERE ID = NEW.TransactionTypeID; --

  IF (V_TranType = 'Adjust Allowable') THEN
    SELECT AllowableAmount, Quantity
    INTO V_OldValue, V_Quantity
    FROM tbl_invoicedetails
    WHERE (CustomerID = NEW.CustomerID) AND (InvoiceID = NEW.InvoiceID) AND (ID = NEW.InvoiceDetailsID); --

    SET NEW.Quantity = V_Quantity; --
    SET NEW.Comments = Concat('Previous Value=', V_OldValue); --

    IF 0.001 < ABS(V_OldValue - NEW.Amount) THEN
      UPDATE tbl_invoicedetails
      SET AllowableAmount = NEW.Amount
      WHERE (CustomerID = NEW.CustomerID) AND (InvoiceID = NEW.InvoiceID) AND (ID = NEW.InvoiceDetailsID); --
    END IF; --
  ELSEIF (V_TranType = 'Adjust Customary') THEN
    SELECT BillableAmount, Quantity
    INTO V_OldValue, V_Quantity
    FROM tbl_invoicedetails
    WHERE (CustomerID = NEW.CustomerID) AND (InvoiceID = NEW.InvoiceID) AND (ID = NEW.InvoiceDetailsID); --

    SET NEW.Quantity = V_Quantity; --
    SET NEW.Comments = Concat('Previous Value=', V_OldValue); --

    IF 0.001 < ABS(V_OldValue - NEW.Amount) THEN
      UPDATE tbl_invoicedetails
      SET BillableAmount = NEW.Amount
      WHERE (CustomerID = NEW.CustomerID) AND (InvoiceID = NEW.InvoiceID) AND (ID = NEW.InvoiceDetailsID); --
    END IF; --
  ELSEIF (V_TranType = 'Adjust Taxes') THEN
    SELECT Taxes, Quantity
    INTO V_OldValue, V_Quantity
    FROM tbl_invoicedetails
    WHERE (CustomerID = NEW.CustomerID) AND (InvoiceID = NEW.InvoiceID) AND (ID = NEW.InvoiceDetailsID); --

    SET NEW.Quantity = V_Quantity; --
    SET NEW.Comments = Concat('Previous Value=', V_OldValue); --

    IF 0.001 < ABS(V_OldValue - NEW.Amount) THEN
      UPDATE tbl_invoicedetails
      SET Taxes = NEW.Amount
      WHERE (CustomerID = NEW.CustomerID) AND (InvoiceID = NEW.InvoiceID) AND (ID = NEW.InvoiceDetailsID); --
    END IF; --
  END IF; --
END$$


DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

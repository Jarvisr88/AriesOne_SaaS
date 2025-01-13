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
-- Schema dmeworks
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `dmeworks` DEFAULT CHARACTER SET latin1 COLLATE latin1_general_ci ;
-- -----------------------------------------------------
-- Schema repository
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema repository
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `repository` DEFAULT CHARACTER SET latin1 COLLATE latin1_general_ci ;
USE `c01` ;

-- -----------------------------------------------------
-- Table `c01`.`tbl_ability_eligibility_request`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_ability_eligibility_request` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` INT(11) NOT NULL,
  `CustomerInsuranceID` INT(11) NOT NULL,
  `RequestTime` DATETIME NOT NULL,
  `RequestText` MEDIUMTEXT NOT NULL,
  `ResponseTime` DATETIME NULL DEFAULT NULL,
  `ResponseText` MEDIUMTEXT NULL DEFAULT NULL,
  `SubmissionTime` DATETIME NULL DEFAULT NULL,
  `SubmissionText` MEDIUMTEXT NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_authorizationtype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_authorizationtype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_batchpayment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_batchpayment` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InsuranceCompanyID` INT(11) NOT NULL,
  `CheckNumber` VARCHAR(14) NOT NULL,
  `CheckDate` DATE NOT NULL,
  `CheckAmount` DECIMAL(18,2) NOT NULL,
  `AmountUsed` DECIMAL(18,2) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NOT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_billingtype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_billingtype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_changes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_changes` (
  `TableName` VARCHAR(64) NOT NULL,
  `SessionID` INT(11) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NOT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`TableName`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CMNType` ENUM('DMERC 01.02A', 'DMERC 01.02B', 'DMERC 02.03A', 'DMERC 02.03B', 'DMERC 03.02', 'DMERC 04.03B', 'DMERC 04.03C', 'DMERC 06.02B', 'DMERC 07.02A', 'DMERC 07.02B', 'DMERC 08.02', 'DMERC 09.02', 'DMERC 10.02A', 'DMERC 10.02B', 'DMERC 484.2', 'DMERC DRORDER', 'DMERC URO', 'DME 04.04B', 'DME 04.04C', 'DME 06.03B', 'DME 07.03A', 'DME 09.03', 'DME 10.03', 'DME 484.03') NOT NULL DEFAULT 'DME 484.03',
  `InitialDate` DATE NULL DEFAULT NULL,
  `RevisedDate` DATE NULL DEFAULT NULL,
  `RecertificationDate` DATE NULL DEFAULT NULL,
  `CustomerID` INT(11) NULL DEFAULT NULL,
  `Customer_ICD9_1` VARCHAR(8) NULL DEFAULT NULL,
  `Customer_ICD9_2` VARCHAR(8) NULL DEFAULT NULL,
  `Customer_ICD9_3` VARCHAR(8) NULL DEFAULT NULL,
  `Customer_ICD9_4` VARCHAR(8) NULL DEFAULT NULL,
  `DoctorID` INT(11) NULL DEFAULT NULL,
  `POSTypeID` INT(11) NULL DEFAULT NULL,
  `FacilityID` INT(11) NULL DEFAULT NULL,
  `AnsweringName` VARCHAR(50) NOT NULL DEFAULT '',
  `AnsweringTitle` VARCHAR(50) NOT NULL DEFAULT '',
  `AnsweringEmployer` VARCHAR(50) NOT NULL DEFAULT '',
  `EstimatedLengthOfNeed` INT(11) NOT NULL DEFAULT '0',
  `Signature_Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Signature_Date` DATE NULL DEFAULT NULL,
  `OnFile` TINYINT(1) NOT NULL DEFAULT '0',
  `OrderID` INT(11) NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `MIR` SET('CMNType', 'InitialDate', 'CustomerID', 'Customer', 'ICD9_1.Required', 'ICD9_1.Unknown', 'ICD9_1.Inactive', 'ICD9_2.Unknown', 'ICD9_2.Inactive', 'ICD9_3.Unknown', 'ICD9_3.Inactive', 'ICD9_4.Unknown', 'ICD9_4.Inactive', 'DoctorID', 'Doctor', 'POSTypeID', 'EstimatedLengthOfNeed', 'Signature_Name', 'Signature_Date', 'Answers') NOT NULL DEFAULT '',
  `Customer_UsingICD10` TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 83
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0102a`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0102a` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer5` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer6` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer7` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0102b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0102b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer12` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer13` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer14` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer15` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer16` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer19` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer20` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer21_Ulcer1_Stage` VARCHAR(30) NULL DEFAULT NULL,
  `Answer21_Ulcer1_MaxLength` DOUBLE NULL DEFAULT NULL,
  `Answer21_Ulcer1_MaxWidth` DOUBLE NULL DEFAULT NULL,
  `Answer21_Ulcer2_Stage` VARCHAR(30) NULL DEFAULT NULL,
  `Answer21_Ulcer2_MaxLength` DOUBLE NULL DEFAULT NULL,
  `Answer21_Ulcer2_MaxWidth` DOUBLE NULL DEFAULT NULL,
  `Answer21_Ulcer3_Stage` VARCHAR(30) NULL DEFAULT NULL,
  `Answer21_Ulcer3_MaxLength` DOUBLE NULL DEFAULT NULL,
  `Answer21_Ulcer3_MaxWidth` DOUBLE NULL DEFAULT NULL,
  `Answer22` ENUM('1', '2', '3') NOT NULL DEFAULT '1',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0203a`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0203a` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer2` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer5` INT(11) NULL DEFAULT NULL,
  `Answer6` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer7` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0203b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0203b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer2` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer5` INT(11) NULL DEFAULT NULL,
  `Answer8` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer9` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0302`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0302` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer12` INT(11) NULL DEFAULT NULL,
  `Answer14` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0403b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0403b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer2` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer5` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0403c`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0403c` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer6a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer6b` INT(11) NOT NULL DEFAULT '0',
  `Answer7a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer7b` INT(11) NOT NULL DEFAULT '0',
  `Answer8` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer9a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer9b` INT(11) NOT NULL DEFAULT '0',
  `Answer10a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer10b` INT(11) NOT NULL DEFAULT '0',
  `Answer10c` INT(11) NOT NULL DEFAULT '0',
  `Answer11a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer11b` INT(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0404b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0404b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer2` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer3` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer4` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer5` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0404c`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0404c` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer6` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer7a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer7b` VARCHAR(10) NULL DEFAULT NULL,
  `Answer8` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer9a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer9b` VARCHAR(10) NULL DEFAULT NULL,
  `Answer10a` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer10b` VARCHAR(10) NULL DEFAULT NULL,
  `Answer10c` VARCHAR(10) NULL DEFAULT NULL,
  `Answer11` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer12` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0602b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0602b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer2` DATE NULL DEFAULT NULL,
  `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer4` INT(11) NULL DEFAULT NULL,
  `Answer5` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1',
  `Answer6` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer7` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer8_begun` DATE NULL DEFAULT NULL,
  `Answer8_ended` DATE NULL DEFAULT NULL,
  `Answer9` DATE NULL DEFAULT NULL,
  `Answer10` ENUM('1', '2', '3') NOT NULL DEFAULT '1',
  `Answer11` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer12` ENUM('2', '4') NOT NULL DEFAULT '2',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0603b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0603b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer2` INT(11) NULL DEFAULT NULL,
  `Answer3` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '5',
  `Answer4` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer5` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer6` DATE NULL DEFAULT NULL,
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0702a`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0702a` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer2` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer5` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0702b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0702b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer6` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer7` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer8` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer12` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer13` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer14` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0703a`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0703a` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer2` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer5` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0802`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0802` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1_HCPCS` VARCHAR(5) NOT NULL DEFAULT '',
  `Answer1_MG` INT(11) NULL DEFAULT NULL,
  `Answer1_Times` INT(11) NULL DEFAULT NULL,
  `Answer2_HCPCS` VARCHAR(5) NOT NULL DEFAULT '',
  `Answer2_MG` INT(11) NULL DEFAULT NULL,
  `Answer2_Times` INT(11) NULL DEFAULT NULL,
  `Answer3_HCPCS` VARCHAR(5) NOT NULL DEFAULT '',
  `Answer3_MG` INT(11) NULL DEFAULT NULL,
  `Answer3_Times` INT(11) NULL DEFAULT NULL,
  `Answer4` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  `Answer5_1` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1',
  `Answer5_2` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1',
  `Answer5_3` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1',
  `Answer8` VARCHAR(60) NOT NULL DEFAULT '',
  `Answer9` VARCHAR(20) NOT NULL DEFAULT '',
  `Answer10` VARCHAR(2) NOT NULL DEFAULT '',
  `Answer11` DATE NULL DEFAULT NULL,
  `Answer12` ENUM('Y', 'N') NOT NULL DEFAULT 'N',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0902`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0902` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('1', '3', '4') NOT NULL DEFAULT '1',
  `Answer2` VARCHAR(50) NOT NULL DEFAULT '',
  `Answer3` VARCHAR(50) NOT NULL DEFAULT '',
  `Answer4` ENUM('1', '3', '4') NOT NULL DEFAULT '1',
  `Answer5` ENUM('1', '2', '3') NOT NULL DEFAULT '1',
  `Answer6` INT(11) NOT NULL DEFAULT '1',
  `Answer7` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_0903`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_0903` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1a` VARCHAR(10) NULL DEFAULT NULL,
  `Answer1b` VARCHAR(10) NULL DEFAULT NULL,
  `Answer1c` VARCHAR(10) NULL DEFAULT NULL,
  `Answer2a` VARCHAR(50) NULL DEFAULT NULL,
  `Answer2b` VARCHAR(50) NULL DEFAULT NULL,
  `Answer2c` VARCHAR(50) NULL DEFAULT NULL,
  `Answer3` ENUM('1', '2', '3', '4') NOT NULL DEFAULT '1',
  `Answer4` ENUM('1', '2') NOT NULL DEFAULT '1',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_1002a`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_1002a` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer3` INT(11) NULL DEFAULT NULL,
  `Concentration_AminoAcid` DOUBLE NULL DEFAULT NULL,
  `Concentration_Dextrose` DOUBLE NULL DEFAULT NULL,
  `Concentration_Lipids` DOUBLE NULL DEFAULT NULL,
  `Dose_AminoAcid` DOUBLE NULL DEFAULT NULL,
  `Dose_Dextrose` DOUBLE NULL DEFAULT NULL,
  `Dose_Lipids` DOUBLE NULL DEFAULT NULL,
  `DaysPerWeek_Lipids` DOUBLE NULL DEFAULT NULL,
  `GmsPerDay_AminoAcid` DOUBLE NULL DEFAULT NULL,
  `Answer5` ENUM('1', '3', '7') NOT NULL DEFAULT '1',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_1002b`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_1002b` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer7` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer8` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer10a` VARCHAR(50) NOT NULL DEFAULT '',
  `Answer10b` VARCHAR(50) NOT NULL DEFAULT '',
  `Answer11a` VARCHAR(50) NOT NULL DEFAULT '',
  `Answer11b` VARCHAR(50) NOT NULL DEFAULT '',
  `Answer12` INT(11) NULL DEFAULT NULL,
  `Answer13` ENUM('1', '2', '3', '4') NOT NULL DEFAULT '1',
  `Answer14` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer15` VARCHAR(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_1003`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_1003` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer2` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer3a` VARCHAR(10) NULL DEFAULT NULL,
  `Answer3b` VARCHAR(10) NULL DEFAULT NULL,
  `Answer4a` INT(11) NULL DEFAULT NULL,
  `Answer4b` INT(11) NULL DEFAULT NULL,
  `Answer5` ENUM('1', '2', '3', '4') NOT NULL DEFAULT '1',
  `Answer6` INT(11) NULL DEFAULT NULL,
  `Answer7` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer8a` INT(11) NULL DEFAULT NULL,
  `Answer8b` INT(11) NULL DEFAULT NULL,
  `Answer8c` INT(11) NULL DEFAULT NULL,
  `Answer8d` INT(11) NULL DEFAULT NULL,
  `Answer8e` INT(11) NULL DEFAULT NULL,
  `Answer8f` INT(11) NULL DEFAULT NULL,
  `Answer8g` INT(11) NULL DEFAULT NULL,
  `Answer8h` INT(11) NULL DEFAULT NULL,
  `Answer9` ENUM('1', '2', '3') NOT NULL DEFAULT '1',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_48403`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_48403` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1a` INT(11) NULL DEFAULT NULL,
  `Answer1b` INT(11) NULL DEFAULT NULL,
  `Answer1c` DATE NULL DEFAULT NULL,
  `Answer2` ENUM('1', '2', '3') NOT NULL DEFAULT '1',
  `Answer3` ENUM('1', '2', '3') NOT NULL DEFAULT '1',
  `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer5` VARCHAR(10) NULL DEFAULT NULL,
  `Answer6a` INT(11) NULL DEFAULT NULL,
  `Answer6b` INT(11) NULL DEFAULT NULL,
  `Answer6c` DATE NULL DEFAULT NULL,
  `Answer7` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer8` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer9` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_4842`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_4842` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Answer1a` INT(11) NULL DEFAULT NULL,
  `Answer1b` INT(11) NULL DEFAULT NULL,
  `Answer1c` DATE NULL DEFAULT NULL,
  `Answer2` ENUM('Y', 'N') NOT NULL DEFAULT 'Y',
  `Answer3` ENUM('1', '2', '3') NOT NULL DEFAULT '1',
  `PhysicianAddress` VARCHAR(50) NOT NULL DEFAULT '',
  `PhysicianCity` VARCHAR(50) NOT NULL DEFAULT '',
  `PhysicianState` VARCHAR(50) NOT NULL DEFAULT '',
  `PhysicianZip` VARCHAR(50) NOT NULL DEFAULT '',
  `PhysicianName` VARCHAR(50) NOT NULL DEFAULT '',
  `Answer5` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer6` VARCHAR(10) NULL DEFAULT NULL,
  `Answer7a` INT(11) NULL DEFAULT NULL,
  `Answer7b` INT(11) NULL DEFAULT NULL,
  `Answer7c` DATE NULL DEFAULT NULL,
  `Answer8` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer9` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  `Answer10` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_details`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_details` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `BillingCode` VARCHAR(50) NULL DEFAULT NULL,
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0',
  `OrderedQuantity` DOUBLE NOT NULL DEFAULT '0',
  `OrderedUnits` VARCHAR(50) NULL DEFAULT NULL,
  `BillablePrice` DOUBLE NOT NULL DEFAULT '0',
  `AllowablePrice` DOUBLE NOT NULL DEFAULT '0',
  `Period` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Semi-Annually', 'Annually', 'Custom') NOT NULL DEFAULT 'One time',
  `Modifier1` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier2` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier3` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier4` VARCHAR(8) NOT NULL DEFAULT '',
  `PredefinedTextID` INT(11) NULL DEFAULT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 333
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_drorder`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_drorder` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Prognosis` VARCHAR(50) NOT NULL DEFAULT '',
  `MedicalJustification` LONGTEXT NOT NULL,
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_cmnform_uro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_cmnform_uro` (
  `CMNFormID` INT(11) NOT NULL DEFAULT '0',
  `Prognosis` VARCHAR(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`CMNFormID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_company`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_company` (
  `Address1` VARCHAR(40) NOT NULL DEFAULT '',
  `Address2` VARCHAR(40) NOT NULL DEFAULT '',
  `BillCustomerCopayUpfront` TINYINT(1) NOT NULL DEFAULT '0',
  `City` VARCHAR(25) NOT NULL DEFAULT '',
  `Fax` VARCHAR(50) NOT NULL DEFAULT '',
  `FederalTaxID` VARCHAR(9) NOT NULL DEFAULT '',
  `TaxonomyCode` VARCHAR(20) NOT NULL DEFAULT '332B00000X',
  `EIN` VARCHAR(20) NOT NULL DEFAULT '',
  `SSN` VARCHAR(20) NOT NULL DEFAULT '',
  `TaxIDType` ENUM('SSN', 'EIN') NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `ParticipatingProvider` TINYINT(1) NOT NULL DEFAULT '0',
  `Phone` VARCHAR(50) NOT NULL DEFAULT '',
  `Phone2` VARCHAR(50) NOT NULL DEFAULT '',
  `POAuthorizationCodeReqiered` TINYINT(1) NOT NULL DEFAULT '0',
  `Print_PricesOnOrders` TINYINT(1) NOT NULL DEFAULT '0',
  `Picture` MEDIUMBLOB NULL DEFAULT NULL,
  `POSTypeID` INT(11) NULL DEFAULT '12',
  `State` CHAR(2) NOT NULL DEFAULT '',
  `SystemGenerate_BlanketAssignments` TINYINT(1) NOT NULL DEFAULT '0',
  `SystemGenerate_CappedRentalLetters` TINYINT(1) NOT NULL DEFAULT '0',
  `SystemGenerate_CustomerAccountNumbers` TINYINT(1) NOT NULL DEFAULT '0',
  `SystemGenerate_DeliveryPickupTickets` TINYINT(1) NOT NULL DEFAULT '0',
  `SystemGenerate_DroctorsOrder` TINYINT(1) NOT NULL DEFAULT '0',
  `SystemGenerate_HIPPAForms` TINYINT(1) NOT NULL DEFAULT '0',
  `SystemGenerate_PatientBillOfRights` TINYINT(1) NOT NULL DEFAULT '0',
  `SystemGenerate_PurchaseOrderNumber` TINYINT(1) NOT NULL DEFAULT '0',
  `WriteoffDifference` TINYINT(1) NOT NULL DEFAULT '0',
  `Zip` VARCHAR(10) NOT NULL DEFAULT '',
  `IncludeLocationInfo` TINYINT(1) NOT NULL DEFAULT '0',
  `Contact` VARCHAR(50) NOT NULL DEFAULT '',
  `Print_CompanyInfoOnInvoice` TINYINT(1) NOT NULL DEFAULT '0',
  `Print_CompanyInfoOnDelivery` TINYINT(1) NOT NULL DEFAULT '0',
  `Print_CompanyInfoOnPickup` TINYINT(1) NOT NULL DEFAULT '0',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Show_InactiveCustomers` TINYINT(1) NOT NULL DEFAULT '0',
  `WarehouseID` INT(11) NULL DEFAULT NULL,
  `NPI` VARCHAR(10) NULL DEFAULT NULL,
  `TaxRateID` INT(11) NULL DEFAULT NULL,
  `ImagingServer` VARCHAR(250) NULL DEFAULT NULL,
  `ZirmedNumber` VARCHAR(20) NOT NULL DEFAULT '',
  `AutomaticallyReorderInventory` TINYINT(1) NOT NULL DEFAULT '1',
  `AvailityNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `Show_QuantityOnHand` TINYINT(1) NOT NULL DEFAULT '0',
  `Use_Icd10ForNewCmnRx` TINYINT(1) NOT NULL DEFAULT '0',
  `OrderSurveyID` INT(11) NULL DEFAULT NULL,
  `AbilityIntegrationSettings` MEDIUMTEXT NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_compliance`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_compliance` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `OrderID` INT(11) NULL DEFAULT NULL,
  `DeliveryDate` DATE NOT NULL DEFAULT '0000-00-00',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_compliance_items`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_compliance_items` (
  `ComplianceID` INT(11) NOT NULL DEFAULT '0',
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0')
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_compliance_notes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_compliance_notes` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `ComplianceID` INT(11) NOT NULL DEFAULT '0',
  `Date` DATE NOT NULL DEFAULT '0000-00-00',
  `Done` TINYINT(1) NOT NULL DEFAULT '0',
  `Notes` LONGTEXT NOT NULL,
  `CreatedByUserID` SMALLINT(6) NULL DEFAULT NULL,
  `AssignedToUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  INDEX `IX_compliance_notes_Done_Date` (`Done` ASC, `Date` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_customer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_customer` (
  `AccountNumber` VARCHAR(40) NOT NULL DEFAULT '',
  `Address1` VARCHAR(40) NOT NULL DEFAULT '',
  `Address2` VARCHAR(40) NOT NULL DEFAULT '',
  `BillingTypeID` INT(11) NULL DEFAULT NULL,
  `City` VARCHAR(25) NOT NULL DEFAULT '',
  `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL DEFAULT 'Dr.',
  `CustomerBalance` DOUBLE NULL DEFAULT NULL,
  `CustomerClassCode` CHAR(2) NULL DEFAULT NULL,
  `CustomerTypeID` INT(11) NULL DEFAULT NULL,
  `DeceasedDate` DATE NULL DEFAULT NULL,
  `DateofBirth` DATE NULL DEFAULT NULL,
  `FirstName` VARCHAR(25) NOT NULL DEFAULT '',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `LastName` VARCHAR(30) NOT NULL DEFAULT '',
  `LocationID` INT(11) NULL DEFAULT NULL,
  `MiddleName` CHAR(1) NOT NULL DEFAULT '',
  `Phone` VARCHAR(50) NOT NULL DEFAULT '',
  `Phone2` VARCHAR(50) NOT NULL DEFAULT '',
  `State` CHAR(2) NOT NULL DEFAULT '',
  `Suffix` VARCHAR(4) NOT NULL DEFAULT '',
  `TotalBalance` DOUBLE NULL DEFAULT NULL,
  `Zip` VARCHAR(10) NOT NULL DEFAULT '',
  `BillActive` TINYINT(1) NOT NULL DEFAULT '0',
  `BillAddress1` VARCHAR(40) NOT NULL DEFAULT '',
  `BillAddress2` VARCHAR(40) NOT NULL DEFAULT '',
  `BillCity` VARCHAR(25) NOT NULL DEFAULT '',
  `BillName` VARCHAR(50) NOT NULL DEFAULT '',
  `BillState` CHAR(2) NOT NULL DEFAULT '',
  `BillZip` VARCHAR(10) NOT NULL DEFAULT '',
  `CommercialAccount` TINYINT(1) NULL DEFAULT NULL,
  `DeliveryDirections` LONGTEXT NOT NULL,
  `EmploymentStatus` ENUM('Unknown', 'Full Time', 'Part Time', 'Retired', 'Student', 'Unemployed') NOT NULL DEFAULT 'Unknown',
  `Gender` ENUM('Male', 'Female') NOT NULL DEFAULT 'Male',
  `Height` DOUBLE NULL DEFAULT NULL,
  `License` VARCHAR(50) NOT NULL DEFAULT '',
  `MaritalStatus` ENUM('Unknown', 'Single', 'Married', 'Legaly Separated', 'Divorced', 'Widowed') NOT NULL DEFAULT 'Unknown',
  `MilitaryBranch` ENUM('N/A', 'Army', 'Air Force', 'Navy', 'Marines', 'Coast Guard', 'National Guard') NOT NULL DEFAULT 'N/A',
  `MilitaryStatus` ENUM('N/A', 'Active', 'Reserve', 'Retired') NOT NULL DEFAULT 'N/A',
  `ShipActive` TINYINT(1) NOT NULL DEFAULT '0',
  `ShipAddress1` VARCHAR(40) NOT NULL DEFAULT '',
  `ShipAddress2` VARCHAR(40) NOT NULL DEFAULT '',
  `ShipCity` VARCHAR(25) NOT NULL DEFAULT '',
  `ShipName` VARCHAR(50) NOT NULL DEFAULT '',
  `ShipState` CHAR(2) NOT NULL DEFAULT '',
  `ShipZip` VARCHAR(10) NOT NULL DEFAULT '',
  `SSNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `StudentStatus` ENUM('N/A', 'Full Time', 'Part Time') NOT NULL DEFAULT 'N/A',
  `Weight` DOUBLE NULL DEFAULT NULL,
  `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill',
  `Block12HCFA` TINYINT(1) NOT NULL DEFAULT '0',
  `Block13HCFA` TINYINT(1) NOT NULL DEFAULT '0',
  `CommercialAcctCreditLimit` DOUBLE NULL DEFAULT NULL,
  `CommercialAcctTerms` VARCHAR(50) NOT NULL DEFAULT '',
  `CopayDollar` DOUBLE NULL DEFAULT NULL,
  `Deductible` DOUBLE NULL DEFAULT NULL,
  `Frequency` ENUM('Per Visit', 'Monthly', 'Yearly') NOT NULL DEFAULT 'Per Visit',
  `Hardship` TINYINT(1) NOT NULL DEFAULT '0',
  `MonthsValid` INT(11) NOT NULL DEFAULT '0',
  `OutOfPocket` DOUBLE NULL DEFAULT NULL,
  `SignatureOnFile` DATE NULL DEFAULT NULL,
  `SignatureType` CHAR(1) NULL DEFAULT NULL,
  `TaxRateID` INT(11) NULL DEFAULT NULL,
  `Doctor1_ID` INT(11) NULL DEFAULT NULL,
  `Doctor2_ID` INT(11) NULL DEFAULT NULL,
  `EmergencyContact` LONGTEXT NOT NULL,
  `FacilityID` INT(11) NULL DEFAULT NULL,
  `LegalRepID` INT(11) NULL DEFAULT NULL,
  `ReferralID` INT(11) NULL DEFAULT NULL,
  `SalesRepID` INT(11) NULL DEFAULT NULL,
  `AccidentType` ENUM('Auto', 'No', 'Other') NOT NULL,
  `StateOfAccident` CHAR(2) NOT NULL DEFAULT '',
  `DateOfInjury` DATE NULL DEFAULT NULL,
  `Emergency` TINYINT(1) NOT NULL DEFAULT '0',
  `EmploymentRelated` TINYINT(1) NOT NULL DEFAULT '0',
  `FirstConsultDate` DATE NULL DEFAULT NULL,
  `ICD9_1` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_2` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_3` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_4` VARCHAR(6) NULL DEFAULT NULL,
  `POSTypeID` INT(11) NULL DEFAULT NULL,
  `ReturnToWorkDate` DATE NULL DEFAULT NULL,
  `CopayPercent` DOUBLE NULL DEFAULT NULL,
  `SetupDate` DATE NOT NULL DEFAULT '0000-00-00',
  `HIPPANote` TINYINT(1) NOT NULL DEFAULT '0',
  `SupplierStandards` TINYINT(1) NOT NULL DEFAULT '0',
  `InactiveDate` DATE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `InvoiceFormID` INT(11) NULL DEFAULT '4',
  `MIR` SET('AccountNumber', 'FirstName', 'LastName', 'Address1', 'City', 'State', 'Zip', 'EmploymentStatus', 'Gender', 'MaritalStatus', 'MilitaryBranch', 'MilitaryStatus', 'StudentStatus', 'MonthsValid', 'DateofBirth', 'SignatureOnFile', 'Doctor1_ID', 'Doctor1', 'ICD9_1') NOT NULL DEFAULT '',
  `Email` VARCHAR(150) NULL DEFAULT NULL,
  `Collections` BIT(1) NOT NULL DEFAULT b'0',
  `ICD10_01` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_02` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_03` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_04` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_05` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_06` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_07` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_08` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_09` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_10` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_11` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_12` VARCHAR(8) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `AccountNumber` (`AccountNumber` ASC) VISIBLE,
  INDEX `IDX_FIRST_LAST_DOB_MIDDLE` (`FirstName` ASC, `LastName` ASC, `DateofBirth` ASC, `MiddleName` ASC) VISIBLE,
  INDEX `IX_customer_InactiveDate` (`InactiveDate` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 52
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_customer_insurance`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_customer_insurance` (
  `Address1` VARCHAR(40) NOT NULL DEFAULT '',
  `Address2` VARCHAR(40) NOT NULL DEFAULT '',
  `City` VARCHAR(25) NOT NULL DEFAULT '',
  `State` CHAR(2) NOT NULL DEFAULT '',
  `Zip` VARCHAR(10) NOT NULL DEFAULT '',
  `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill',
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `DateofBirth` DATE NULL DEFAULT NULL,
  `Gender` ENUM('Male', 'Female') NOT NULL DEFAULT 'Male',
  `GroupNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InactiveDate` DATE NULL DEFAULT NULL,
  `InsuranceCompanyID` INT(11) NOT NULL DEFAULT '0',
  `InsuranceType` CHAR(2) NULL DEFAULT NULL,
  `FirstName` VARCHAR(25) NOT NULL DEFAULT '',
  `LastName` VARCHAR(30) NOT NULL DEFAULT '',
  `MiddleName` CHAR(1) NOT NULL DEFAULT '',
  `Employer` VARCHAR(50) NOT NULL DEFAULT '',
  `Mobile` VARCHAR(50) NOT NULL DEFAULT '',
  `PaymentPercent` INT(11) NULL DEFAULT NULL,
  `Phone` VARCHAR(50) NOT NULL DEFAULT '',
  `PolicyNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `Rank` INT(11) NULL DEFAULT NULL,
  `RelationshipCode` CHAR(2) NULL DEFAULT NULL,
  `RequestEligibility` TINYINT(1) NOT NULL DEFAULT '0',
  `RequestEligibilityOn` DATE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `MIR` SET('FirstName', 'LastName', 'Address1', 'City', 'State', 'Zip', 'Gender', 'DateofBirth', 'InsuranceCompanyID', 'InsuranceCompany', 'InsuranceType', 'PolicyNumber', 'RelationshipCode') NOT NULL DEFAULT '',
  `Suffix` VARCHAR(4) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 77
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_customer_notes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_customer_notes` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` INT(11) NOT NULL,
  `Notes` LONGTEXT NOT NULL,
  `Active` TINYINT(1) NOT NULL DEFAULT '0',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Operator` VARCHAR(50) NULL DEFAULT NULL,
  `CallbackDate` DATETIME NULL DEFAULT NULL,
  `CreatedBy` SMALLINT(6) NULL DEFAULT NULL,
  `CreatedAt` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_customerclass`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_customerclass` (
  `Code` CHAR(2) NOT NULL DEFAULT '',
  `Description` VARCHAR(50) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_customertype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_customertype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 35
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_denial`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_denial` (
  `Code` VARCHAR(6) NOT NULL,
  `Description` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_order`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_order` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `Approved` TINYINT(1) NOT NULL DEFAULT '0',
  `RetailSales` TINYINT(1) NOT NULL DEFAULT '0',
  `OrderDate` DATE NULL DEFAULT NULL,
  `DeliveryDate` DATE NULL DEFAULT NULL,
  `BillDate` DATE NULL DEFAULT NULL,
  `EndDate` DATE NULL DEFAULT NULL,
  `ShippingMethodID` INT(11) NULL DEFAULT NULL,
  `SpecialInstructions` TEXT NULL DEFAULT NULL,
  `TicketMesage` VARCHAR(50) NULL DEFAULT NULL,
  `CustomerInsurance1_ID` INT(11) NULL DEFAULT NULL,
  `CustomerInsurance2_ID` INT(11) NULL DEFAULT NULL,
  `CustomerInsurance3_ID` INT(11) NULL DEFAULT NULL,
  `CustomerInsurance4_ID` INT(11) NULL DEFAULT NULL,
  `ICD9_1` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_2` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_3` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_4` VARCHAR(6) NULL DEFAULT NULL,
  `DoctorID` INT(11) NULL DEFAULT NULL,
  `POSTypeID` INT(11) NULL DEFAULT NULL,
  `TakenBy` VARCHAR(50) NULL DEFAULT '',
  `Discount` DOUBLE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `SaleType` ENUM('Retail', 'Back Office') NOT NULL DEFAULT 'Back Office',
  `State` ENUM('New', 'Approved', 'Closed', 'Canceled') NOT NULL DEFAULT 'New',
  `MIR` SET('BillDate', 'CustomerID', 'DeliveryDate', 'Customer.Inactive', 'Customer.MIR', 'Policy1.Required', 'Policy1.MIR', 'Policy2.Required', 'Policy2.MIR', 'Facility.MIR', 'PosType.Required', 'ICD9.Required', 'ICD9.1.Unknown', 'ICD9.1.Inactive', 'ICD9.2.Unknown', 'ICD9.2.Inactive', 'ICD9.3.Unknown', 'ICD9.3.Inactive', 'ICD9.4.Unknown', 'ICD9.4.Inactive', 'ICD10.Required', 'ICD10.01.Unknown', 'ICD10.01.Inactive', 'ICD10.02.Unknown', 'ICD10.02.Inactive', 'ICD10.03.Unknown', 'ICD10.03.Inactive', 'ICD10.04.Unknown', 'ICD10.04.Inactive', 'ICD10.05.Unknown', 'ICD10.05.Inactive', 'ICD10.06.Unknown', 'ICD10.06.Inactive', 'ICD10.07.Unknown', 'ICD10.07.Inactive', 'ICD10.08.Unknown', 'ICD10.08.Inactive', 'ICD10.09.Unknown', 'ICD10.09.Inactive', 'ICD10.10.Unknown', 'ICD10.10.Inactive', 'ICD10.11.Unknown', 'ICD10.11.Inactive', 'ICD10.12.Unknown', 'ICD10.12.Inactive') NOT NULL DEFAULT '',
  `AcceptAssignment` TINYINT(1) NOT NULL DEFAULT '0',
  `ClaimNote` VARCHAR(80) NULL DEFAULT NULL,
  `FacilityID` INT(11) NULL DEFAULT NULL,
  `ReferralID` INT(11) NULL DEFAULT NULL,
  `SalesrepID` INT(11) NULL DEFAULT NULL,
  `LocationID` INT(11) NULL DEFAULT NULL,
  `Archived` TINYINT(1) NOT NULL DEFAULT '0',
  `TakenAt` DATETIME NULL DEFAULT NULL,
  `ICD10_01` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_02` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_03` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_04` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_05` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_06` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_07` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_08` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_09` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_10` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_11` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_12` VARCHAR(8) NULL DEFAULT NULL,
  `UserField1` VARCHAR(100) NOT NULL DEFAULT '',
  `UserField2` VARCHAR(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  INDEX `IDX_CUSTOMERID_ID` (`CustomerID` ASC, `ID` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 358
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_deposits`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_deposits` (
  `CustomerID` INT(11) NOT NULL,
  `OrderID` INT(11) NOT NULL,
  `Amount` DECIMAL(18,2) NOT NULL,
  `Date` DATE NOT NULL,
  `PaymentMethod` ENUM('Cash', 'Check', 'Credit Card') NOT NULL,
  `Notes` TEXT NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NOT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`CustomerID`, `OrderID`),
  CONSTRAINT `FK_DEPOSITS_ORDER`
    FOREIGN KEY (`CustomerID` , `OrderID`)
    REFERENCES `c01`.`tbl_order` (`CustomerID` , `ID`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_orderdetails`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_orderdetails` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `OrderID` INT(11) NOT NULL DEFAULT '0',
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `SerialNumber` VARCHAR(50) NULL DEFAULT NULL,
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0',
  `PriceCodeID` INT(11) NOT NULL DEFAULT '0',
  `SaleRentType` ENUM('Medicare Oxygen Rental', 'One Time Rental', 'Monthly Rental', 'Capped Rental', 'Parental Capped Rental', 'Rent to Purchase', 'One Time Sale', 'Re-occurring Sale') NOT NULL DEFAULT 'Monthly Rental',
  `SerialID` INT(11) NULL DEFAULT NULL,
  `BillablePrice` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `AllowablePrice` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Taxable` TINYINT(1) NOT NULL DEFAULT '0',
  `FlatRate` TINYINT(1) NOT NULL DEFAULT '0',
  `DOSFrom` DATE NOT NULL DEFAULT '0000-00-00',
  `DOSTo` DATE NULL DEFAULT NULL,
  `PickupDate` DATE NULL DEFAULT NULL,
  `ShowSpanDates` TINYINT(1) NOT NULL DEFAULT '0',
  `OrderedQuantity` DOUBLE NOT NULL DEFAULT '0',
  `OrderedUnits` VARCHAR(50) NULL DEFAULT NULL,
  `OrderedWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Semi-Annually', 'Annually') NOT NULL DEFAULT 'One time',
  `OrderedConverter` DOUBLE NOT NULL DEFAULT '1',
  `BilledQuantity` DOUBLE NOT NULL DEFAULT '0',
  `BilledUnits` VARCHAR(50) NULL DEFAULT NULL,
  `BilledWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Calendar Monthly', 'Quarterly', 'Semi-Annually', 'Annually', 'Custom') NOT NULL DEFAULT 'One time',
  `BilledConverter` DOUBLE NOT NULL DEFAULT '1',
  `DeliveryQuantity` DOUBLE NOT NULL DEFAULT '0',
  `DeliveryUnits` VARCHAR(50) NULL DEFAULT NULL,
  `DeliveryConverter` DOUBLE NOT NULL DEFAULT '1',
  `BillingCode` VARCHAR(50) NULL DEFAULT NULL,
  `Modifier1` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier2` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier3` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier4` VARCHAR(8) NOT NULL DEFAULT '',
  `DXPointer` VARCHAR(50) NULL DEFAULT NULL,
  `BillingMonth` INT(11) NOT NULL DEFAULT '1',
  `BillItemOn` ENUM('Day of Delivery', 'Last day of the Month', 'Last day of the Period', 'Day of Pick-up') NOT NULL DEFAULT 'Day of Delivery',
  `AuthorizationNumber` VARCHAR(50) NULL DEFAULT NULL,
  `AuthorizationTypeID` INT(11) NULL DEFAULT NULL,
  `ReasonForPickup` VARCHAR(50) NULL DEFAULT NULL,
  `SendCMN_RX_w_invoice` TINYINT(1) NOT NULL DEFAULT '0',
  `MedicallyUnnecessary` TINYINT(1) NOT NULL DEFAULT '0',
  `Sale` TINYINT(1) NOT NULL DEFAULT '0',
  `SpecialCode` VARCHAR(50) NULL DEFAULT NULL,
  `ReviewCode` VARCHAR(50) NULL DEFAULT NULL,
  `NextOrderID` INT(11) NULL DEFAULT NULL,
  `ReoccuringID` INT(11) NULL DEFAULT NULL,
  `CMNFormID` INT(11) NULL DEFAULT NULL,
  `HAOCode` VARCHAR(10) NULL DEFAULT NULL,
  `State` ENUM('New', 'Approved', 'Pickup', 'Closed', 'Canceled') NOT NULL DEFAULT 'New',
  `BillIns1` TINYINT(1) NOT NULL DEFAULT '1',
  `BillIns2` TINYINT(1) NOT NULL DEFAULT '1',
  `BillIns3` TINYINT(1) NOT NULL DEFAULT '1',
  `BillIns4` TINYINT(1) NOT NULL DEFAULT '1',
  `EndDate` DATE NULL DEFAULT NULL,
  `MIR` SET('InventoryItemID', 'PriceCodeID', 'SaleRentType', 'OrderedQuantity', 'OrderedUnits', 'OrderedWhen', 'OrderedConverter', 'BilledQuantity', 'BilledUnits', 'BilledWhen', 'BilledConverter', 'DeliveryQuantity', 'DeliveryUnits', 'DeliveryConverter', 'BillingCode', 'BillItemOn', 'DXPointer9', 'DXPointer10', 'Modifier1', 'Modifier2', 'Modifier3', 'CMNForm.Required', 'CMNForm.RecertificationDate', 'CMNForm.FormExpired', 'CMNForm.MIR', 'EndDate.Invalid', 'EndDate.Unconfirmed', 'AuthorizationNumber.Expired', 'AuthorizationNumber.Expires') NOT NULL DEFAULT '',
  `NextBillingDate` DATE NULL DEFAULT NULL,
  `WarehouseID` INT(11) NOT NULL,
  `AcceptAssignment` TINYINT(1) NOT NULL DEFAULT '0',
  `DrugNoteField` VARCHAR(20) NULL DEFAULT NULL,
  `DrugControlNumber` VARCHAR(50) NULL DEFAULT NULL,
  `NopayIns1` TINYINT(1) NOT NULL DEFAULT '0',
  `PointerICD10` SMALLINT(6) NOT NULL DEFAULT '0',
  `DXPointer10` VARCHAR(50) NULL DEFAULT NULL,
  `MIR.ORDER` SET('Customer.Inactive', 'Customer.MIR', 'Policy1.Required', 'Policy1.MIR', 'Policy2.Required', 'Policy2.MIR', 'Facility.MIR', 'PosType.Required', 'ICD9.Required', 'ICD9.1.Unknown', 'ICD9.1.Inactive', 'ICD9.2.Unknown', 'ICD9.2.Inactive', 'ICD9.3.Unknown', 'ICD9.3.Inactive', 'ICD9.4.Unknown', 'ICD9.4.Inactive', 'ICD10.Required', 'ICD10.01.Unknown', 'ICD10.01.Inactive', 'ICD10.02.Unknown', 'ICD10.02.Inactive', 'ICD10.03.Unknown', 'ICD10.03.Inactive', 'ICD10.04.Unknown', 'ICD10.04.Inactive', 'ICD10.05.Unknown', 'ICD10.05.Inactive', 'ICD10.06.Unknown', 'ICD10.06.Inactive', 'ICD10.07.Unknown', 'ICD10.07.Inactive', 'ICD10.08.Unknown', 'ICD10.08.Inactive', 'ICD10.09.Unknown', 'ICD10.09.Inactive', 'ICD10.10.Unknown', 'ICD10.10.Inactive', 'ICD10.11.Unknown', 'ICD10.11.Inactive', 'ICD10.12.Unknown', 'ICD10.12.Inactive') NOT NULL DEFAULT '',
  `HaoDescription` VARCHAR(100) NULL DEFAULT NULL,
  `UserField1` VARCHAR(100) NOT NULL DEFAULT '',
  `UserField2` VARCHAR(100) NOT NULL DEFAULT '',
  `AuthorizationExpirationDate` DATE NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `IDX_CUSTOMERID_ORDERID_ID` (`CustomerID` ASC, `OrderID` ASC, `ID` ASC) VISIBLE,
  INDEX `IDX_CUSTOMERID_ORDERID_ID_INVENTORYITEMID` (`CustomerID` ASC, `OrderID` ASC, `ID` ASC, `InventoryItemID` ASC) VISIBLE,
  INDEX `IDX_CUSTOMERID_NEXTORDERID` (`CustomerID` ASC, `NextOrderID` ASC) VISIBLE,
  INDEX `IDX_InventoryItemID_SerialNumber` (`InventoryItemID` ASC, `SerialNumber` ASC) VISIBLE,
  CONSTRAINT `FK_NEXTORDER`
    FOREIGN KEY (`CustomerID` , `NextOrderID`)
    REFERENCES `c01`.`tbl_order` (`CustomerID` , `ID`)
    ON UPDATE CASCADE,
  CONSTRAINT `FK_ORDER`
    FOREIGN KEY (`CustomerID` , `OrderID`)
    REFERENCES `c01`.`tbl_order` (`CustomerID` , `ID`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 500
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_depositdetails`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_depositdetails` (
  `OrderDetailsID` INT(11) NOT NULL,
  `OrderID` INT(11) NOT NULL,
  `CustomerID` INT(11) NOT NULL,
  `Amount` DECIMAL(18,2) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NOT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`OrderDetailsID`),
  INDEX `IDX_DEPOSITS` (`CustomerID` ASC, `OrderID` ASC, `OrderDetailsID` ASC) VISIBLE,
  CONSTRAINT `FK_DEPOSITDETAILS_DEPOSITS`
    FOREIGN KEY (`CustomerID` , `OrderID`)
    REFERENCES `c01`.`tbl_deposits` (`CustomerID` , `OrderID`)
    ON UPDATE CASCADE,
  CONSTRAINT `FK_DEPOSITDETAILS_ORDERDETAILS`
    FOREIGN KEY (`OrderDetailsID`)
    REFERENCES `c01`.`tbl_orderdetails` (`ID`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_eligibilityrequest`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_eligibilityrequest` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `CustomerInsuranceID` INT(11) NOT NULL DEFAULT '0',
  `Region` ENUM('Region A', 'Region B', 'Region C', 'Region D', 'Zirmed', 'Medi-Cal', 'Availity', 'Office Ally', 'Ability') NOT NULL DEFAULT 'Region A',
  `RequestBatchID` INT(11) NULL DEFAULT NULL,
  `RequestTime` DATETIME NOT NULL DEFAULT '1900-01-01 00:00:00',
  `RequestText` MEDIUMTEXT NOT NULL,
  `ResponseBatchID` INT(11) NULL DEFAULT NULL,
  `ResponseTime` DATETIME NULL DEFAULT NULL,
  `ResponseText` MEDIUMTEXT NULL DEFAULT NULL,
  `SubmissionTime` DATETIME NULL DEFAULT NULL,
  `SubmissionText` MEDIUMTEXT NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 10
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_facility`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_facility` (
  `Address1` VARCHAR(40) NOT NULL,
  `Address2` VARCHAR(40) NOT NULL,
  `City` VARCHAR(25) NOT NULL,
  `Contact` VARCHAR(50) NOT NULL,
  `DefaultDeliveryWeek` ENUM('1st week of month', '2nd week of month', '3rd week of month', '4th week of month', 'as needed') NOT NULL,
  `Directions` LONGTEXT NULL DEFAULT NULL,
  `Fax` VARCHAR(50) NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `MedicaidID` VARCHAR(50) NOT NULL,
  `MedicareID` VARCHAR(50) NOT NULL,
  `Name` VARCHAR(50) NOT NULL,
  `Phone` VARCHAR(50) NOT NULL,
  `Phone2` VARCHAR(50) NOT NULL,
  `POSTypeID` INT(11) NULL DEFAULT '12',
  `State` VARCHAR(2) NOT NULL,
  `Zip` VARCHAR(10) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `NPI` VARCHAR(10) NULL DEFAULT NULL,
  `MIR` SET('Name', 'Address1', 'City', 'State', 'Zip', 'POSTypeID', 'NPI') NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 27
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_hao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_hao` (
  `Code` VARCHAR(10) NOT NULL,
  `Description` LONGTEXT NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_image`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_image` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Type` VARCHAR(50) NOT NULL DEFAULT '',
  `Description` TEXT NULL DEFAULT NULL,
  `CustomerID` INT(11) NULL DEFAULT NULL,
  `OrderID` INT(11) NULL DEFAULT NULL,
  `InvoiceID` INT(11) NULL DEFAULT NULL,
  `DoctorID` INT(11) NULL DEFAULT NULL,
  `CMNFormID` INT(11) NULL DEFAULT NULL,
  `Thumbnail` BLOB NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 22
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_insurancetype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_insurancetype` (
  `Code` VARCHAR(2) NOT NULL,
  `Description` VARCHAR(40) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_inventory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_inventory` (
  `WarehouseID` INT(11) NOT NULL DEFAULT '0',
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0',
  `OnHand` DOUBLE NOT NULL DEFAULT '0',
  `Committed` DOUBLE NOT NULL DEFAULT '0',
  `OnOrder` DOUBLE NOT NULL DEFAULT '0',
  `UnAvailable` DOUBLE NOT NULL DEFAULT '0',
  `Rented` DOUBLE NOT NULL DEFAULT '0',
  `Sold` DOUBLE NOT NULL DEFAULT '0',
  `BackOrdered` DOUBLE NOT NULL DEFAULT '0',
  `ReOrderPoint` DOUBLE NOT NULL DEFAULT '0',
  `CostPerUnit` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `TotalCost` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`WarehouseID`, `InventoryItemID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_inventory_transaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_inventory_transaction` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0',
  `WarehouseID` INT(11) NOT NULL DEFAULT '0',
  `TypeID` INT(11) NOT NULL DEFAULT '0',
  `Date` DATE NOT NULL DEFAULT '0000-00-00',
  `Quantity` DOUBLE NULL DEFAULT NULL,
  `Cost` DECIMAL(18,2) NULL DEFAULT NULL,
  `Description` VARCHAR(30) NULL DEFAULT NULL,
  `SerialID` INT(11) NULL DEFAULT NULL,
  `VendorID` INT(11) NULL DEFAULT NULL,
  `CustomerID` INT(11) NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `PurchaseOrderID` INT(11) NULL DEFAULT NULL,
  `PurchaseOrderDetailsID` INT(11) NULL DEFAULT NULL,
  `InvoiceID` INT(11) NULL DEFAULT NULL,
  `ManufacturerID` INT(11) NULL DEFAULT NULL,
  `OrderDetailsID` INT(11) NULL DEFAULT NULL,
  `OrderID` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `idx_typeid_custid_orid_ordetailsid_itemid_warehouseid` (`TypeID` ASC, `CustomerID` ASC, `OrderID` ASC, `OrderDetailsID` ASC, `InventoryItemID` ASC, `WarehouseID` ASC) VISIBLE,
  INDEX `idx_typeid_itemid_warehouseid` (`TypeID` ASC, `InventoryItemID` ASC, `WarehouseID` ASC) VISIBLE,
  INDEX `idx_typeid_poid_podetailsid_itemid_warehouseid` (`TypeID` ASC, `PurchaseOrderID` ASC, `PurchaseOrderDetailsID` ASC, `InventoryItemID` ASC, `WarehouseID` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 497
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_inventory_transaction_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_inventory_transaction_type` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `OnHand` INT(11) NOT NULL DEFAULT '0',
  `Committed` INT(11) NOT NULL DEFAULT '0',
  `OnOrder` INT(11) NOT NULL DEFAULT '0',
  `UnAvailable` INT(11) NOT NULL DEFAULT '0',
  `Rented` INT(11) NOT NULL DEFAULT '0',
  `Sold` INT(11) NOT NULL DEFAULT '0',
  `BackOrdered` INT(11) NOT NULL DEFAULT '0',
  `AdjTotalCost` INT(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 28
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_inventoryitem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_inventoryitem` (
  `Barcode` VARCHAR(50) NOT NULL DEFAULT '',
  `BarcodeType` VARCHAR(50) NOT NULL DEFAULT '',
  `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill',
  `CommissionPaidAt` ENUM('Billing', 'Payment', 'Never') NOT NULL DEFAULT 'Billing',
  `VendorID` INT(11) NULL DEFAULT NULL,
  `FlatRate` TINYINT(1) NOT NULL DEFAULT '0',
  `FlatRateAmount` DOUBLE NULL DEFAULT NULL,
  `Frequency` ENUM('One time', 'Monthly', 'Weekly', 'Never') NOT NULL DEFAULT 'One time',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InventoryCode` VARCHAR(50) NOT NULL DEFAULT '',
  `ModelNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `Name` VARCHAR(100) NOT NULL DEFAULT '',
  `O2Tank` TINYINT(1) NOT NULL DEFAULT '0',
  `Percentage` TINYINT(1) NOT NULL DEFAULT '0',
  `PercentageAmount` DOUBLE NOT NULL DEFAULT '0',
  `PredefinedTextID` INT(11) NULL DEFAULT NULL,
  `ProductTypeID` INT(11) NULL DEFAULT NULL,
  `Serialized` TINYINT(1) NOT NULL DEFAULT '0',
  `Service` TINYINT(1) NOT NULL DEFAULT '0',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Inactive` TINYINT(1) NOT NULL DEFAULT '0',
  `ManufacturerID` INT(11) NULL DEFAULT NULL,
  `PurchasePrice` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `UserField1` VARCHAR(100) NOT NULL DEFAULT '',
  `UserField2` VARCHAR(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 1938
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_invoice`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_invoice` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `OrderID` INT(11) NULL DEFAULT NULL,
  `Approved` TINYINT(1) NOT NULL DEFAULT '0',
  `InvoiceDate` DATE NULL DEFAULT NULL,
  `InvoiceBalance` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `SubmittedTo` ENUM('Ins1', 'Ins2', 'Ins3', 'Ins4', 'Patient') NOT NULL DEFAULT 'Ins1',
  `SubmittedBy` VARCHAR(50) NULL DEFAULT NULL,
  `SubmittedDate` DATE NULL DEFAULT NULL,
  `SubmittedBatch` VARCHAR(50) NULL DEFAULT NULL,
  `CustomerInsurance1_ID` INT(11) NULL DEFAULT NULL,
  `CustomerInsurance2_ID` INT(11) NULL DEFAULT NULL,
  `CustomerInsurance3_ID` INT(11) NULL DEFAULT NULL,
  `CustomerInsurance4_ID` INT(11) NULL DEFAULT NULL,
  `ICD9_1` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_2` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_3` VARCHAR(6) NULL DEFAULT NULL,
  `ICD9_4` VARCHAR(6) NULL DEFAULT NULL,
  `DoctorID` INT(11) NULL DEFAULT NULL,
  `POSTypeID` INT(11) NULL DEFAULT NULL,
  `TaxRateID` INT(11) NULL DEFAULT NULL,
  `TaxRatePercent` DOUBLE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Discount` DOUBLE NULL DEFAULT '0',
  `AcceptAssignment` TINYINT(1) NOT NULL DEFAULT '0',
  `ClaimNote` VARCHAR(80) NULL DEFAULT NULL,
  `FacilityID` INT(11) NULL DEFAULT NULL,
  `ReferralID` INT(11) NULL DEFAULT NULL,
  `SalesrepID` INT(11) NULL DEFAULT NULL,
  `Archived` TINYINT(1) NOT NULL DEFAULT '0',
  `ICD10_01` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_02` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_03` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_04` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_05` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_06` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_07` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_08` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_09` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_10` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_11` VARCHAR(8) NULL DEFAULT NULL,
  `ICD10_12` VARCHAR(8) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `IDX_CUSTOMERID_ID` (`CustomerID` ASC, `ID` ASC) VISIBLE,
  INDEX `IDX_CUSTOMERID_ORDERID` (`CustomerID` ASC, `OrderID` ASC) VISIBLE,
  CONSTRAINT `FK_ORDER_2`
    FOREIGN KEY (`CustomerID` , `OrderID`)
    REFERENCES `c01`.`tbl_order` (`CustomerID` , `ID`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 331
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_invoicedetails`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_invoicedetails` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InvoiceID` INT(11) NOT NULL DEFAULT '0',
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0',
  `PriceCodeID` INT(11) NOT NULL DEFAULT '0',
  `OrderID` INT(11) NULL DEFAULT NULL,
  `OrderDetailsID` INT(11) NULL DEFAULT NULL,
  `Balance` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `BillableAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `AllowableAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Taxes` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Quantity` DOUBLE NOT NULL DEFAULT '0',
  `InvoiceDate` DATE NULL DEFAULT NULL,
  `DOSFrom` DATE NOT NULL DEFAULT '0000-00-00',
  `DOSTo` DATE NULL DEFAULT NULL,
  `BillingCode` VARCHAR(50) NULL DEFAULT NULL,
  `Modifier1` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier2` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier3` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier4` VARCHAR(8) NOT NULL DEFAULT '',
  `DXPointer` VARCHAR(50) NULL DEFAULT NULL,
  `BillingMonth` INT(11) NOT NULL DEFAULT '0',
  `SendCMN_RX_w_invoice` TINYINT(1) NOT NULL DEFAULT '0',
  `SpecialCode` VARCHAR(50) NULL DEFAULT NULL,
  `ReviewCode` VARCHAR(50) NULL DEFAULT NULL,
  `MedicallyUnnecessary` TINYINT(1) NOT NULL DEFAULT '0',
  `AuthorizationNumber` VARCHAR(50) NULL DEFAULT NULL,
  `AuthorizationTypeID` INT(11) NULL DEFAULT NULL,
  `InvoiceNotes` VARCHAR(255) NULL DEFAULT NULL,
  `InvoiceRecord` VARCHAR(255) NULL DEFAULT NULL,
  `CMNFormID` INT(11) NULL DEFAULT NULL,
  `HAOCode` VARCHAR(10) NULL DEFAULT NULL,
  `BillIns1` TINYINT(1) NOT NULL DEFAULT '1',
  `BillIns2` TINYINT(1) NOT NULL DEFAULT '1',
  `BillIns3` TINYINT(1) NOT NULL DEFAULT '1',
  `BillIns4` TINYINT(1) NOT NULL DEFAULT '1',
  `Hardship` TINYINT(1) NOT NULL DEFAULT '0',
  `ShowSpanDates` TINYINT(1) NOT NULL DEFAULT '0',
  `PaymentAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `WriteoffAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `CurrentPayer` ENUM('Ins1', 'Ins2', 'Ins3', 'Ins4', 'Patient', 'None') NOT NULL DEFAULT 'Ins1',
  `Pendings` TINYINT(4) NOT NULL DEFAULT '0',
  `Submits` TINYINT(4) NOT NULL DEFAULT '0',
  `Payments` TINYINT(4) NOT NULL DEFAULT '0',
  `SubmittedDate` DATE NULL DEFAULT NULL,
  `Submitted` TINYINT(1) NOT NULL DEFAULT '0',
  `CurrentInsuranceCompanyID` INT(11) NULL DEFAULT NULL,
  `CurrentCustomerInsuranceID` INT(11) NULL DEFAULT NULL,
  `AcceptAssignment` TINYINT(1) NOT NULL DEFAULT '0',
  `DeductibleAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `DrugNoteField` VARCHAR(20) NULL DEFAULT NULL,
  `DrugControlNumber` VARCHAR(50) NULL DEFAULT NULL,
  `NopayIns1` TINYINT(1) NOT NULL DEFAULT '0',
  `PointerICD10` SMALLINT(6) NOT NULL DEFAULT '0',
  `DXPointer10` VARCHAR(50) NULL DEFAULT NULL,
  `HaoDescription` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `IDX_CUSTOMERID_INVOICEID_ID` (`CustomerID` ASC, `InvoiceID` ASC, `ID` ASC) VISIBLE,
  CONSTRAINT `FK_INVOICE`
    FOREIGN KEY (`CustomerID` , `InvoiceID`)
    REFERENCES `c01`.`tbl_invoice` (`CustomerID` , `ID`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 384
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_invoice_transaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_invoice_transaction` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InvoiceDetailsID` INT(11) NOT NULL DEFAULT '0',
  `InvoiceID` INT(11) NOT NULL DEFAULT '0',
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `InsuranceCompanyID` INT(11) NULL DEFAULT NULL,
  `CustomerInsuranceID` INT(11) NULL DEFAULT NULL,
  `TransactionTypeID` INT(11) NOT NULL DEFAULT '0',
  `TransactionDate` DATE NULL DEFAULT NULL,
  `Amount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Quantity` DOUBLE NOT NULL DEFAULT '0',
  `Taxes` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `BatchNumber` VARCHAR(20) NOT NULL DEFAULT '',
  `Comments` TEXT NULL DEFAULT NULL,
  `Extra` TEXT NULL DEFAULT NULL,
  `Approved` TINYINT(1) NOT NULL DEFAULT '0',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Deductible` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`ID`),
  INDEX `IDX_CUSTOMERID_INVOICEID_INVOICEDETAILSID` (`CustomerID` ASC, `InvoiceID` ASC, `InvoiceDetailsID` ASC) VISIBLE,
  CONSTRAINT `FK_INVOICE_TRANSACTION_INVOICE`
    FOREIGN KEY (`CustomerID` , `InvoiceID` , `InvoiceDetailsID`)
    REFERENCES `c01`.`tbl_invoicedetails` (`CustomerID` , `InvoiceID` , `ID`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 617
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_invoice_transactiontype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_invoice_transactiontype` (
  `ID` INT(11) NOT NULL DEFAULT '0',
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Balance` INT(11) NOT NULL DEFAULT '0',
  `Allowable` INT(11) NOT NULL DEFAULT '0',
  `Amount` INT(11) NOT NULL DEFAULT '0',
  `Taxes` INT(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `IX_invoice_transactiontype_name` (`Name` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_invoiceform`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_invoiceform` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `ReportFileName` VARCHAR(50) NOT NULL,
  `MarginTop` DOUBLE NOT NULL DEFAULT '0.25',
  `MarginLeft` DOUBLE NOT NULL DEFAULT '0.19',
  `MarginBottom` DOUBLE NOT NULL DEFAULT '0.18',
  `MarginRight` DOUBLE NOT NULL DEFAULT '0.22',
  `SpecialCoding` VARCHAR(20) NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 37
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_invoicenotes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_invoicenotes` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InvoiceDetailsID` INT(11) NOT NULL DEFAULT '0',
  `InvoiceID` INT(11) NOT NULL DEFAULT '0',
  `CustomerID` INT(11) NOT NULL DEFAULT '0',
  `CallbackDate` DATE NULL DEFAULT NULL,
  `Done` TINYINT(1) NOT NULL DEFAULT '0',
  `Notes` LONGTEXT NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_kit`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_kit` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_kitdetails`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_kitdetails` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `KitID` INT(11) NOT NULL,
  `WarehouseID` INT(11) NOT NULL,
  `InventoryItemID` INT(11) NOT NULL,
  `PriceCodeID` INT(11) NULL DEFAULT NULL,
  `Quantity` INT(11) NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 16
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_legalrep`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_legalrep` (
  `Address1` VARCHAR(40) NOT NULL,
  `Address2` VARCHAR(40) NOT NULL,
  `City` VARCHAR(25) NOT NULL,
  `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL,
  `FirstName` VARCHAR(25) NOT NULL,
  `OfficePhone` VARCHAR(50) NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `LastName` VARCHAR(30) NOT NULL,
  `MiddleName` VARCHAR(1) NOT NULL,
  `Mobile` VARCHAR(50) NOT NULL,
  `Pager` VARCHAR(50) NOT NULL,
  `State` VARCHAR(2) NOT NULL,
  `Suffix` VARCHAR(4) NOT NULL,
  `Zip` VARCHAR(10) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `FirmName` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_location`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_location` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Contact` VARCHAR(50) NOT NULL DEFAULT '',
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Code` VARCHAR(40) NOT NULL DEFAULT '',
  `City` VARCHAR(25) NOT NULL DEFAULT '',
  `Address1` VARCHAR(40) NOT NULL DEFAULT '',
  `Address2` VARCHAR(40) NOT NULL DEFAULT '',
  `State` CHAR(2) NOT NULL DEFAULT '',
  `Zip` VARCHAR(10) NOT NULL DEFAULT '',
  `Fax` VARCHAR(50) NOT NULL DEFAULT '',
  `FEDTaxID` VARCHAR(50) NOT NULL DEFAULT '',
  `TaxIDType` ENUM('SSN', 'EIN') NOT NULL DEFAULT 'SSN',
  `Phone` VARCHAR(50) NOT NULL DEFAULT '',
  `Phone2` VARCHAR(50) NOT NULL DEFAULT '',
  `PrintInfoOnDelPupTicket` TINYINT(1) NULL DEFAULT NULL,
  `PrintInfoOnInvoiceAcctStatements` TINYINT(1) NULL DEFAULT NULL,
  `PrintInfoOnPartProvider` TINYINT(1) NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `NPI` VARCHAR(10) NULL DEFAULT NULL,
  `InvoiceFormID` INT(11) NULL DEFAULT NULL,
  `PriceCodeID` INT(11) NULL DEFAULT NULL,
  `ParticipatingProvider` TINYINT(1) NULL DEFAULT NULL,
  `Email` VARCHAR(50) NULL DEFAULT NULL,
  `WarehouseID` INT(11) NULL DEFAULT NULL,
  `POSTypeID` INT(11) NULL DEFAULT '12',
  `TaxRateID` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_manufacturer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_manufacturer` (
  `AccountNumber` VARCHAR(40) NOT NULL,
  `Address1` VARCHAR(40) NOT NULL,
  `Address2` VARCHAR(40) NOT NULL,
  `City` VARCHAR(25) NOT NULL,
  `Contact` VARCHAR(50) NOT NULL,
  `Fax` VARCHAR(50) NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `Phone` VARCHAR(50) NOT NULL,
  `Phone2` VARCHAR(50) NOT NULL,
  `State` VARCHAR(2) NOT NULL,
  `Zip` VARCHAR(10) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_medicalconditions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_medicalconditions` (
  `Code` VARCHAR(6) NOT NULL,
  `Description` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_object`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_object` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Description` VARCHAR(50) NOT NULL,
  `Name` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 91
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_order_survey`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_order_survey` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `SurveyID` INT(11) NOT NULL,
  `OrderID` INT(11) NOT NULL,
  `Form` TEXT NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `OrderID` (`OrderID` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_orderdeposits`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_orderdeposits` (
  `OrderDetailsID` INT(11) NOT NULL,
  `OrderID` INT(11) NOT NULL,
  `CustomerID` INT(11) NOT NULL,
  `Amount` DECIMAL(18,2) NOT NULL,
  `Date` DATE NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NOT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`OrderDetailsID`),
  INDEX `IDX_ORDERDEPOSITS` (`CustomerID` ASC, `OrderID` ASC, `OrderDetailsID` ASC) VISIBLE,
  CONSTRAINT `FK_ORDERDEPOSITS_ORDER`
    FOREIGN KEY (`CustomerID` , `OrderID`)
    REFERENCES `c01`.`tbl_order` (`CustomerID` , `ID`)
    ON UPDATE CASCADE,
  CONSTRAINT `FK_ORDERDEPOSITS_ORDERDETAILS`
    FOREIGN KEY (`OrderDetailsID`)
    REFERENCES `c01`.`tbl_orderdetails` (`ID`)
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_payer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_payer` (
  `InsuranceCompanyID` INT(11) NOT NULL,
  `ParticipatingProvider` TINYINT(1) NOT NULL DEFAULT '0',
  `LastUpdateUserID` SMALLINT(6) NOT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ExtractOrderingPhysician` TINYINT(1) NOT NULL DEFAULT '1',
  `ExtractReferringPhysician` TINYINT(1) NOT NULL DEFAULT '0',
  `ExtractRenderingProvider` TINYINT(1) NOT NULL DEFAULT '0',
  `TaxonomyCodePrefix` VARCHAR(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`InsuranceCompanyID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_paymentplan`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_paymentplan` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` INT(11) NOT NULL,
  `Period` ENUM('Weekly', 'Bi-weekly', 'Monthly') NOT NULL DEFAULT 'Weekly',
  `FirstPayment` DATE NOT NULL DEFAULT '1900-01-01',
  `PaymentCount` INT(11) NOT NULL,
  `PaymentAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Details` MEDIUMTEXT NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_paymentplan_payments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_paymentplan_payments` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `PaymentPlanID` INT(11) NOT NULL,
  `CustomerID` INT(11) NOT NULL,
  `Index` INT(11) NOT NULL,
  `DueDate` DATE NOT NULL DEFAULT '1900-01-01',
  `DueAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `PaymentDate` DATE NULL DEFAULT NULL,
  `PaymentAmount` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Details` MEDIUMTEXT NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 10
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_permissions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_permissions` (
  `UserID` SMALLINT(6) NOT NULL,
  `ObjectID` SMALLINT(6) NOT NULL,
  `ADD_EDIT` TINYINT(1) NOT NULL DEFAULT '0',
  `DELETE` TINYINT(1) NOT NULL DEFAULT '0',
  `PROCESS` TINYINT(1) NOT NULL DEFAULT '0',
  `VIEW` TINYINT(1) NOT NULL DEFAULT '0',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`UserID`, `ObjectID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_postype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_postype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 100
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_predefinedtext`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_predefinedtext` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Type` ENUM('Document Text', 'Account Statements', 'Compliance Notes', 'Customer Notes', 'Invoice Notes', 'HAO') NOT NULL DEFAULT 'Document Text',
  `Text` LONGTEXT NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_pricecode`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_pricecode` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_pricecode_item`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_pricecode_item` (
  `AcceptAssignment` TINYINT(1) NOT NULL DEFAULT '0',
  `OrderedQuantity` DOUBLE NOT NULL DEFAULT '0',
  `OrderedUnits` VARCHAR(50) NULL DEFAULT NULL,
  `OrderedWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Semi-Annually', 'Annually') NOT NULL DEFAULT 'One time',
  `OrderedConverter` DOUBLE NOT NULL DEFAULT '1',
  `BilledUnits` VARCHAR(50) NULL DEFAULT NULL,
  `BilledWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Calendar Monthly', 'Quarterly', 'Semi-Annually', 'Annually', 'Custom') NOT NULL DEFAULT 'One time',
  `BilledConverter` DOUBLE NOT NULL DEFAULT '1',
  `DeliveryUnits` VARCHAR(50) NULL DEFAULT NULL,
  `DeliveryConverter` DOUBLE NOT NULL DEFAULT '1',
  `BillingCode` VARCHAR(50) NULL DEFAULT NULL,
  `BillItemOn` ENUM('Day of Delivery', 'Last day of the Month', 'Last day of the Period', 'Day of Pick-up') NOT NULL DEFAULT 'Day of Delivery',
  `DefaultCMNType` ENUM('DMERC 02.03A', 'DMERC 02.03B', 'DMERC 03.02', 'DMERC 07.02B', 'DMERC 08.02', 'DMERC DRORDER', 'DMERC URO', 'DME 04.04B', 'DME 04.04C', 'DME 06.03B', 'DME 07.03A', 'DME 09.03', 'DME 10.03', 'DME 484.03') NOT NULL DEFAULT 'DME 484.03',
  `DefaultOrderType` ENUM('Sale', 'Rental') NOT NULL DEFAULT 'Sale',
  `AuthorizationTypeID` INT(11) NULL DEFAULT NULL,
  `FlatRate` TINYINT(1) NOT NULL DEFAULT '0',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0',
  `Modifier1` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier2` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier3` VARCHAR(8) NOT NULL DEFAULT '',
  `Modifier4` VARCHAR(8) NOT NULL DEFAULT '',
  `PriceCodeID` INT(11) NOT NULL DEFAULT '0',
  `PredefinedTextID` INT(11) NULL DEFAULT NULL,
  `Rent_AllowablePrice` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Rent_BillablePrice` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Sale_AllowablePrice` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Sale_BillablePrice` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `RentalType` ENUM('Medicare Oxygen Rental', 'One Time Rental', 'Monthly Rental', 'Capped Rental', 'Parental Capped Rental', 'Rent to Purchase') NOT NULL DEFAULT 'Monthly Rental',
  `ReoccuringSale` TINYINT(1) NOT NULL DEFAULT '0',
  `ShowSpanDates` TINYINT(1) NOT NULL DEFAULT '0',
  `Taxable` TINYINT(1) NOT NULL DEFAULT '0',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `BillInsurance` TINYINT(1) NOT NULL DEFAULT '1',
  `DrugNoteField` VARCHAR(20) NULL DEFAULT NULL,
  `DrugControlNumber` VARCHAR(50) NULL DEFAULT NULL,
  `UserField1` VARCHAR(100) NOT NULL DEFAULT '',
  `UserField2` VARCHAR(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `InventoryItemID` (`InventoryItemID` ASC, `PriceCodeID` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 1950
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_producttype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_producttype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 106
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_provider`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_provider` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `LocationID` INT(11) NOT NULL DEFAULT '0',
  `InsuranceCompanyID` INT(11) NOT NULL DEFAULT '0',
  `ProviderNumber` VARCHAR(25) NOT NULL DEFAULT '',
  `Password` VARCHAR(20) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ProviderNumberType` VARCHAR(6) NOT NULL DEFAULT '1C',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_providernumbertype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_providernumbertype` (
  `Code` VARCHAR(6) NOT NULL,
  `Description` VARCHAR(100) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_purchaseorder`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_purchaseorder` (
  `Approved` TINYINT(1) NOT NULL DEFAULT '0',
  `Cost` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `Freight` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Tax` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `TotalDue` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  `VendorID` INT(11) NOT NULL,
  `ShipToName` VARCHAR(50) NOT NULL,
  `ShipToAddress1` VARCHAR(40) NOT NULL,
  `ShipToAddress2` VARCHAR(40) NOT NULL,
  `ShipToCity` VARCHAR(25) NOT NULL,
  `ShipToState` VARCHAR(2) NOT NULL,
  `ShipToZip` VARCHAR(10) NOT NULL,
  `ShipToPhone` VARCHAR(50) NOT NULL,
  `OrderDate` DATE NULL DEFAULT NULL,
  `CompanyName` VARCHAR(50) NOT NULL,
  `CompanyAddress1` VARCHAR(40) NOT NULL,
  `CompanyAddress2` VARCHAR(40) NOT NULL,
  `CompanyCity` VARCHAR(25) NOT NULL,
  `CompanyState` VARCHAR(2) NOT NULL,
  `CompanyZip` VARCHAR(10) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ShipVia` ENUM('BEST WAY', 'UPS/RPS') NULL DEFAULT NULL,
  `FOB` VARCHAR(50) NULL DEFAULT NULL,
  `VendorSalesRep` VARCHAR(50) NULL DEFAULT NULL,
  `Terms` TEXT NULL DEFAULT NULL,
  `CompanyPhone` VARCHAR(50) NULL DEFAULT NULL,
  `TaxRateID` INT(11) NULL DEFAULT NULL,
  `Reoccuring` TINYINT(1) NOT NULL DEFAULT '0',
  `CreatedDate` DATE NULL DEFAULT NULL,
  `CreatedUserID` SMALLINT(6) NULL DEFAULT NULL,
  `SubmittedDate` DATE NULL DEFAULT NULL,
  `SubmittedUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LocationID` INT(11) NULL DEFAULT NULL,
  `Number` VARCHAR(40) NOT NULL DEFAULT '',
  `Archived` TINYINT(1) NOT NULL DEFAULT '0',
  `ConfirmationNumber` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `ix_purchaseorder_search` (`LocationID` ASC, `ID` ASC, `Number` ASC, `VendorID` ASC, `OrderDate` ASC, `SubmittedDate` ASC, `Approved` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 22
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_purchaseorderdetails`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_purchaseorderdetails` (
  `BackOrder` INT(11) NOT NULL DEFAULT '0',
  `Ordered` INT(11) NOT NULL DEFAULT '0',
  `Received` INT(11) NOT NULL DEFAULT '0',
  `Price` DOUBLE NOT NULL DEFAULT '0',
  `Customer` VARCHAR(50) NULL DEFAULT NULL,
  `DatePromised` DATE NULL DEFAULT NULL,
  `DateReceived` DATE NULL DEFAULT NULL,
  `DropShipToCustomer` TINYINT(1) NOT NULL DEFAULT '0',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `InventoryItemID` INT(11) NOT NULL,
  `PurchaseOrderID` INT(11) NULL DEFAULT NULL,
  `WarehouseID` INT(11) NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `VendorSTKNumber` VARCHAR(50) NULL DEFAULT NULL,
  `ReferenceNumber` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `ix_purchaseorderdetails_parent` (`PurchaseOrderID` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 23
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_referral`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_referral` (
  `Address1` VARCHAR(40) NOT NULL,
  `Address2` VARCHAR(40) NOT NULL,
  `City` VARCHAR(25) NOT NULL,
  `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL,
  `Employer` VARCHAR(50) NOT NULL,
  `Fax` VARCHAR(50) NOT NULL,
  `FirstName` VARCHAR(25) NOT NULL,
  `HomePhone` VARCHAR(50) NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `LastName` VARCHAR(30) NOT NULL,
  `MiddleName` VARCHAR(1) NOT NULL,
  `Mobile` VARCHAR(50) NOT NULL,
  `ReferralTypeID` INT(11) NULL DEFAULT NULL,
  `State` VARCHAR(2) NOT NULL,
  `Suffix` VARCHAR(4) NOT NULL,
  `WorkPhone` VARCHAR(50) NOT NULL,
  `Zip` VARCHAR(10) NOT NULL,
  `LastContacted` DATE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_referraltype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_referraltype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_relationship`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_relationship` (
  `Code` CHAR(2) NOT NULL DEFAULT '',
  `Description` VARCHAR(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_salesrep`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_salesrep` (
  `Address1` VARCHAR(40) NOT NULL,
  `Address2` VARCHAR(40) NOT NULL,
  `City` VARCHAR(25) NOT NULL,
  `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL,
  `FirstName` VARCHAR(25) NOT NULL,
  `HomePhone` VARCHAR(50) NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `LastName` VARCHAR(30) NOT NULL,
  `MiddleName` VARCHAR(1) NOT NULL,
  `Mobile` VARCHAR(50) NOT NULL,
  `Pager` VARCHAR(50) NOT NULL,
  `State` VARCHAR(2) NOT NULL,
  `Suffix` VARCHAR(4) NOT NULL,
  `Zip` VARCHAR(10) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_serial`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_serial` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CurrentCustomerID` INT(11) NULL DEFAULT NULL,
  `InventoryItemID` INT(11) NOT NULL DEFAULT '0',
  `LastCustomerID` INT(11) NULL DEFAULT NULL,
  `ManufacturerID` INT(11) NULL DEFAULT NULL,
  `VendorID` INT(11) NULL DEFAULT NULL,
  `WarehouseID` INT(11) NULL DEFAULT NULL,
  `LengthOfWarranty` VARCHAR(50) NOT NULL DEFAULT '',
  `LotNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `MaintenanceRecord` LONGTEXT NOT NULL,
  `ManufaturerSerialNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `ModelNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `MonthsRented` VARCHAR(50) NOT NULL DEFAULT '',
  `NextMaintenanceDate` DATE NULL DEFAULT NULL,
  `PurchaseOrderID` INT(11) NULL DEFAULT NULL,
  `PurchaseAmount` DOUBLE NOT NULL DEFAULT '0',
  `PurchaseDate` DATE NULL DEFAULT NULL,
  `SerialNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `SoldDate` DATE NULL DEFAULT NULL,
  `Status` ENUM('Empty', 'Filled', 'Junked', 'Lost', 'Reserved', 'On Hand', 'Rented', 'Sold', 'Sent', 'Maintenance', 'Transferred Out') NOT NULL DEFAULT 'Empty',
  `Warranty` VARCHAR(50) NOT NULL DEFAULT '',
  `OwnRent` ENUM('Own', 'Rent') NOT NULL DEFAULT 'Own',
  `FirstRented` DATE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `SalvageValue` DECIMAL(18,2) NULL DEFAULT NULL,
  `SalePrice` DECIMAL(18,2) NULL DEFAULT NULL,
  `ConsignmentType` VARCHAR(20) NULL DEFAULT NULL,
  `ConsignmentName` VARCHAR(50) NULL DEFAULT NULL,
  `ConsignmentDate` DATETIME NULL DEFAULT NULL,
  `VendorStockNumber` VARCHAR(20) NULL DEFAULT NULL,
  `LotNumberExpires` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `IDX_InventoryItemID_SerialNumber` (`InventoryItemID` ASC, `SerialNumber` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 42
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_serial_maintenance`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_serial_maintenance` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `SerialID` INT(11) NOT NULL,
  `AdditionalEquipment` TEXT NULL DEFAULT NULL,
  `DescriptionOfProblem` TEXT NULL DEFAULT NULL,
  `DescriptionOfWork` TEXT NULL DEFAULT NULL,
  `MaintenanceRecord` TEXT NULL DEFAULT NULL,
  `LaborHours` VARCHAR(255) NULL DEFAULT NULL,
  `Technician` VARCHAR(255) NULL DEFAULT NULL,
  `MaintenanceDue` DATE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `MaintenanceCost` DECIMAL(18,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_serial_transaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_serial_transaction` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `TypeID` INT(11) NOT NULL DEFAULT '0',
  `SerialID` INT(11) NOT NULL DEFAULT '0',
  `TransactionDatetime` DATETIME NOT NULL,
  `VendorID` INT(11) NULL DEFAULT NULL,
  `WarehouseID` INT(11) NULL DEFAULT NULL,
  `CustomerID` INT(11) NULL DEFAULT NULL,
  `OrderID` INT(11) NULL DEFAULT NULL,
  `OrderDetailsID` INT(11) NULL DEFAULT NULL,
  `LotNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 109
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_serial_transaction_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_serial_transaction_type` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 18
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_sessions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_sessions` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `UserID` SMALLINT(6) NOT NULL,
  `LoginTime` DATETIME NOT NULL,
  `LastUpdateTime` DATETIME NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_shippingmethod`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_shippingmethod` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Type` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 9
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_signaturetype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_signaturetype` (
  `Code` CHAR(1) NOT NULL DEFAULT '',
  `Description` VARCHAR(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_submitter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_submitter` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `ECSFormat` ENUM('Region A', 'Region B', 'Region C', 'Region D') NULL DEFAULT NULL,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Number` VARCHAR(16) NOT NULL DEFAULT '',
  `Password` VARCHAR(50) NOT NULL DEFAULT '',
  `Production` TINYINT(1) NOT NULL DEFAULT '0',
  `ContactName` VARCHAR(50) NOT NULL DEFAULT '',
  `Address1` VARCHAR(40) NOT NULL DEFAULT '',
  `Address2` VARCHAR(40) NOT NULL DEFAULT '',
  `City` VARCHAR(25) NOT NULL DEFAULT '',
  `State` CHAR(2) NOT NULL DEFAULT '',
  `Zip` VARCHAR(10) NOT NULL DEFAULT '',
  `Phone1` VARCHAR(50) NOT NULL DEFAULT '',
  `LastBatchNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_survey`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_survey` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(100) NOT NULL,
  `Description` VARCHAR(200) NOT NULL,
  `Template` MEDIUMTEXT NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_taxrate`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_taxrate` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `CityTax` DOUBLE NULL DEFAULT NULL,
  `CountyTax` DOUBLE NULL DEFAULT NULL,
  `Name` VARCHAR(50) NOT NULL,
  `OtherTax` DOUBLE NULL DEFAULT NULL,
  `StateTax` DOUBLE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_user` (
  `ID` SMALLINT(6) NOT NULL AUTO_INCREMENT,
  `Login` VARCHAR(16) NOT NULL,
  `Password` VARCHAR(32) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Email` VARCHAR(150) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `Login` (`Login` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_user_location`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_user_location` (
  `UserID` SMALLINT(6) NOT NULL,
  `LocationID` INT(11) NOT NULL,
  PRIMARY KEY (`UserID`, `LocationID`),
  UNIQUE INDEX `LocationID` (`LocationID` ASC, `UserID` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_user_notifications`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_user_notifications` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Type` VARCHAR(50) NOT NULL,
  `Args` VARCHAR(255) NOT NULL,
  `UserID` SMALLINT(6) NOT NULL,
  `Datetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_variables`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_variables` (
  `Name` VARCHAR(31) NOT NULL,
  `Value` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`Name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_vendor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_vendor` (
  `AccountNumber` VARCHAR(40) NOT NULL,
  `Address1` VARCHAR(40) NOT NULL,
  `Address2` VARCHAR(40) NOT NULL,
  `City` VARCHAR(25) NOT NULL,
  `Contact` VARCHAR(50) NOT NULL,
  `Fax` VARCHAR(50) NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `Phone` VARCHAR(50) NOT NULL,
  `Phone2` VARCHAR(50) NOT NULL,
  `State` VARCHAR(2) NOT NULL,
  `Zip` VARCHAR(10) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Comments` TEXT NULL DEFAULT NULL,
  `FOBDelivery` VARCHAR(50) NULL DEFAULT NULL,
  `Terms` VARCHAR(50) NULL DEFAULT NULL,
  `ShipVia` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `c01`.`tbl_warehouse`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `c01`.`tbl_warehouse` (
  `Address1` VARCHAR(40) NOT NULL DEFAULT '',
  `Address2` VARCHAR(40) NOT NULL DEFAULT '',
  `City` VARCHAR(25) NOT NULL DEFAULT '',
  `Contact` VARCHAR(50) NOT NULL DEFAULT '',
  `Fax` VARCHAR(50) NOT NULL DEFAULT '',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Phone` VARCHAR(50) NOT NULL DEFAULT '',
  `Phone2` VARCHAR(50) NOT NULL DEFAULT '',
  `State` CHAR(2) NOT NULL DEFAULT '',
  `Zip` VARCHAR(10) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;

USE `dmeworks` ;

-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_ability_eligibility_payer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_ability_eligibility_payer` (
  `Id` INT(11) NOT NULL AUTO_INCREMENT,
  `Code` VARCHAR(50) NOT NULL,
  `Name` VARCHAR(100) NOT NULL,
  `Comments` VARCHAR(100) NOT NULL,
  `SearchOptions` MEDIUMTEXT NOT NULL,
  `AllowsSubmission` TINYINT(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`Id`),
  UNIQUE INDEX `uq_ability_eligibility_payer` (`Code` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 892
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_doctor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_doctor` (
  `Address1` VARCHAR(40) NOT NULL,
  `Address2` VARCHAR(40) NOT NULL,
  `City` VARCHAR(25) NOT NULL,
  `Contact` VARCHAR(50) NOT NULL,
  `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL,
  `Fax` VARCHAR(50) NOT NULL,
  `FirstName` VARCHAR(25) NOT NULL,
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `LastName` VARCHAR(30) NOT NULL,
  `LicenseNumber` VARCHAR(16) NOT NULL,
  `LicenseExpired` DATE NULL DEFAULT NULL,
  `MedicaidNumber` VARCHAR(16) NOT NULL,
  `MiddleName` VARCHAR(1) NOT NULL,
  `OtherID` VARCHAR(16) NOT NULL,
  `FEDTaxID` VARCHAR(9) NOT NULL DEFAULT '',
  `DEANumber` VARCHAR(20) NOT NULL DEFAULT '',
  `Phone` VARCHAR(50) NOT NULL,
  `Phone2` VARCHAR(50) NOT NULL,
  `State` VARCHAR(2) NOT NULL,
  `Suffix` VARCHAR(4) NOT NULL,
  `Title` VARCHAR(50) NOT NULL,
  `TypeID` INT(11) NULL DEFAULT NULL,
  `UPINNumber` VARCHAR(11) NOT NULL,
  `Zip` VARCHAR(10) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `MIR` SET('FirstName', 'LastName', 'Address1', 'City', 'State', 'Zip', 'NPI', 'Phone') NOT NULL DEFAULT '',
  `NPI` VARCHAR(10) NULL DEFAULT NULL,
  `PecosEnrolled` TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 6713
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_doctortype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_doctortype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 741
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_icd10`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_icd10` (
  `Code` VARCHAR(8) NOT NULL,
  `Description` VARCHAR(255) NOT NULL DEFAULT '',
  `Header` TINYINT(1) NOT NULL DEFAULT '0',
  `ActiveDate` DATE NULL DEFAULT NULL,
  `InactiveDate` DATE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_icd9`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_icd9` (
  `Code` VARCHAR(6) NOT NULL DEFAULT '',
  `Description` VARCHAR(255) NOT NULL DEFAULT '',
  `ActiveDate` DATE NULL DEFAULT NULL,
  `InactiveDate` DATE NULL DEFAULT NULL,
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Code`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_insurancecompany`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_insurancecompany` (
  `Address1` VARCHAR(40) NOT NULL DEFAULT '',
  `Address2` VARCHAR(40) NOT NULL DEFAULT '',
  `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill',
  `City` VARCHAR(25) NOT NULL DEFAULT '',
  `Contact` VARCHAR(50) NOT NULL DEFAULT '',
  `ECSFormat` ENUM('Region A', 'Region B', 'Region C', 'Region D', 'Zirmed', 'Medi-Cal', 'Availity', 'Office Ally', 'Ability') NOT NULL DEFAULT 'Region A',
  `ExpectedPercent` DOUBLE NULL DEFAULT NULL,
  `Fax` VARCHAR(50) NOT NULL DEFAULT '',
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `Phone` VARCHAR(50) NOT NULL DEFAULT '',
  `Phone2` VARCHAR(50) NOT NULL DEFAULT '',
  `PriceCodeID` INT(11) NULL DEFAULT NULL,
  `PrintHAOOnInvoice` TINYINT(1) NULL DEFAULT NULL,
  `PrintInvOnInvoice` TINYINT(1) NULL DEFAULT NULL,
  `State` CHAR(2) NOT NULL DEFAULT '',
  `Title` VARCHAR(50) NOT NULL DEFAULT '',
  `Type` INT(11) NULL DEFAULT NULL,
  `Zip` VARCHAR(10) NOT NULL DEFAULT '',
  `MedicareNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `OfficeAllyNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `ZirmedNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `InvoiceFormID` INT(11) NULL DEFAULT NULL,
  `MedicaidNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `MIR` SET('MedicareNumber') NOT NULL DEFAULT '',
  `GroupID` INT(11) NULL DEFAULT NULL,
  `AvailityNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `AbilityNumber` VARCHAR(50) NOT NULL DEFAULT '',
  `AbilityEligibilityPayerId` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 2998
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_insurancecompanygroup`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_insurancecompanygroup` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  `LastUpdateUserID` SMALLINT(6) NULL DEFAULT NULL,
  `LastUpdateDatetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_insurancecompanytype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_insurancecompanytype` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_variables`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_variables` (
  `Name` VARCHAR(31) NOT NULL,
  `Value` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`Name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `dmeworks`.`tbl_zipcode`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dmeworks`.`tbl_zipcode` (
  `Zip` VARCHAR(10) NOT NULL,
  `State` VARCHAR(2) NOT NULL,
  `City` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`Zip`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;

USE `repository` ;

-- -----------------------------------------------------
-- Table `repository`.`tbl_batches`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `repository`.`tbl_batches` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `Region` VARCHAR(50) NULL DEFAULT NULL,
  `Company` VARCHAR(50) NULL DEFAULT NULL,
  `Workflow` VARCHAR(50) NULL DEFAULT NULL,
  `FileName` VARCHAR(250) NULL DEFAULT NULL,
  `Location` VARCHAR(255) NULL DEFAULT NULL,
  `FileType` VARCHAR(50) NULL DEFAULT NULL,
  `Status` VARCHAR(50) NULL DEFAULT NULL,
  `CreatedDate` DATETIME NULL DEFAULT NULL,
  `StatusDate` DATETIME NULL DEFAULT NULL,
  `Comment` TEXT NULL DEFAULT NULL,
  `Data` MEDIUMBLOB NULL DEFAULT NULL,
  `Archived` BIT(1) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `repository`.`tbl_certificates`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `repository`.`tbl_certificates` (
  `Name` VARCHAR(50) NOT NULL,
  `Description` VARCHAR(100) NULL DEFAULT NULL,
  `Data` MEDIUMBLOB NULL DEFAULT NULL,
  PRIMARY KEY (`Name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `repository`.`tbl_companies`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `repository`.`tbl_companies` (
  `Name` VARCHAR(50) NOT NULL,
  `ODBCDSN` VARCHAR(50) NULL DEFAULT NULL,
  `Server` VARCHAR(50) NULL DEFAULT NULL,
  `Port` INT(11) NULL DEFAULT NULL,
  `Database` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`Name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `repository`.`tbl_globals`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `repository`.`tbl_globals` (
  `Name` VARCHAR(50) NOT NULL,
  `Value` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`Name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `repository`.`tbl_regions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `repository`.`tbl_regions` (
  `Name` VARCHAR(50) NOT NULL,
  `ReceiverID` VARCHAR(50) NULL DEFAULT NULL,
  `ReceiverName` VARCHAR(50) NULL DEFAULT NULL,
  `ReceiverCode` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterID` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterName` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterNumber` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterContact` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterPhone` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterAddress1` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterAddress2` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterCity` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterState` VARCHAR(50) NULL DEFAULT NULL,
  `SubmitterZip` VARCHAR(50) NULL DEFAULT NULL,
  `Production` TINYINT(1) NULL DEFAULT NULL,
  `Login` VARCHAR(50) NULL DEFAULT NULL,
  `Password` VARCHAR(50) NULL DEFAULT NULL,
  `Phone` VARCHAR(250) NULL DEFAULT NULL,
  `ZipAbility` TINYINT(1) NULL DEFAULT NULL,
  `UpdateAllowable` TINYINT(1) NULL DEFAULT NULL,
  `PostZeroPay` TINYINT(1) NULL DEFAULT NULL,
  `UploadMask` VARCHAR(255) NULL DEFAULT NULL,
  `DownloadMask` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`Name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


-- -----------------------------------------------------
-- Table `repository`.`tbl_variables`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `repository`.`tbl_variables` (
  `Name` VARCHAR(31) NOT NULL,
  `Value` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`Name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1
COLLATE = latin1_general_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

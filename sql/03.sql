-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: 192.168.1.18    Database: zookeeper
-- ------------------------------------------------------
-- Server version	5.6.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `externalfile`
--

DROP TABLE IF EXISTS `externalfile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `externalfile` (
  `externalfile_id` int(11) NOT NULL AUTO_INCREMENT,
  `externalfile_projectid` int(11) NOT NULL,
  `externalfile_path` varchar(1024) NOT NULL,
  PRIMARY KEY (`externalfile_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frame`
--

DROP TABLE IF EXISTS `frame`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `frame` (
  `frame_id` int(11) NOT NULL AUTO_INCREMENT,
  `frame_projectid` int(11) NOT NULL,
  `frame_jobid` int(11) NOT NULL,
  `frame_priority` int(11) DEFAULT '50',
  `frame_package` int(11) DEFAULT '1',
  `frame_machineid` int(11) DEFAULT '-1',
  `frame_time` int(11) DEFAULT '0',
  `frame_timeend` int(11) DEFAULT NULL,
  `frame_status` enum('WAITING','PROCESSING','COMPLETED','DELIVERED','FAILED') DEFAULT 'WAITING',
  `frame_tries` int(11) DEFAULT '0',
  `frame_started` datetime DEFAULT NULL,
  `frame_ended` datetime DEFAULT NULL,
  `frame_duration` int(11) DEFAULT NULL,
  PRIMARY KEY (`frame_id`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `input`
--

DROP TABLE IF EXISTS `input`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `input` (
  `input_id` int(11) NOT NULL AUTO_INCREMENT,
  `input_path` varchar(1024) NOT NULL,
  PRIMARY KEY (`input_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `job`
--

DROP TABLE IF EXISTS `job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `job` (
  `job_id` int(11) NOT NULL AUTO_INCREMENT,
  `job_projectid` int(11) NOT NULL,
  `job_inputid` int(11) NOT NULL,
  `job_user` varchar(45) NOT NULL,
  `job_machine` int(11) NOT NULL,
  `job_type` enum('CAPTURE','FIRSTLAST','ALL') NOT NULL DEFAULT 'ALL',
  `job_name` varchar(45) NOT NULL,
  `job_priority` int(11) DEFAULT NULL,
  `job_dcc` varchar(45) NOT NULL,
  `job_dccversion` varchar(45) NOT NULL,
  `job_renderer` varchar(45) NOT NULL,
  `job_rendererversion` varchar(45) NOT NULL,
  `job_mincores` int(11) DEFAULT '0',
  `job_minramgb` int(11) DEFAULT '0',
  `job_mingpuramgb` int(11) DEFAULT '0',
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `machine`
--

DROP TABLE IF EXISTS `machine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `machine` (
  `machine_id` int(11) NOT NULL AUTO_INCREMENT,
  `machine_name` varchar(45) NOT NULL,
  `machine_level` tinyint(4) DEFAULT '3',
  `machine_ips` varchar(255) NOT NULL,
  `machine_macadresses` varchar(255) NOT NULL,
  `machine_lastseen` datetime DEFAULT NULL,
  `machine_status` enum('OFFLINE','ONLINE') DEFAULT 'OFFLINE',
  `machine_priority` enum('OFF','LOW','MED','HIGH') DEFAULT 'HIGH',
  `machine_cores` int(11) DEFAULT '0',
  `machine_ramgb` int(11) DEFAULT '0',
  `machine_gpuramgb` int(11) DEFAULT '0',
  `machine_cpuusage` int(11) DEFAULT '0',
  `machine_ramavailablemb` int(11) DEFAULT '0',
  `machine_ramusedmb` int(11) DEFAULT '0',
  PRIMARY KEY (`machine_id`),
  UNIQUE KEY `machine_name_UNIQUE` (`machine_name`),
  UNIQUE KEY `machine_id_UNIQUE` (`machine_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification` (
  `notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `notification_machineid` int(11) NOT NULL,
  `notification_frameid` int(11) DEFAULT '-1',
  `notification_severity` enum('LOG','WARNING','ERROR') NOT NULL DEFAULT 'ERROR',
  `notification_text` text NOT NULL,
  `notification_status` enum('NEW','DISMISSED') DEFAULT 'NEW',
  PRIMARY KEY (`notification_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `output`
--

DROP TABLE IF EXISTS `output`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `output` (
  `output_id` int(11) NOT NULL AUTO_INCREMENT,
  `output_projectid` int(11) NOT NULL,
  `output_jobid` int(11) NOT NULL,
  `output_frameid` int(11) NOT NULL,
  `output_name` varchar(45) NOT NULL,
  `output_path` varchar(1024) NOT NULL,
  PRIMARY KEY (`output_id`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project` (
  `project_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(45) NOT NULL,
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uncmap`
--

DROP TABLE IF EXISTS `uncmap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uncmap` (
  `uncmap_id` int(11) NOT NULL AUTO_INCREMENT,
  `uncmap_machineid` int(11) NOT NULL,
  `uncmap_drive` varchar(3) NOT NULL,
  `uncmap_uncpath` varchar(96) NOT NULL,
  `uncmap_created` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`uncmap_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `validunc`
--

DROP TABLE IF EXISTS `validunc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `validunc` (
  `validunc_id` int(11) NOT NULL AUTO_INCREMENT,
  `validunc_path` varchar(96) NOT NULL,
  PRIMARY KEY (`validunc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'zookeeper'
--
/*!50003 DROP PROCEDURE IF EXISTS `look_for_work` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `look_for_work`(IN my_machine_id INT(11), IN max_results INT(11))
BEGIN
  SELECT frame.frame_id from frame, job, machine
  WHERE 
    machine.machine_id = my_machine_id and 
    frame.frame_jobid = job.job_id and 
    frame.frame_status = 'WAITING' and 
    job.job_mincores <= machine.machine_cores and 
    job.job_minramgb <= machine.machine_ramgb and 
    job.job_mingpuramgb <= machine.machine_gpuramgb
  ORDER BY job.job_priority DESC, 
    frame.frame_priority DESC, 
    frame.frame_package ASC,
    job.job_id ASC,
    frame.frame_time ASC
  LIMIT max_results;


END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-12  1:54:54

-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: 192.168.1.10    Database: zookeeper
-- ------------------------------------------------------
-- Server version 5.7.9-log

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
  `externalfile_type` varchar(128) NOT NULL,
  `externalfile_userpath` varchar(2048) NOT NULL,
  `externalfile_resolvedpath` varchar(2048) NOT NULL,
  `externalfile_resolution` int(11) DEFAULT '-1',
  `externalfile_start` int(11) DEFAULT '1',
  `externalfile_end` int(11) DEFAULT '1',
  `externalfile_padding` int(11) DEFAULT '5',
  PRIMARY KEY (`externalfile_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
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
  `frame_machineid` int(11) DEFAULT '1',
  `frame_time` int(11) DEFAULT '0',
  `frame_timeend` int(11) DEFAULT NULL,
  `frame_status` enum('STOPPED','WAITING','PROCESSING','COMPLETED','DELIVERED','FAILED') DEFAULT 'WAITING',
  `frame_tries` int(11) DEFAULT '0',
  `frame_started` datetime DEFAULT NULL,
  `frame_ended` datetime DEFAULT NULL,
  `frame_duration` int(11) DEFAULT NULL,
  `frame_log` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`frame_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
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
  `job_type` enum('DELETED','CAPTURE','FIRSTLAST','ALL') NOT NULL DEFAULT 'ALL',
  `job_name` varchar(1024) NOT NULL,
  `job_priority` int(11) DEFAULT '50',
  `job_dcc` varchar(45) NOT NULL,
  `job_dccversion` varchar(45) NOT NULL,
  `job_renderer` varchar(45) NOT NULL,
  `job_rendererversion` varchar(45) NOT NULL,
  `job_mincores` int(11) DEFAULT '0',
  `job_minramgb` int(11) DEFAULT '0',
  `job_mingpuramgb` int(11) DEFAULT '0',
  `job_overwriteoutputs` int(11) DEFAULT '0',
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
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
  `machine_frameid` int(11) DEFAULT '-1',
  `machine_ips` varchar(255) NOT NULL,
  `machine_macadresses` varchar(255) NOT NULL,
  `machine_lastseen` datetime DEFAULT NULL,
  `machine_status` enum('OFFLINE','ONLINE') DEFAULT 'OFFLINE',
  `machine_priority` enum('OFF','LOW','MED','HIGH') DEFAULT 'MED',
  `machine_cores` int(11) DEFAULT '0',
  `machine_ramgb` int(11) DEFAULT '0',
  `machine_gpuramgb` int(11) DEFAULT '0',
  `machine_cpuusage` int(11) DEFAULT '0',
  `machine_ramavailablemb` int(11) DEFAULT '0',
  `machine_ramusedmb` int(11) DEFAULT '0',
  `machine_installeddccs` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`machine_id`),
  UNIQUE KEY `machine_name_UNIQUE` (`machine_name`),
  UNIQUE KEY `machine_id_UNIQUE` (`machine_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machine`
--

LOCK TABLES `machine` WRITE;
/*!40000 ALTER TABLE `machine` DISABLE KEYS */;
INSERT INTO `machine` VALUES (1,'none',1,-1,' ',' ',NULL,'OFFLINE','MED',0,0,0,0,0,0,NULL);
/*!40000 ALTER TABLE `machine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `machinegroup`
--

DROP TABLE IF EXISTS `machinegroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `machinegroup` (
  `machinegroup_id` int(11) NOT NULL AUTO_INCREMENT,
  `machinegroup_name` varchar(255) NOT NULL,
  PRIMARY KEY (`machinegroup_id`),
  UNIQUE KEY `machinegroup_name_UNIQUE` (`machinegroup_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machinegroup`
--

LOCK TABLES `machinegroup` WRITE;
/*!40000 ALTER TABLE `machinegroup` DISABLE KEYS */;
INSERT INTO `machinegroup` VALUES (1,'all');
/*!40000 ALTER TABLE `machinegroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `membership`
--

DROP TABLE IF EXISTS `membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `membership` (
  `membership_id` int(11) NOT NULL AUTO_INCREMENT,
  `membership_machine` int(11) NOT NULL,
  `membership_machinegroup` int(11) NOT NULL,
  PRIMARY KEY (`membership_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membership`
--

LOCK TABLES `membership` WRITE;
/*!40000 ALTER TABLE `membership` DISABLE KEYS */;
INSERT INTO `membership` VALUES (1,1,1);
/*!40000 ALTER TABLE `membership` ENABLE KEYS */;
UNLOCK TABLES;

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
  `output_status` enum('PENDING','DELIVERED') DEFAULT 'PENDING',
  `output_name` varchar(45) NOT NULL,
  `output_path` varchar(1024) NOT NULL,
  PRIMARY KEY (`output_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
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
  `project_type` enum('DELETED','NORMAL') NOT NULL DEFAULT 'NORMAL',
  `project_machinegroup` int(11) NOT NULL DEFAULT '1',
  `project_localizefiles` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`project_id`),
  UNIQUE KEY `project_name_UNIQUE` (`project_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `setting`
--

DROP TABLE IF EXISTS `setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `setting` (
  `setting_id` int(11) NOT NULL AUTO_INCREMENT,
  `setting_name` varchar(45) NOT NULL,
  `setting_value` varchar(1024) NOT NULL,
  PRIMARY KEY (`setting_id`),
  UNIQUE KEY `setting_name_UNIQUE` (`setting_name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setting`
--

LOCK TABLES `setting` WRITE;
/*!40000 ALTER TABLE `setting` DISABLE KEYS */;
INSERT INTO `setting` VALUES (1,'log_root','\\\\domain\\public\\zookeeper\\logs'),(2,'softimage_workgroup_root','\\\\domain\\public\\zookeeper\\workgroups'),(3,'render_user','render'),(5,'render_password','render123');
/*!40000 ALTER TABLE `setting` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

--
-- Dumping routines for database 'zookeeper'
--
/*!50003 DROP PROCEDURE IF EXISTS `cleanup_frame_on_machine_start` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `cleanup_frame_on_machine_start`(in target INT(11))
BEGIN
  UPDATE
    frame
  SET
    frame.frame_status = 'WAITING',
        frame.frame_machineid = 1
  WHERE
    frame.frame_status = 'PROCESSING' and
        frame.frame_machineid = target;
  COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `delete_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `delete_group`(in g INT(11))
BEGIN
  UPDATE 
    project
  SET
    project_machinegroup = 1
  WHERE 
    project_machinegroup = g;
  DELETE FROM 
    membership
  WHERE
    membership_machinegroup = g;
  DELETE FROM
    machinegroup
  WHERE 
    machinegroup_id = g AND machinegroup_id != 1;
  COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `delete_job` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `delete_job`(in target INT(11))
BEGIN
  DELETE FROM 
    output
  WHERE
    output_jobid = target;
        
  DELETE FROM
    frame
  WHERE
    frame_jobid = target;
        
  DELETE FROM
    input
  USING 
    input, job
  WHERE
    job_id = target AND
    input_id = job_inputid;
        
  UPDATE
    job
  SET
    job_type = 'DELETED'
  WHERE
    job_id = target;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `delete_project` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `delete_project`(in target INT(11))
BEGIN
  DELETE FROM 
    output
  WHERE
    output_projectid = target;
        
  DELETE FROM
    frame
  WHERE
    frame_projectid = target;
        
  DELETE FROM
    input
  USING 
    input, job
  WHERE
    job_projectid = target AND
    input_id = job_inputid;
        
  UPDATE
    job
  SET
    job_type = 'DELETED'
  WHERE
    job_projectid = target;

  UPDATE
    project
  SET
    project_type = 'DELETED'
  WHERE
    project_id = target;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_frames_for_manager` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_frames_for_manager`(in currentjob INT(11))
BEGIN
  SELECT 
    frame_id, 
        job_name, 
        frame_time, 
        frame_status, 
        frame_duration, 
        machine_name, 
        frame_priority, 
        frame_package 
  FROM 
    frame, 
        job, 
        machine 
  WHERE 
    job_id = currentjob AND 
        frame_jobid = job_id AND 
        frame_machineid = machine_id 
  ORDER BY frame_time ASC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_frame_range_for_job` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_frame_range_for_job`(in target INT(11))
BEGIN
  SELECT
    MIN(frame_time),
        MAX(frame_time)
  FROM
    frame
  WHERE
    frame_jobid = target;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_groups_for_manager` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_groups_for_manager`()
BEGIN
  SELECT DISTINCT
    machinegroup_id, 
        machinegroup_name,
        (
      SELECT GROUP_CONCAT(machine_name SEPARATOR ',')
      FROM
        machine,
                membership
      WHERE
        membership_machine = machine_id AND
        membership_machinegroup = machinegroup_id
      ORDER BY
        machine_name ASC
    )
  FROM
    machinegroup
  ORDER BY
    machinegroup_name ASC;
    
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_jobs_for_manager` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_jobs_for_manager`()
BEGIN
  SELECT 
    job_id, 
        project_name,
        job_name, 
        job_user, 
        (
      SELECT 
        COUNT(frame_id) 
      FROM 
        frame 
      WHERE 
        frame_jobid = job_id
    ), 
        job_priority, 
        (
      SELECT 
        COUNT(frame_id) 
      FROM 
        frame 
      WHERE 
        frame_jobid = job_id AND 
                frame_status = 'PROCESSING'
    ), 
        ROUND(
      100.0 * 
            (
        SELECT 
          COUNT(frame_id) 
        FROM 
          frame 
        WHERE 
          frame_jobid = job_id AND 
                    (
            frame_status = 'COMPLETED' or 
                        frame_status = 'DELIVERED'
          )
      ) / 
            (
        SELECT 
          COUNT(frame_id) 
        FROM 
          frame 
        WHERE 
          frame_jobid = job_id
      )
    ),
    (
      SELECT
        (
          SUM(timediff(frame_ended, frame_started)) DIV
          COUNT(frame_id)
        )
      FROM
        frame
      WHERE
        frame_jobid = job_id AND
        frame_status = 'DELIVERED'
    ) *
    (
      SELECT
        COUNT(frame_id)
      FROM
        frame
      WHERE
        frame_jobid = job_id AND
        frame_status != 'DELIVERED'
    ),
    (
      SELECT
        (
          SUM(timediff(frame_ended, frame_started))
        )
      FROM
        frame
      WHERE
        frame_jobid = job_id AND
        frame_status = 'DELIVERED'
    )
  FROM 
    job,
        project
  WHERE
    job_type != 'DELETED' AND
        job_projectid = project_id
  ORDER BY 
    job_id ASC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_jobs_to_cleanup` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_jobs_to_cleanup`()
BEGIN
  SELECT 
    job_id
  FROM
    job
  WHERE
    job_type = 'DELETED';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_machines_for_manager` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_machines_for_manager`()
BEGIN
  SELECT 
    machine_id, 
        machine_name, 
        (
      SELECT GROUP_CONCAT(
        machinegroup_name SEPARATOR ',')
      FROM
        machinegroup,
                membership
      WHERE
        membership_machine = machine_id AND
        membership_machinegroup = machinegroup_id
      ORDER BY
        machinegroup_name ASC
    ),        
        machine_status, 
        machine_priority, 
        machine_cpuusage, 
        ROUND(100.0 * (machine_ramusedmb / (machine_ramgb * 1024))) 
  FROM 
    machine 
  WHERE 
    machine_id > 1 
  ORDER BY 
    machine_name ASC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_outputs_per_frame` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_outputs_per_frame`(in target INT(11))
BEGIN
  SELECT 
    output_id,
    output_name 
  FROM 
    output 
  WHERE 
    output_frameid = target
  ORDER BY
    output_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_outputs_per_job` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_outputs_per_job`(in target INT(11))
BEGIN
  SELECT
    DISTINCT(output_name)
  FROM
    output
  WHERE output_jobid = target;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_projects_for_manager` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_projects_for_manager`()
BEGIN
  SELECT
    project_id,
        project_name,
        (
      SELECT 
        COUNT(job_id) 
      FROM 
        job
      WHERE 
        job_projectid = project_id AND
                job_type != 'DELETED'
    ),
        machinegroup_name,
        project_localizefiles
  FROM
    project, machinegroup
  WHERE
    project_type != 'DELETED' AND
        project_machinegroup = machinegroup_id
  ORDER BY
    project_name ASC;
    
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_projects_to_cleanup` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `get_projects_to_cleanup`()
BEGIN
  SELECT 
    project_id
  FROM
    project
  WHERE
    project_type = 'DELETED';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `groups_for_machine` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `groups_for_machine`(in m INT(11))
BEGIN
  SELECT DISTINCT
    machinegroup_name
  FROM
    machinegroup, membership
  WHERE
    (
      membership_machinegroup = machinegroup_id AND
            membership_machine = m
    )
        OR
    machinegroup_id = 1
  ORDER BY
    machinegroup_name ASC;
        
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `look_for_outputs_to_deliver` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `look_for_outputs_to_deliver`(in target INT(11))
BEGIN
  SELECT 
    output_id
  FROM
    frame, output
  WHERE
    frame_machineid = target AND
        output_frameid = frame_id AND
        output_status = 'PENDING';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `look_for_work` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `look_for_work`(IN my_machine_id INT(11), IN max_results INT(11))
BEGIN
  SELECT DISTINCT frame.frame_id from frame, job, project, machine, membership
  WHERE 
    machine.machine_id = my_machine_id and 
    frame.frame_jobid = job.job_id and 
    frame.frame_projectid = project.project_id and
    frame.frame_status = 'WAITING' and 
    frame.frame_machineid != my_machine_id and # don't do the same frame twice on the same machine
    (
    (
      membership_machinegroup = project.project_machinegroup and
      membership_machine = my_machine_id
    ) or
        project.project_machinegroup = 1 # all machines group
  ) and
    job.job_mincores <= machine.machine_cores and 
    job.job_minramgb <= machine.machine_ramgb and 
    job.job_mingpuramgb <= machine.machine_gpuramgb and
    FIND_IN_SET(CONCAT(job.job_dcc, ' ', job.job_dccversion), machine.machine_installeddccs) > 0
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
/*!50003 DROP PROCEDURE IF EXISTS `machines_for_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `machines_for_group`(in g INT(11))
BEGIN
  SELECT DISTINCT
    machine_name
  FROM
    machine, membership, machinegroup
  WHERE
    (
      membership_machinegroup = g AND
            membership_machine = machine_id
    )
        OR
        (
      machinegroup_id = g AND
            g = 1
    )
  ORDER BY
    machine_name ASC;
        
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `resubmit_frame` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `resubmit_frame`(in target INT(11))
BEGIN
  DELETE FROM 
    output
  USING
    output, frame, machine
  WHERE
    output_frameid = target AND
        output_frameid = frame_id AND
        (
      frame_status != 'PROCESSING' OR
            frame_machineid != (SELECT machine_frameid FROM machine WHERE machine_id = frame_machineid LIMIT 1)
    );
  UPDATE 
    frame 
  SET 
    frame_status='WAITING', 
        frame_machineid = 1 
  WHERE 
    frame_id = target AND 
        (
      frame_status != 'PROCESSING' OR
            frame_machineid != (SELECT machine_frameid FROM machine WHERE machine_id = frame_machineid LIMIT 1)
    );
            
  COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `resubmit_job` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `resubmit_job`(in target INT(11))
BEGIN
  DELETE FROM
    output
  USING
    output, frame
  WHERE
    output_jobid = frame_jobid AND
        output_jobid = target AND
        frame_status != "PROCESSING";
  UPDATE 
    frame 
  SET 
    frame_status='WAITING', 
        frame_machineid = 1 
  WHERE 
    frame_jobid = target AND
        frame_status != 'PROCESSING';
  COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `resume_frame` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `resume_frame`(in target INT(11))
BEGIN
  UPDATE 
    frame 
  SET 
    frame_status='WAITING' 
  WHERE 
    frame_id = target AND 
        frame_status = 'STOPPED';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `resume_job` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `resume_job`(in target INT(11))
BEGIN
  UPDATE 
    frame 
  SET 
    frame_status='WAITING' 
  WHERE 
    frame_jobid = target AND 
        frame_status = 'STOPPED';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `set_frame_failed` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `set_frame_failed`(in target INT(11))
BEGIN
  UPDATE 
    frame 
  SET 
    frame.frame_status = IF(frame.frame_tries < 2, 'WAITING', 'FAILED'), 
        frame.frame_tries = frame.frame_tries + 1,
        frame.frame_ended = NOW()
  WHERE frame.frame_id = target;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `set_frame_processing` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `set_frame_processing`(in target INT(11), in targetMachine INT(11))
BEGIN
  UPDATE 
    frame
  SET
    frame.frame_status = 'PROCESSING',
        frame.frame_started = NOW(),
        frame.frame_ended = NOW(),
        frame.frame_machineid = targetMachine
  WHERE
    frame.frame_id = target;
  UPDATE
    machine
  SET
    machine.machine_frameid = target
  WHERE
    machine.machine_id = targetMachine;
  COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `set_machine_priority` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `set_machine_priority`(in target INT(11), in priority VARCHAR(45))
BEGIN
  UPDATE
    machine
  SET
    machine_priority = priority
  WHERE
    machine_id = target;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `stop_frame` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `stop_frame`(in target INT(11))
BEGIN
  UPDATE 
    frame 
  SET 
    frame_status='STOPPED' 
  WHERE 
    frame_id = target AND 
        frame_status = 'WAITING';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `stop_job` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `stop_job`(in target INT(11))
BEGIN
  UPDATE 
    frame 
  SET 
    frame_status='STOPPED' 
  WHERE 
    frame_jobid = target AND 
        frame_status = 'WAITING';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `truncate_complete_db` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mysql`@`%` PROCEDURE `truncate_complete_db`()
BEGIN
  TRUNCATE externalfile;
  TRUNCATE frame;
  TRUNCATE input;
  TRUNCATE job;
  TRUNCATE notification;
  TRUNCATE output;
  TRUNCATE project;
  TRUNCATE uncmap;
  DELETE FROM machine WHERE machine_id > 1; 
  ALTER TABLE machine AUTO_INCREMENT = 2;
  DELETE FROM machinegroup WHERE machinegroup_id > 1;
  ALTER TABLE machinegroup AUTO_INCREMENT = 2;
  DELETE FROM membership WHERE membership_id > 1;
  ALTER TABLE membership AUTO_INCREMENT = 2;
  COMMIT;
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

-- Dump completed on 2016-02-27 16:56:33

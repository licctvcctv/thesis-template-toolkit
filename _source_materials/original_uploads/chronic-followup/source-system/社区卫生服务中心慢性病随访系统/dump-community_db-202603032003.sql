-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: community_db
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(100) NOT NULL COMMENT '科室名称',
  `code` varchar(50) DEFAULT NULL COMMENT '科室编码',
  `description` varchar(500) DEFAULT NULL COMMENT '科室描述',
  `status` tinyint DEFAULT '1' COMMENT '状态：1-启用，0-禁用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='科室表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'内科','NK','内科科室',1,'2026-03-01 18:33:05','2026-03-01 18:33:05'),(2,'外科','WK','外科科室',1,'2026-03-01 18:33:05','2026-03-01 18:33:05'),(4,'妇科','FK','妇科科室',1,'2026-03-01 18:33:05','2026-03-01 18:33:05');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctor`
--

DROP TABLE IF EXISTS `doctor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `employee_id` varchar(50) DEFAULT NULL COMMENT '工号',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `department` varchar(100) DEFAULT NULL COMMENT '科室',
  `title` varchar(50) DEFAULT NULL COMMENT '职称',
  `specialty` varchar(200) DEFAULT NULL COMMENT '专业特长',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `doctor_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='医生表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor`
--

LOCK TABLES `doctor` WRITE;
/*!40000 ALTER TABLE `doctor` DISABLE KEYS */;
INSERT INTO `doctor` VALUES (1,2,'Y001','','','内科','主任','','2026-03-01 18:38:50','2026-03-01 18:38:50'),(2,3,'Y002','','','外科','副主任','','2026-03-01 20:59:19','2026-03-01 20:59:19');
/*!40000 ALTER TABLE `doctor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctor_assignment`
--

DROP TABLE IF EXISTS `doctor_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor_assignment` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `patient_id` bigint NOT NULL COMMENT '患者ID',
  `doctor_id` bigint NOT NULL COMMENT '医生ID',
  `assign_date` date NOT NULL COMMENT '分配日期',
  `assigner_id` bigint DEFAULT NULL COMMENT '分配人ID',
  `status` tinyint DEFAULT '1' COMMENT '状态：1-当前分配，0-历史分配',
  `remarks` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `assigner_id` (`assigner_id`),
  CONSTRAINT `doctor_assignment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  CONSTRAINT `doctor_assignment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`) ON DELETE CASCADE,
  CONSTRAINT `doctor_assignment_ibfk_3` FOREIGN KEY (`assigner_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='医生分配记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor_assignment`
--

LOCK TABLES `doctor_assignment` WRITE;
/*!40000 ALTER TABLE `doctor_assignment` DISABLE KEYS */;
INSERT INTO `doctor_assignment` VALUES (1,2,1,'2026-03-01',1,1,'','2026-03-01 18:55:56');
/*!40000 ALTER TABLE `doctor_assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `followup_record`
--

DROP TABLE IF EXISTS `followup_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `followup_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` bigint DEFAULT NULL COMMENT '任务ID',
  `patient_id` bigint NOT NULL COMMENT '患者ID',
  `doctor_id` bigint NOT NULL COMMENT '医生ID',
  `followup_date` date NOT NULL COMMENT '随访日期',
  `followup_type` varchar(50) DEFAULT NULL COMMENT '随访类型',
  `symptoms` text COMMENT '症状描述',
  `blood_pressure` varchar(50) DEFAULT NULL COMMENT '血压',
  `blood_sugar` varchar(50) DEFAULT NULL COMMENT '血糖',
  `weight` decimal(5,2) DEFAULT NULL COMMENT '体重',
  `medication_compliance` varchar(50) DEFAULT NULL COMMENT '用药依从性',
  `adverse_reactions` text COMMENT '不良反应',
  `lifestyle_guidance` text COMMENT '生活方式指导',
  `next_followup_date` date DEFAULT NULL COMMENT '下次随访日期',
  `followup_result` text COMMENT '随访结果',
  `remarks` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `followup_record_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `followup_task` (`id`) ON DELETE SET NULL,
  CONSTRAINT `followup_record_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  CONSTRAINT `followup_record_ibfk_3` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='随访记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `followup_record`
--

LOCK TABLES `followup_record` WRITE;
/*!40000 ALTER TABLE `followup_record` DISABLE KEYS */;
INSERT INTO `followup_record` VALUES (2,1,2,1,'2026-03-01','医院随访','111','120/80','5.5',60.00,'','','',NULL,'111','','2026-03-01 21:33:07','2026-03-01 21:33:07');
/*!40000 ALTER TABLE `followup_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `followup_record_medicine`
--

DROP TABLE IF EXISTS `followup_record_medicine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `followup_record_medicine` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `followup_record_id` bigint NOT NULL COMMENT '随访记录ID',
  `medicine_id` bigint NOT NULL COMMENT '药品ID',
  `quantity` int NOT NULL COMMENT '数量',
  `dosage` varchar(255) DEFAULT NULL COMMENT '用法用量',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `followup_record_id` (`followup_record_id`),
  KEY `medicine_id` (`medicine_id`),
  CONSTRAINT `followup_record_medicine_ibfk_1` FOREIGN KEY (`followup_record_id`) REFERENCES `followup_record` (`id`) ON DELETE CASCADE,
  CONSTRAINT `followup_record_medicine_ibfk_2` FOREIGN KEY (`medicine_id`) REFERENCES `medicine` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='随访记录药品关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `followup_record_medicine`
--

LOCK TABLES `followup_record_medicine` WRITE;
/*!40000 ALTER TABLE `followup_record_medicine` DISABLE KEYS */;
INSERT INTO `followup_record_medicine` VALUES (1,2,1,3,'111','2026-03-01 21:33:07','2026-03-01 21:33:07');
/*!40000 ALTER TABLE `followup_record_medicine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `followup_task`
--

DROP TABLE IF EXISTS `followup_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `followup_task` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_no` varchar(50) NOT NULL COMMENT '任务编号',
  `patient_id` bigint NOT NULL COMMENT '患者ID',
  `doctor_id` bigint NOT NULL COMMENT '负责医生ID',
  `task_type` varchar(50) DEFAULT NULL COMMENT '任务类型',
  `task_content` text COMMENT '任务内容',
  `plan_date` date NOT NULL COMMENT '计划随访日期',
  `actual_date` date DEFAULT NULL COMMENT '实际随访日期',
  `status` varchar(20) DEFAULT 'pending' COMMENT '状态：pending-待办，in_progress-进行中，completed-已完成，cancelled-已取消',
  `priority` varchar(20) DEFAULT 'normal' COMMENT '优先级：low-低，normal-正常，high-高',
  `creator_id` bigint DEFAULT NULL COMMENT '创建人ID',
  `assign_date` date DEFAULT NULL COMMENT '分配日期',
  `remarks` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_no` (`task_no`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `followup_task_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  CONSTRAINT `followup_task_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`) ON DELETE CASCADE,
  CONSTRAINT `followup_task_ibfk_3` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='随访任务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `followup_task`
--

LOCK TABLES `followup_task` WRITE;
/*!40000 ALTER TABLE `followup_task` DISABLE KEYS */;
INSERT INTO `followup_task` VALUES (1,'FT1772369988797',2,1,'测试','测试','2026-03-02','2026-03-01','completed','normal',1,'2026-03-01','','2026-03-01 20:59:48','2026-03-01 21:33:07'),(2,'FT1772466240649',2,1,'','1111','2026-03-03',NULL,'in_progress','normal',1,'2026-03-02','','2026-03-02 23:44:00','2026-03-02 23:44:48');
/*!40000 ALTER TABLE `followup_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_record`
--

DROP TABLE IF EXISTS `medical_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `patient_id` bigint NOT NULL COMMENT '患者ID',
  `doctor_id` bigint NOT NULL COMMENT '医生ID',
  `record_date` date NOT NULL COMMENT '诊疗日期',
  `chief_complaint` varchar(500) DEFAULT NULL COMMENT '主诉',
  `present_illness` text COMMENT '现病史',
  `physical_examination` text COMMENT '体格检查',
  `diagnosis` varchar(500) DEFAULT NULL COMMENT '诊断',
  `treatment_plan` text COMMENT '治疗方案',
  `medication` text COMMENT '用药情况',
  `remarks` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `medical_record_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  CONSTRAINT `medical_record_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='诊疗记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_record`
--

LOCK TABLES `medical_record` WRITE;
/*!40000 ALTER TABLE `medical_record` DISABLE KEYS */;
INSERT INTO `medical_record` VALUES (1,2,1,'2026-03-01','1','1','1','1','1','','','2026-03-01 19:10:45','2026-03-01 19:10:45');
/*!40000 ALTER TABLE `medical_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_record_medicine`
--

DROP TABLE IF EXISTS `medical_record_medicine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_record_medicine` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `medical_record_id` bigint NOT NULL COMMENT '诊疗记录ID',
  `medicine_id` bigint NOT NULL COMMENT '药品ID',
  `quantity` int NOT NULL COMMENT '数量',
  `dosage` varchar(100) DEFAULT NULL COMMENT '用法用量',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `medical_record_id` (`medical_record_id`),
  KEY `medicine_id` (`medicine_id`),
  CONSTRAINT `medical_record_medicine_ibfk_1` FOREIGN KEY (`medical_record_id`) REFERENCES `medical_record` (`id`) ON DELETE CASCADE,
  CONSTRAINT `medical_record_medicine_ibfk_2` FOREIGN KEY (`medicine_id`) REFERENCES `medicine` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='诊疗记录药品关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_record_medicine`
--

LOCK TABLES `medical_record_medicine` WRITE;
/*!40000 ALTER TABLE `medical_record_medicine` DISABLE KEYS */;
INSERT INTO `medical_record_medicine` VALUES (1,1,1,2,'111','2026-03-01 19:10:45'),(2,1,2,1,'222','2026-03-01 19:10:45');
/*!40000 ALTER TABLE `medical_record_medicine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicine`
--

DROP TABLE IF EXISTS `medicine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicine` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `medicine_code` varchar(50) NOT NULL COMMENT '药品编码',
  `medicine_name` varchar(100) NOT NULL COMMENT '药品名称',
  `specification` varchar(100) DEFAULT NULL COMMENT '规格',
  `unit` varchar(20) DEFAULT NULL COMMENT '单位',
  `manufacturer` varchar(200) DEFAULT NULL COMMENT '生产厂家',
  `price` decimal(10,2) DEFAULT NULL COMMENT '价格',
  `stock` int DEFAULT '0' COMMENT '库存数量',
  `description` varchar(500) DEFAULT NULL COMMENT '药品描述',
  `status` tinyint DEFAULT '1' COMMENT '状态：1-启用，0-停用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `medicine_code` (`medicine_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='药品表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicine`
--

LOCK TABLES `medicine` WRITE;
/*!40000 ALTER TABLE `medicine` DISABLE KEYS */;
INSERT INTO `medicine` VALUES (1,'M001','阿司匹林肠溶片','100mg*30片','盒','北京制药厂',15.50,100,'用于预防心脑血管疾病',1,'2026-03-01 19:00:32','2026-03-01 19:00:32'),(2,'M002','硝苯地平缓释片','30mg*30片','盒','上海制药有限公司',28.00,80,'用于治疗高血压',1,'2026-03-01 19:00:32','2026-03-01 19:00:32'),(3,'M003','二甲双胍片','0.5g*30片','盒','广州制药集团',12.80,120,'用于治疗2型糖尿病',1,'2026-03-01 19:00:32','2026-03-01 19:00:32');
/*!40000 ALTER TABLE `medicine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient`
--

DROP TABLE IF EXISTS `patient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `patient_no` varchar(50) NOT NULL COMMENT '患者编号',
  `name` varchar(50) NOT NULL COMMENT '姓名',
  `gender` tinyint DEFAULT NULL COMMENT '性别：1-男，2-女',
  `birthday` date DEFAULT NULL COMMENT '出生日期',
  `id_card` varchar(18) DEFAULT NULL COMMENT '身份证号',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `address` varchar(200) DEFAULT NULL COMMENT '地址',
  `disease_type` varchar(100) DEFAULT NULL COMMENT '疾病类型',
  `diagnosis_date` date DEFAULT NULL COMMENT '确诊日期',
  `current_doctor_id` bigint DEFAULT NULL COMMENT '当前负责医生ID',
  `risk_level` varchar(20) DEFAULT 'low' COMMENT '风险等级：low-低风险，medium-中风险，high-高风险',
  `status` tinyint DEFAULT '1' COMMENT '状态：1-正常，0-停用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `patient_no` (`patient_no`),
  KEY `current_doctor_id` (`current_doctor_id`),
  CONSTRAINT `patient_ibfk_1` FOREIGN KEY (`current_doctor_id`) REFERENCES `doctor` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='患者表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (2,'P202603015CE8AA40','孙哲',1,'2000-03-05','11010120000305341X','','xxx','1111\n2222',NULL,1,'low',1,'2026-03-01 18:55:16','2026-03-03 19:56:29'),(3,'P20260301B4D91BAE','李腾',NULL,'2000-03-05','110101200003051916','13122189811','xxx','',NULL,2,'low',1,'2026-03-01 21:09:17','2026-03-01 21:09:17');
/*!40000 ALTER TABLE `patient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_vital_signs`
--

DROP TABLE IF EXISTS `patient_vital_signs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient_vital_signs` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `patient_id` bigint NOT NULL COMMENT '患者ID',
  `record_date` datetime NOT NULL COMMENT '录入时间',
  `blood_pressure_systolic` int DEFAULT NULL COMMENT '收缩压',
  `blood_pressure_diastolic` int DEFAULT NULL COMMENT '舒张压',
  `blood_sugar` decimal(5,2) DEFAULT NULL COMMENT '血糖值',
  `blood_sugar_type` varchar(20) DEFAULT NULL COMMENT '血糖类型：fasting-空腹，postprandial-餐后，random-随机',
  `remarks` varchar(255) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `patient_vital_signs_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='患者生命体征数据表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_vital_signs`
--

LOCK TABLES `patient_vital_signs` WRITE;
/*!40000 ALTER TABLE `patient_vital_signs` DISABLE KEYS */;
INSERT INTO `patient_vital_signs` VALUES (1,3,'2026-02-01 14:00:41',120,80,5.50,'fasting','','2026-03-01 22:04:01','2026-03-01 22:04:01'),(2,3,'2026-02-02 22:31:40',100,95,8.50,'fasting','','2026-03-01 22:32:02','2026-03-01 22:32:02');
/*!40000 ALTER TABLE `patient_vital_signs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `risk_assessment`
--

DROP TABLE IF EXISTS `risk_assessment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `risk_assessment` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `patient_id` bigint NOT NULL COMMENT '患者ID',
  `risk_level` varchar(20) NOT NULL COMMENT '风险等级：low-低风险，medium-中风险，high-高风险',
  `assessment_date` date NOT NULL COMMENT '评估日期',
  `assessor_id` bigint DEFAULT NULL COMMENT '评估人ID',
  `assessment_result` text COMMENT '评估结果',
  `remarks` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `assessor_id` (`assessor_id`),
  CONSTRAINT `risk_assessment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  CONSTRAINT `risk_assessment_ibfk_2` FOREIGN KEY (`assessor_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='风险等级评估记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `risk_assessment`
--

LOCK TABLES `risk_assessment` WRITE;
/*!40000 ALTER TABLE `risk_assessment` DISABLE KEYS */;
INSERT INTO `risk_assessment` VALUES (1,2,'low','2026-03-01',1,'暂无问题','','2026-03-01 18:55:40');
/*!40000 ALTER TABLE `risk_assessment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `risk_level_config`
--

DROP TABLE IF EXISTS `risk_level_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `risk_level_config` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `level_code` varchar(20) NOT NULL COMMENT '等级代码：low、medium、high',
  `level_name` varchar(50) NOT NULL COMMENT '等级名称',
  `description` varchar(500) DEFAULT NULL COMMENT '描述',
  `sort_order` int DEFAULT '0' COMMENT '排序',
  `status` tinyint DEFAULT '1' COMMENT '状态：1-启用，0-禁用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `level_code` (`level_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='风险等级配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `risk_level_config`
--

LOCK TABLES `risk_level_config` WRITE;
/*!40000 ALTER TABLE `risk_level_config` DISABLE KEYS */;
INSERT INTO `risk_level_config` VALUES (1,'low','低风险','病情稳定，风险较低',1,1,'2026-03-01 18:44:49','2026-03-01 18:44:49'),(2,'medium','中风险','病情需要关注，风险中等',2,1,'2026-03-01 18:44:49','2026-03-01 18:44:49'),(3,'high','高风险','病情严重，需要重点关注',3,1,'2026-03-01 18:44:49','2026-03-01 18:44:49');
/*!40000 ALTER TABLE `risk_level_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(100) NOT NULL COMMENT '密码',
  `name` varchar(50) NOT NULL COMMENT '姓名',
  `role` varchar(20) NOT NULL COMMENT '角色：admin-管理员，doctor-医生',
  `status` tinyint DEFAULT '1' COMMENT '状态：1-启用，0-禁用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','123456','系统管理员','admin',1,'2026-03-01 18:07:59','2026-03-01 18:07:59'),(2,'Y001','123456','张扬','doctor',1,'2026-03-01 18:38:50','2026-03-01 18:38:50'),(3,'Y002','123456','王莽','doctor',1,'2026-03-01 20:59:19','2026-03-01 20:59:19');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'community_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-03 20:03:25

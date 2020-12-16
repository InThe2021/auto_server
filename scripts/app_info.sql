CREATE TABLE `app_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sn` int(11) DEFAULT NULL COMMENT '序号',
  `hostname` varchar(50) NOT NULL COMMENT '服务器名',
  `ip` varchar(50) NOT NULL COMMENT '服务器IP',
  `port` int(11) DEFAULT NULL COMMENT '应用程序端口',
  `application` varchar(200) DEFAULT NULL COMMENT '应用程序名',
  `cmds` varchar(200) DEFAULT NULL COMMENT '执行命令',
  `project` varchar(200) DEFAULT NULL COMMENT '项目名称',
  `status` int(4) DEFAULT NULL COMMENT '应用状态值#1在线#0离线',
  `http_code` int(20) DEFAULT NULL COMMENT 'http状态码',
  `last_scan_err_time` datetime DEFAULT NULL COMMENT '自动重启脚本最后扫描到异常时间',
  `before_scan_err_time` datetime DEFAULT NULL COMMENT '自动重启脚本上一次扫描到异常时间',
  `last_startup_time` varchar(200) DEFAULT NULL COMMENT '最后一次重启时间',
  `startup_times` int(11) NOT NULL COMMENT '启动耗时',
  `before_startup_time` varchar(200) DEFAULT NULL COMMENT '上一次重启时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=146 DEFAULT CHARSET=utf8 COMMENT='应用程序信息';
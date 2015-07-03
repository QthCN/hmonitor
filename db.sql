DROP DATABASE IF EXISTS hmonitor;
CREATE DATABASE hmonitor;
USE hmonitor;
CREATE TABLE USERS (
  id       INT           NOT NULL AUTO_INCREMENT,
  name     VARCHAR(128)  NOT NULL UNIQUE,
  mail     VARCHAR(128)  NOT NULL UNIQUE,
  phone    VARCHAR(128)  NOT NULL UNIQUE,
  password VARCHAR(1024) NOT NULL,
  PRIMARY KEY (id),
  KEY (name)
);
CREATE TABLE USERS_TRIGGER_BINDING (
  id           INT          NOT NULL AUTO_INCREMENT,
  user_id      INT          NOT NULL,
  trigger_name VARCHAR(256) NOT NULL,
  PRIMARY KEY (id),
  KEY (user_id),
  KEY (trigger_name)
);
CREATE TABLE TRIGGER_EVENTS (
  id               INT          NOT NULL AUTO_INCREMENT,
  trigger_name     VARCHAR(256) NOT NULL,
  hostname         VARCHAR(256) NOT NULL,
  event            VARCHAR(256) NOT NULL,
  value            VARCHAR(256) NOT NULL,
  type             VARCHAR(128) NOT NULL DEFAULT 'NORMAL',
  last_occur_time  TIMESTAMP    NOT NULL,
  first_occur_time TIMESTAMP    NOT NULL,
  severity         VARCHAR(256) NOT NULL,
  occur_amount     INT          NOT NULL,
  status           VARCHAR(128) NOT NULL,
  PRIMARY KEY (id),
  KEY (trigger_name),
  KEY (last_occur_time),
  KEY (first_occur_time),
  KEY (status),
  KEY (severity)
);
CREATE TABLE ALERT_MSG (
  id           INT          NOT NULL AUTO_INCREMENT,
  mail         VARCHAR(128),
  phone        VARCHAR(128),
  trigger_name VARCHAR(256) NOT NULL,
  hostname     VARCHAR(256) NOT NULL,
  send_time    TIMESTAMP    NOT NULL,
  PRIMARY KEY (id),
  KEY (send_time),
  KEY (trigger_name)
);
CREATE TABLE AUTOFIX_BINDING (
  id              INT          NOT NULL AUTO_INCREMENT,
  trigger_name    VARCHAR(256) NOT NULL,
  auto_fix_script VARCHAR(256) NOT NULL,
  change_user     VARCHAR(256) NOT NULL,
  change_date     TIMESTAMP    NOT NULL,
  PRIMARY KEY (id),
  KEY (trigger_name)
);
CREATE TABLE AUTOFIX_LOG (
  id           INT           NOT NULL AUTO_INCREMENT,
  trigger_name VARCHAR(256)  NOT NULL,
  hostname     VARCHAR(256)  NOT NULL,
  script       VARCHAR(256)  NOT NULL,
  begin_time   TIMESTAMP     NOT NULL,
  status       VARCHAR(256)  NOT NULL,
  event_id     INT           NOT NULL,
  comments     VARCHAR(4096) NOT NULL DEFAULT "",
  PRIMARY KEY (id),
  KEY (trigger_name),
  KEY (hostname),
  KEY (begin_time),
  KEY (status)
);
CREATE TABLE ALERT_FILTER (
  id           INT           NOT NULL AUTO_INCREMENT,
  trigger_name VARCHAR(256)  NOT NULL,
  hostname     VARCHAR(256)  NOT NULL,
  begin_time   TIMESTAMP     NOT NULL,
  end_time     TIMESTAMP     NOT NULL,
  filter       VARCHAR(256)  NOT NULL,
  comment      VARCHAR(4096) NOT NULL,
  PRIMARY KEY (id),
  KEY (trigger_name),
  KEY (hostname)
);
CREATE TABLE HM_TRIGGER (
  id          INT           NOT NULL AUTO_INCREMENT,
  description VARCHAR(256)  NOT NULL,
  priority    INT           NOT NULL,
  comments    VARCHAR(4096) NOT NULL DEFAULT "",
  PRIMARY KEY (id),
  KEY (description)
);

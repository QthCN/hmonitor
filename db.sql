drop database if exists hmonitor;
create database hmonitor;
use hmonitor;
create table USERS(id int not null AUTO_INCREMENT, name varchar(128) not null unique, mail varchar(128) not null unique, phone varchar(128) not null unique, password varchar(1024) not null, primary key (id), key(name));
create table USERS_TRIGGER_BINDING(id int not null AUTO_INCREMENT, user_id int not null, trigger_name varchar(256) not null, primary key(id), key(user_id), key(trigger_name));
create table TRIGGER_EVENTS(id int not null AUTO_INCREMENT, trigger_name varchar(256) not null, hostname varchar(256) not null, event varchar(256) not null, value varchar(256) not null, last_occur_time timestamp not null, first_occur_time timestamp not null, occur_amount int not null, status varchar(128) not null, primary key (id), key(trigger_name), key(last_occur_time), key(first_occur_time), key(status));


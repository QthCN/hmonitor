drop database if exists hmonitor;
create database hmonitor;
use hmonitor;
create table USERS(id int not null AUTO_INCREMENT, name varchar(128) not null unique, mail varchar(128) not null unique, phone varchar(128) not null unique, password varchar(1024) not null, primary key (id), key(name));
create table USERS_TRIGGER_BINDING(id int not null AUTO_INCREMENT, user_id int not null, trigger_id int not null, primary key(id), key(user_id), key(trigger_id));


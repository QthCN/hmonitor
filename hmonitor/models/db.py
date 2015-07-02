# -*- coding: utf-8 -*-

import logging

import torndb

import hmonitor.common.constants as constants


class DB(object):

    def __init__(self, mysql_user, mysql_passwd,
                 mysql_host, mysql_database):
        self.mysql_user = mysql_user
        self.mysql_passwd = mysql_passwd
        self.mysql_host = mysql_host
        self.mysql_database = mysql_database

    def __enter__(self):
        try:
            db = torndb.Connection(host=self.mysql_host,
                                   database=self.mysql_database,
                                   user=self.mysql_user,
                                   password=self.mysql_passwd)
            self.db = db
        except Exception as e:
            logging.exception(e)
        finally:
            return db

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.db.close()
        except Exception as e:
            pass


class HMonitorDB(object):

    def __init__(self, mysql_user, mysql_passwd,
                 mysql_host, mysql_database):
        self.db_dict = dict(mysql_user=mysql_user,
                            mysql_passwd=mysql_passwd,
                            mysql_host=mysql_host,
                            mysql_database=mysql_database)

    def get_users(self):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM USERS")
            return users

    def get_user_by_id(self, id):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM USERS WHERE ID={0}".format(id))
            return users[0] if len(users) > 0 else {}

    def get_user_name_by_id(self, id):
        user = self.get_user_by_id(id)
        return user.get("name", None)

    def get_user_mail_by_id(self, id):
        user = self.get_user_by_id(id)
        return user.get("mail", None)

    def get_user_phone_by_id(self, id):
        user = self.get_user_by_id(id)
        return user.get("phone", None)

    def get_user_by_name(self, name):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM USERS WHERE NAME='{0}'".format(
                name
            ))
            return users[0] if len(users) > 0 else {}

    def get_user_by_mail(self, mail):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM USERS WHERE MAIL='{0}'".format(
                mail
            ))
            return users[0] if len(users) > 0 else {}

    def get_user_by_phone(self, phone):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM USERS WHERE PHONE='{0}'".format(
                phone
            ))
            return users[0] if len(users) > 0 else {}

    def check_password_by_mail(self, mail, passwd):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM USERS WHERE MAIL='{mail}' "
                             "AND PASSWORD=PASSWORD('{passwd}')".format(
                mail=mail,
                passwd=passwd
            ))
            return len(users) > 0

    def check_password_by_name(self, name, passwd):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM USERS WHERE NAME='{name}' "
                             "AND PASSWORD=PASSWORD('{passwd}')".format(
                name=name,
                passwd=passwd
            ))
            return len(users) > 0

    def update_password(self, name, passwd):
        with DB(**self.db_dict) as db:
            db.execute("UPDATE USERS SET PASSWORD=PASSWORD('{p}') "
                       "WHERE NAME='{n}'".format(p=passwd, n=name))

    def create_user(self, name, mail, phone, passwd):
        with DB(**self.db_dict) as db:
            db.execute("INSERT INTO USERS (name, mail, phone, password) "
                       "VALUES('{name}', '{mail}', '{phone}', "
                       "PASSWORD('{passwd}'))".format(name=name,
                                                      mail=mail,
                                                      phone=phone,
                                                      passwd=passwd))

    def get_triggers_name_by_user_id(self, id):
        with DB(**self.db_dict) as db:
            triggers_name = db.query("SELECT * FROM "
                                     "USERS_TRIGGER_BINDING WHERE "
                                     "USER_ID={0}".format(id))
            return [t.trigger_name for t in triggers_name]

    def get_users_id_by_trigger_name(self, trigger_name):
        with DB(**self.db_dict) as db:
            users = db.query("SELECT * FROM "
                             "USERS_TRIGGER_BINDING WHERE "
                             "TRIGGER_NAME='{0}'".format(trigger_name))
            return [u.user_id for u in users]

    def bind_triggers_with_user_id(self, user_id, trigger_name):
        triggers_name = self.get_triggers_name_by_user_id(user_id)
        if trigger_name in triggers_name:
            return

        with DB(**self.db_dict) as db:
            db.execute("INSERT INTO USERS_TRIGGER_BINDING "
                       "(USER_ID, TRIGGER_NAME) VALUES "
                       "({user_id}, '{trigger_name}')".format(
                user_id=user_id,
                trigger_name=trigger_name
            ))

    def unbind_triggers_with_user_id(self, user_id, trigger_name):
        with DB(**self.db_dict) as db:
            db.execute("DELETE FROM USERS_TRIGGER_BINDING WHERE "
                       "USER_ID={user_id} and "
                       "TRIGGER_NAME='{trigger_name}'".format(
                user_id=user_id,
                trigger_name=trigger_name
            ))

    def record_trigger_event(self, trigger_name, hostname, event,
                             value, severity):
        with DB(**self.db_dict) as db:
            db._db.autocommit(False)

            events = db.query("SELECT * FROM TRIGGER_EVENTS "
                              "WHERE TRIGGER_NAME='{trigger_name}' "
                              "AND HOSTNAME='{hostname}' "
                              "AND STATUS='{status}' FOR UPDATE".format(
                trigger_name=trigger_name,
                hostname=hostname,
                status=constants.TRIGGER_EVENT_STATUS["new"]
            ))

            if len(events) == 0:
                db.execute("INSERT INTO TRIGGER_EVENTS (TRIGGER_NAME, "
                           "HOSTNAME, EVENT, VALUE, FIRST_OCCUR_TIME, "
                           "SEVERITY, "
                           "LAST_OCCUR_TIME, OCCUR_AMOUNT, STATUS) VALUES "
                           "('{trigger_name}', '{hostname}', '{event}', "
                           "'{value}', NOW(), '{severity}', NOW(), 1, "
                           "'{status}')".format(
                    trigger_name=trigger_name,
                    hostname=hostname,
                    event=event,
                    value=value,
                    severity=severity,
                    status=constants.TRIGGER_EVENT_STATUS["new"]
                ))

            else:
                db.execute("UPDATE TRIGGER_EVENTS SET "
                           "LAST_OCCUR_TIME=NOW(), VALUE='{value}', "
                           "OCCUR_AMOUNT=OCCUR_AMOUNT+1 "
                           "WHERE TRIGGER_NAME='{trigger_name}' "
                           "AND STATUS='{status}' "
                           "AND HOSTNAME='{hostname}'".format(
                    value=value,
                    trigger_name=trigger_name,
                    status=constants.TRIGGER_EVENT_STATUS["new"],
                    hostname=hostname
                ))

            db._db.commit()

    def expire_trigger_events(self, expire_time=5):
        with DB(**self.db_dict) as db:
            db._db.autocommit(False)

            events = db.query("SELECT * FROM TRIGGER_EVENTS "
                              "WHERE STATUS='{status}' "
                              "AND DATE_SUB(NOW(), INTERVAL {t} MINUTE) > "
                              "LAST_OCCUR_TIME FOR UPDATE".format(
                status=constants.TRIGGER_EVENT_STATUS["new"],
                t=expire_time
            ))

            for event in events:
                event_id = event.get("id", -1)
                db.execute("UPDATE TRIGGER_EVENTS SET STATUS='{status}' "
                           "WHERE ID={event_id}".format(
                    status=constants.TRIGGER_EVENT_STATUS["expired"],
                    event_id=event_id
                ))

            db._db.commit()

    def expire_trigger_event(self, event_id):
        with DB(**self.db_dict) as db:
            db.execute("UPDATE TRIGGER_EVENTS SET STATUS='{status}' "
                       "WHERE ID={event_id}".format(
                status=constants.TRIGGER_EVENT_STATUS["expired"],
                event_id=event_id
            ))

    def get_trigger_events_in_problem(self):
        with DB(**self.db_dict) as db:
            events = db.query("SELECT * FROM TRIGGER_EVENTS "
                              "WHERE STATUS='{status}'".format(
                status=constants.TRIGGER_EVENT_STATUS["new"],
            ))
            return events

    def record_alert_msg(self, trigger_name, hostname,
                         mail=None, phone=None):
        if mail is None and phone is None:
            logging.error("MAIL AND PHONE ARE NONE.")
            return
        with DB(**self.db_dict) as db:
            if mail is not None:
                sql = ("INSERT INTO ALERT_MSG(MAIL, TRIGGER_NAME, HOSTNAME, "
                       "SEND_TIME) VALUES('{mail}', '{trigger_name}', "
                       "'{hostname}', NOW())".format(mail=mail,
                                                     trigger_name=trigger_name,
                                                     hostname=hostname))
            else:
                sql = ("INSERT INTO ALERT_MSG(PHONE, TRIGGER_NAME, HOSTNAME, "
                       "SEND_TIME) VALUES('{phone}', '{trigger_name}', "
                       "'{hostname}', NOW())".format(phone=phone,
                                                     trigger_name=trigger_name,
                                                     hostname=hostname))
            db.execute(sql)

    def get_last_7_days_alert_msgs(self, mail=None, phone=None):
        with DB(**self.db_dict) as db:
            msg = db.query("SELECT * FROM ALERT_MSG WHERE "
                           "DATE_SUB(NOW(), INTERVAL 7 DAY) < SEND_TIME "
                           "AND (MAIL='{mail}' OR PHONE='{phone}')".format(
                mail = mail or "NOTEXISTMAIL",
                phone = phone or "NOTEXISTPHONE"
            ))
            return msg

    def get_last_30_days_alert_msgs(self, mail=None, phone=None):
        with DB(**self.db_dict) as db:
            msg = db.query("SELECT * FROM ALERT_MSG WHERE "
                           "DATE_SUB(NOW(), INTERVAL 30 DAY) < SEND_TIME "
                           "AND (MAIL='{mail}' OR PHONE='{phone}')".format(
                mail = mail or "NOTEXISTMAIL",
                phone = phone or "NOTEXISTPHONE"
            ))
            return msg

    def get_autofix_bindings(self):
        with DB(**self.db_dict) as db:
            bindings = db.query("SELECT * FROM AUTOFIX_BINDING")
            return bindings

    def bind_autofix(self, trigger_name, username, script):
        with DB(**self.db_dict) as db:
            db._db.autocommit(False)

            binding = db.query("SELECT * FROM AUTOFIX_BINDING "
                               "WHERE TRIGGER_NAME='{t}' FOR UPDATE".format(
                t=trigger_name
            ))
            if len(binding) == 0:
                sql = ("INSERT INTO AUTOFIX_BINDING "
                       "(TRIGGER_NAME, AUTO_FIX_SCRIPT, CHANGE_USER, "
                       "CHANGE_DATE) VALUES ('{t}', '{s}', "
                       "'{u}', NOW())".format(t=trigger_name, s=script,
                                              u=username))
            else:
                sql = ("UPDATE AUTOFIX_BINDING SET AUTO_FIX_SCRIPT='{s}', "
                       "CHANGE_USER='{u}', CHANGE_DATE=NOW() WHERE "
                       "TRIGGER_NAME='{t}'".format(s=script,
                                                   u=username,
                                                   t=trigger_name))
            db.execute(sql)

            db._db.commit()

    def unbind_autofix(self, trigger_name):
        with DB(**self.db_dict) as db:
            db.execute("DELETE FROM AUTOFIX_BINDING WHERE "
                       "TRIGGER_NAME ='{t}'".format(t=trigger_name))

    def get_autofix_logs(self, trigger_name, hostname, last_minutes=30):
        with DB(**self.db_dict) as db:
            logs = db.query("SELECT * FROM AUTOFIX_LOG "
                            "WHERE TRIGGER_NAME='{t}' AND HOSTNAME='{h}' "
                            "AND DATE_SUB(NOW(), INTERVAL {ti} MINUTE) < "
                            "BEGIN_TIME ORDER BY BEGIN_TIME ASC".format(
                t=trigger_name,
                h=hostname,
                ti=last_minutes
            ))
            return logs

    def get_all_autofix_logs(self, last_day=7):
        with DB(**self.db_dict) as db:
            logs = db.query("SELECT * FROM AUTOFIX_LOG "
                            "WHERE DATE_SUB(NOW(), INTERVAL {t} DAY) < "
                            "BEGIN_TIME ORDER BY BEGIN_TIME DESC "
                            "".format(t=last_day))
            return logs

    def create_autofix_log(self, trigger_name, hostname, script, event_id):
        with DB(**self.db_dict) as db:
            db._db.autocommit(False)

            logs = db.query("SELECT * FROM AUTOFIX_LOG "
                            "WHERE TRIGGER_NAME='{t}' AND HOSTNAME='{h}' "
                            "AND DATE_SUB(NOW(), INTERVAL 10 MINUTE) < "
                            "BEGIN_TIME AND STATUS='{s}' FOR UPDATE".format(
                t=trigger_name,
                h=hostname,
                s=constants.AUTOFIX_STATUS["fixing"]
            ))

            if len(logs) > 0:
                db._db.commit()
                return None

            db.execute("INSERT INTO AUTOFIX_LOG (TRIGGER_NAME, HOSTNAME, "
                       "SCRIPT, BEGIN_TIME, STATUS, EVENT_ID) VALUES ( "
                       "'{t}', '{h}', '{s}', NOW(), '{st}', {e})".format(
                t=trigger_name,
                h=hostname,
                s=script,
                st=constants.AUTOFIX_STATUS["fixing"],
                e=event_id
            ))

            # TODO(tianhuan) can we get this id in another way?
            logs = db.query("SELECT * FROM AUTOFIX_LOG "
                            "WHERE TRIGGER_NAME='{t}' AND HOSTNAME='{h}' "
                            "AND DATE_SUB(NOW(), INTERVAL 1 MINUTE) < "
                            "BEGIN_TIME AND STATUS='{s}' FOR UPDATE".format(
                t=trigger_name,
                h=hostname,
                s=constants.AUTOFIX_STATUS["fixing"]
            ))

            db._db.commit()
            return logs[-1]["id"]

    def update_autofix_log(self, log_id, status, comments):
        comments.replace("\"", "'")
        with DB(**self.db_dict) as db:
            db.execute("UPDATE AUTOFIX_LOG SET STATUS='{s}', "
                       "COMMENTS=\"{c}\" WHERE ID={i}".format(
                s=status,
                c=comments,
                i=log_id
            ))

    def create_alert_filter(self, trigger_name, hostname, filter, begin_time,
                            end_time, comment):
        comment.replace("\"", "'")
        with DB(**self.db_dict) as db:
            db._db.autocommit(False)
            f = db.query("SELECT * FROM ALERT_FILTER WHERE "
                         "TRIGGER_NAME='{t}' AND UPPER(HOSTNAME)=UPPER('{h}') "
                         "AND END_TIME > NOW() FOR UPDATE".format(
                t=trigger_name,
                h=hostname
            ))
            if len(f) == 0:
                db.execute("INSERT INTO ALERT_FILTER(TRIGGER_NAME, HOSTNAME, "
                           "FILTER, BEGIN_TIME, END_TIME, COMMENT) VALUES "
                           "('{t}', '{h}', '{f}', '{bd}', '{ed}', '{c}' "
                           ")".format(t=trigger_name,
                                      h=hostname,
                                      f=filter,
                                      bd=begin_time,
                                      ed=end_time,
                                      c=comment))
            else:
                db.execute("UPDATE ALERT_FILTER SET BEGIN_TIME='{bd}', "
                           "END_TIME='{ed}', FILTER='{f}', COMMENT='{c}' "
                           "WHERE TRIGGER_NAME='{t}' AND "
                           "UPPER(HOSTNAME)=UPPER('{h}') "
                           "".format(bd=begin_time,
                                     ed=end_time,
                                     f=filter,
                                     c=comment,
                                     t=trigger_name,
                                     h=hostname))
            db._db.commit()

    def cancel_alert_filter(self, trigger_name, hostname):
        with DB(**self.db_dict) as db:
            db.execute("DELETE FROM ALERT_FILTER WHERE "
                       "TRIGGER_NAME='{t}' AND "
                       "UPPER(HOSTNAME)=UPPER('{h}')".format(
                t=trigger_name,
                h=hostname
            ))

    def get_active_alert_filters(self):
        with DB(**self.db_dict) as db:
            filters = db.query("SELECT * FROM ALERT_FILTER WHERE "
                               "END_TIME > NOW()")
            return filters


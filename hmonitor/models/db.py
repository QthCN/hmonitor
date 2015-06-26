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

    def bind_triggers_with_user_id(self, user_id, trigger_name):
        triggers_name = self.get_triggers_name_by_user_id(user_id)
        if trigger_name in triggers_name:
            return

        with DB(**self.db_dict) as db:
            db.execute("INSERT INTO USERS_TRIGGER_BINDING "
                       "(USER_ID, TRIGGER_NAME) VALUES "
                       "({user_id}, {trigger_name})".format(
                user_id=user_id,
                trigger_name=trigger_name
            ))

    def unbind_triggers_with_user_id(self, user_id, trigger_name):
        with DB(**self.db_dict) as db:
            db.execute("DELETE FROM USERS_TRIGGER_BINDING WHERE "
                       "USER_ID={user_id} and "
                       "TRIGGER_NAME={trigger_name}".format(
                user_id=user_id,
                trigger_name=trigger_name
            ))

    def record_trigger_event(self, trigger_name, hostname, event, value):
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
                           "LAST_OCCUR_TIME, OCCUR_AMOUNT, STATUS) VALUES "
                           "('{trigger_name}', '{hostname}', '{event}', "
                           "'{value}', NOW(), NOW(), 1, '{status}')".format(
                    trigger_name=trigger_name,
                    hostname=hostname,
                    event=event,
                    value=value,
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

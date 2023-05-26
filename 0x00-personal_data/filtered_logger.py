#!/usr/bin/env python3
'''Implementing the Logging facility for Python'''


import logging
from typings import List


def filter_datum(
                fields: List[str],
                redaction: str,
                message: str,
                separator: str
                ) -> str:
    '''
    Args:
        fields - a list of strings representing all fields to obfuscate
        redaction - string representing by what the field will be obfuscated
        message - a string representing the log line
        separator - a string representing by which character
                is separating all fields in the log line (message)

    Returns: the log message obfuscated
    '''
    for f in fields:
        logMessage = re.sub(f'{f}=.*?{separator}',
                            f'{f}={redaction}{separator}', message)
    return logMessage


def get_logger() -> logging.Logger:
    """
    Returns a Logger object for handling Personal Data

    Returns:
        A Logger object with INFO log level and RedactingFormatter
        formatter for filtering PII fields
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Returns a MySQLConnection object for accessing Personal Data database

    Returns:
        A MySQLConnection object using connection details from
        environment variables
    """
    username = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = environ.get("PERSONAL_DATA_DB_NAME")

    cnx = mysql.connector.connection.MySQLConnection(user=username,
                                                     password=password,
                                                     host=host,
                                                     database=db_name)
    return cnx


def main():
    """
    Main function to retrieve user data from database and log to console
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    field_names = [i[0] for i in cursor.description]

    logger = get_logger()

    for row in cursor:
        str_row = ''.join(f'{f}={str(r)}; ' for r, f in zip(row, field_names))
        logger.info(str_row.strip())

    cursor.close()
    db.close()


class RedactingFormatter(logging.Formatter):
    """
    Redacting Formatter class for filtering PII fields
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """
        Constructor method for RedactingFormatter class

        Args:
            fields: list of fields to redact in log messages
        """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the specified log record as text.

        Filters values in incoming log records using filter_datum.
        """
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return super(RedactingFormatter, self).format(record)


if __name__ == '__main__':
    main()

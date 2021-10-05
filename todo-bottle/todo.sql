PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: status
DROP TABLE IF EXISTS status;

CREATE TABLE status (
    id          TEXT PRIMARY KEY
                     CONSTRAINT [status id may not be empty] CHECK (LENGTH(id) > 0),
    description TEXT NOT NULL
                     CONSTRAINT [status description may not be empty] CHECK (LENGTH(description) > 0) 
)
WITHOUT ROWID;

INSERT INTO status (
                       id,
                       description
                   )
                   VALUES (
                       'C',
                       'Closed'
                   );

INSERT INTO status (
                       id,
                       description
                   )
                   VALUES (
                       'O',
                       'Open'
                   );


-- Table: task
DROP TABLE IF EXISTS task;

CREATE TABLE task (
    id          INTEGER   PRIMARY KEY AUTOINCREMENT,
    summary     TEXT      CONSTRAINT [summary may not be empty] CHECK (LENGTH(summary) > 0) 
                          NOT NULL,
    description TEXT,
    duedate     DATE      NOT NULL
                          DEFAULT (DATE('now', 'localtime') ),
    status_id   TEXT      NOT NULL
                          REFERENCES status (id) 
                          DEFAULT O,
    modified    TIMESTAMP DEFAULT (DATETIME('now', 'localtime') ) 
);

INSERT INTO task (
                     id,
                     summary,
                     description,
                     duedate,
                     status_id,
                     modified
                 )
                 VALUES (
                     1,
                     'Read',
                     'Read something to get a good introduction into Python',
                     '2020-01-01',
                     'C',
                     '2017-09-18 09:10:20'
                 );

INSERT INTO task (
                     id,
                     summary,
                     description,
                     duedate,
                     status_id,
                     modified
                 )
                 VALUES (
                     2,
                     'Visit',
                     'Visit the python.org website',
                     '2015-03-27',
                     'C',
                     '2017-09-17 17:58:28'
                 );


-- Trigger: update modified
DROP TRIGGER IF EXISTS "update modified";
CREATE TRIGGER [update modified]
         AFTER UPDATE
            ON task
      FOR EACH ROW
          WHEN NEW.modified = OLD.modified
BEGIN
    UPDATE task
       SET modified = DATETIME('now', 'localtime') 
     WHERE id = OLD.id;
END;


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
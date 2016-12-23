/*
This file creates the tables in the database.
Tables (formatted "<table name>: <field1>, <field2>, etc."):
Posts: time, word, id
*/

create table Posts (time timestamp not null default current_timestamp primary key, word varchar(64) not null, id varchar(31) not null unique);

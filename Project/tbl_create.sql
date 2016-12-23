/*
This file creates the tables in the database.
Tables (formatted "<table name>: <field1>, <field2>, etc."):
Posts: time, id, word
*/

create table Posts (time int not null primary key, id varchar(31) not null, word varchar(64) not null, constraint unique_id unique (id));

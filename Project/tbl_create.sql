/*
This file creates the tables in the database.
Tables (formatted "<table name>: <field1>, <field2>, etc."):
Posts: time, id, word
*/

create table Posts (time int not null, id varchar(31), word varchar(64), primary key(id));

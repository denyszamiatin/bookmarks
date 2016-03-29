create table user (
    id int primary key auto_increment,
    login varchar(20) unique,
    email varchar(200),
    passwd varchar(128)
);

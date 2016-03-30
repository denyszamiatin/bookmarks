create table user (
    id int primary key auto_increment,
    login varchar(20) unique,
    email varchar(200),
    passwd varchar(128)
);
create table link (
    id int primary key auto_increment,
    user int,
    title varchar(100),
    descr varchar(255),
    link varchar(255),
    count int default 0
);
create table link_hashes (
    user int,
    link int,
    hash int
);